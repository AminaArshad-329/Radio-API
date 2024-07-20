import tempfile

from fastapi import status, FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from elevenlabs import generate, set_api_key, voices
from schemas import (
    ScriptRequest,
    ScriptResponse,
    TTSRequest,
    VoiceResponse,
)

from config import settings
from helpers import gpt
from services import add_dynamic_information

# Set Elevel Labls API Key
set_api_key(settings.ELEVEN_LABS_API_KEY)

app = FastAPI(
    title="VoiceTrack API Docs",
    docs_url="/",
    # swagger_ui_parameters={"defaultModelsExpandDepth": -1}, # This will hide the 'schemas' tab on the swagger ui
)

# Middlewares
origins = ["*"]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
    expose_headers=["*"],
)


@app.post(
    "/tts",
    status_code=status.HTTP_200_OK,
    summary="This endpoint is used to generate an audio file based on the script sent",
    tags=["Voicetrack API"],
)
def tts(request: TTSRequest):
    # Generate the audio using the script
    audio = generate(
        text=request.script, voice=request.voice_id, model="eleven_multilingual_v2"
    )
    with tempfile.NamedTemporaryFile(suffix=".mp3", delete=False) as tmpFile:
        tmpFile.write(audio)
        return FileResponse(tmpFile.name, media_type="audio/mp3")


@app.get(
    "/tts/voices",
    status_code=status.HTTP_200_OK,
    summary="This endpoint is used to get the available AI RadioPlayer voices you can use",
    response_model=VoiceResponse,
    tags=["Voicetrack API"],
)
def get_tts_voices():
    return VoiceResponse(voices=[voice.name for voice in voices()])


@app.post(
    "/script",
    status_code=status.HTTP_200_OK,
    summary="This endpoint is used to generata a script",
    response_model=ScriptResponse,
    tags=["Voicetrack API"],
)
def get_ai_script(request: ScriptRequest):
    prompt = add_dynamic_information(data=request)
    script = gpt(prompt=prompt)
    return ScriptResponse(script=script)
