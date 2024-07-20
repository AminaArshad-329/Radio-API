import os

from pydantic_settings import BaseSettings


class Settings(BaseSettings):

    # Eleven Labs
    ELEVEN_LABS_API_KEY: str = os.environ.get("ELEVEN_LABS_API_KEY")

    # OpenAI
    OPENAI_KEY: str = os.environ.get("OPENAI_KEY")

    # G-News
    GNEWS_API_KEY: str = os.environ.get("GNEWS_API_KEY")

    class Config:
        env_file = ".env"


settings = Settings()
