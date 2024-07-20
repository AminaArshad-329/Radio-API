from pydantic import BaseModel, Field


class TTSRequest(BaseModel):
    """This schema is used to generate an audio file"""

    script: str = Field(description="The script to be used to generate the audio file")
    voice_id: str = Field(description="The voice to use")


class VoiceResponse(BaseModel):
    voices: list[str] = Field(
        description="The list of valid voices you can use to generate the tts"
    )


class ScriptRequest(BaseModel):
    """Schema for generating a script for TTS (Text-to-Speech)"""

    prompt: str = Field(description="The prompt to use")
    presenter: str = Field(description="The presenter's name")
    station: str = Field(description="The name of the radio station")
    previous_artist: str = Field(description="Name of the artist before the current one")
    next_artist: str = Field(description="Name of the artist after the current one")
    next_song: str = Field(description="Title of the next song")


class ScriptResponse(BaseModel):
    """This schema is used to return the script after it is generated"""

    script: str = Field(description="The generated script")
