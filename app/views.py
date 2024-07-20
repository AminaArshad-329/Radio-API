import os
import pandas as pd

from django.conf import settings
from django.http import JsonResponse, StreamingHttpResponse
from rest_framework.views import APIView
from rest_framework.parsers import MultiPartParser, FormParser
from rest_framework.response import Response
from rest_framework import status, serializers
from drf_yasg.utils import swagger_auto_schema
from langchain_community.vectorstores import FAISS
from langchain_openai import OpenAIEmbeddings
from tempfile import NamedTemporaryFile
from .analysis import Analysis
from .models import TemporaryTable
from .dailylogs import generate_daily_logs
from .generator import build_documents, build_playlist
from .spotify import get_similar_songs, write_to_csv


analytics = Analysis()
tempTable = TemporaryTable
OPENAI_KEY = getattr(settings, "OPENAI_KEY")

example_file = "app/data/example.csv"
dest_playlist = "app/data/playlist.csv"
spotify = "app/data/spotify_songs.csv"


def hello(request):
    return JsonResponse({"hello": "Hello checking api"})


def get_songs_data(request):
    return JsonResponse(analytics.display_table(), safe=False)


def get_file_name(request):
    return JsonResponse({"file_name": analytics.get_file_name()})


# def artist_bar_chart(request):
#     return JsonResponse(analytics.get_artist_barchart_data(), safe=False)


# def volume_added_overtime(request):
#     return JsonResponse(analytics.get_volume_added_overtime(), safe=False)


def analyse_csv(request):
    return JsonResponse(analytics.analyse_csv())


class FileUploadSerializer(serializers.Serializer):
    file = serializers.FileField()


class UploadCSVFileView(APIView):
    parser_classes = [MultiPartParser, FormParser]

    @swagger_auto_schema(request_body=FileUploadSerializer)
    def post(self, request, *args, **kwargs):
        file_serializer = FileUploadSerializer(data=request.data)
        if file_serializer.is_valid():
            file = file_serializer.validated_data["file"]
            if not file.name.endswith(".csv"):
                return Response(
                    {"error": "Invalid file format. Please upload a CSV file."},
                    status=status.HTTP_400_BAD_REQUEST,
                )

            with NamedTemporaryFile(delete=False, suffix=".csv") as temp_file:
                for chunk in file.chunks():
                    temp_file.write(chunk)
                temp_file_path = temp_file.name

            output_csv_file_path = spotify
            similar_songs_list = get_similar_songs(temp_file_path)
            similar_songs_list.sort(
                key=lambda x: (x["Category"], x["Popularity"]), reverse=True
            )
            write_to_csv(similar_songs_list, output_csv_file_path)

            os.remove(temp_file_path)

            return Response(
                {
                    "message": "File uploaded and processed successfully",
                    "filename": file.name,
                }
            )
        else:
            return Response(file_serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class DownloadLogsView(APIView):

    def get(self, request, *args, **kwargs):
        zip_file = generate_daily_logs()
        response = StreamingHttpResponse(
            zip_file, content_type="application/x-zip-compressed"
        )
        response.headers["Content-Disposition"] = "attachment; filename=daily_logs.zip"
        return response


class DownloadPlaylistView(APIView):

    def get(self, request, *args, **kwargs):
        playlist_len = int(request.GET.get("playlist_len", 10))
        docs = build_documents(spotify)
        embeddings = OpenAIEmbeddings(api_key=OPENAI_KEY)
        db = FAISS.from_documents(docs, embeddings)
        build_playlist(
            db, example_file=example_file, dest=dest_playlist, playlist_len=playlist_len
        )
        df = pd.read_csv(dest_playlist)
        csv = df.to_csv(index=False)
        response = StreamingHttpResponse(csv, content_type="text/csv")
        response["Content-Disposition"] = (
            f"attachment; filename={os.path.basename(dest_playlist)}"
        )
        return response
