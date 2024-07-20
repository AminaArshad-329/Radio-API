import datetime
import os
import random
import tempfile

from django.conf import settings
from django.core.files import File
from django.http import HttpResponse, JsonResponse, FileResponse
from pydub import AudioSegment
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.views import APIView
from google.cloud import storage
from rest_framework_simplejwt.authentication import JWTAuthentication

from news_generation.generate_news_script import get_news_script, generate_bulletin, speak_elevenlabs, \
    get_elevenlab_voices
from .serializers import NewsGenerationSerializer, AudioGenerationSerializer, ExportPlaylistSerializer


class GenerateAIStoryView(APIView):
    # authentication_classes = (JWTAuthentication,)
    # permission_classes = (IsAuthenticated,)

    def post(self, request, *args, **kwargs):
        serializer = NewsGenerationSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        data = serializer.validated_data

        stories = data.get('stories', 0) + 1
        voice = data.get('voice', '')
        newsbed = data.get('newsbed', '')
        separator = data.get('separator', '')

        news = int(request.POST.get('news', 0))
        entertainment = int(request.POST.get('entertainment', 0))
        sports = int(request.POST.get('sports', 0))
        weather = int(request.POST.get('weather', 0))

        concatenated_audio = AudioSegment.empty()

        prompts = [
            'Get World News'
            'Get Entertainment News',
            'Get Sports News',
            'Get Health News',
            'What is the weather like in Paris in Farenheit?',
        ]
        news = []

        for i in range(stories):
            news.append(get_news_script(prompts[i]))

        bulletin = generate_bulletin(','.join(news))

        if not separator:
            with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as tmpFile:
                speak_elevenlabs(bulletin, tmpFile.name, voice)
                audio = AudioSegment.from_file(tmpFile.name)
                concatenated_audio += audio

        else:
            beep_sound = AudioSegment.from_file(settings.MEDIA_ROOT + '/audios/' + 'beep.mp3')

            for n in news:
                with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as tmpFile:
                    speak_elevenlabs(n, tmpFile.name, voice)
                    audio = AudioSegment.from_file(tmpFile.name)
                    concatenated_audio += beep_sound
                    concatenated_audio += audio

        if newsbed:
            backgroundMusic = AudioSegment.from_file(settings.MEDIA_ROOT + '/audios/' + "newsbed.mp3")
            # Reduce the volume by 30dB
            backgroundMusic = backgroundMusic - 30

            # Loop and extend the background music to match the duration of the concatenated audio
            backgroundMusic = backgroundMusic * (len(concatenated_audio) // len(backgroundMusic) + 1)
            backgroundMusic = backgroundMusic[:len(concatenated_audio)]

            backgroundMusic = backgroundMusic.fade_out(2000)
            finalAudio = concatenated_audio.overlay(backgroundMusic)
        else:
            finalAudio = concatenated_audio

        final_audio_path = os.path.join(settings.MEDIA_ROOT + "/audios", "generated_audio.wav")
        finalAudio.export(final_audio_path, format="wav")

        with open(final_audio_path, "rb") as audio_file:
            response = HttpResponse(File(audio_file), content_type="audio/wav")

        response["Content-Disposition"] = 'attachment; filename="generated_audio.wav"'
        return response


class GenerateStoryFromInputView(APIView):
    # authentication_classes = (JWTAuthentication,)
    # permission_classes = (IsAuthenticated,)

    def post(self, request, *args, **kwargs):
        serializer = AudioGenerationSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        data = serializer.validated_data

        voice = data.get('voice', '')
        script = data.get('script', '')

        audio = AudioSegment.empty()

        with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as tmpFile:
            speak_elevenlabs(script, tmpFile.name, voice)
            output = AudioSegment.from_file(tmpFile.name)
            audio += output

        try:
            final_audio_path = os.path.join(settings.MEDIA_ROOT + "/audios", f"{script}.wav")
            audio.export(final_audio_path, format="wav")

        except Exception:
            final_audio_path = os.path.join(settings.MEDIA_ROOT + "/audios", f"{datetime.datetime.now()}_{random.randint(0,1000)}.wav")
            audio.export(final_audio_path, format="wav")

        # with open(final_audio_path, "rb") as audio_file:
        response = FileResponse(open(final_audio_path, 'rb'), content_type="audio/wav")

        response["Content-Disposition"] = 'attachment; filename="generated_audio.wav"'
        return response


class ExportPlaylistView(APIView):
    # authentication_classes = (JWTAuthentication,)
    # permission_classes = (IsAuthenticated,)

    def post(self, request, *args, **kwargs):
        serializer = ExportPlaylistSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        data = serializer.validated_data
        newsbed = data.get('newsbed', False)
        separator = data.get('separator', False)
        files = data.get('files', [])

        final_audio = AudioSegment.empty()

        for file in files:
            audio = AudioSegment.from_file(file)

            if separator:
                beep_sound = AudioSegment.from_file(settings.MEDIA_ROOT + '/audios/' + 'beep.mp3')
                final_audio += beep_sound
                final_audio += audio

            else:
                final_audio += audio

        if newsbed:
            bg_music = AudioSegment.from_file(settings.MEDIA_ROOT + '/audios/' + 'newsbed.mp3')
            bg_music = bg_music - 30

            bg_music = bg_music * (len(final_audio) // len(bg_music) + 1)
            bg_music = bg_music[:len(final_audio)]

            bg_music = bg_music.fade_out(2000)
            final_audio = final_audio.overlay(bg_music)

        final_audio_path = os.path.join(settings.MEDIA_ROOT + "/audios", "playlist.wav")
        final_audio.export(final_audio_path, format="wav")

        client = storage.Client(credentials=settings.GS_CREDENTIALS)
        bucket = client.bucket('viveca_static')
        blob = bucket.blob("generated_audio.wav")
        blob.upload_from_filename(final_audio_path)

        audio_url = 'https://storage.googleapis.com/viveca_static/generated_audio.wav'

        return HttpResponse(audio_url)


class VoicesView(APIView):
    # authentication_classes = (JWTAuthentication,)
    # permission_classes = (IsAuthenticated,)

    def get(self, request, *args, **kwargs):
        voices = get_elevenlab_voices()
        return JsonResponse({"voices": voices}, status=status.HTTP_200_OK)
