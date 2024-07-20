from schemas import ScriptRequest
from helpers import get_news


def add_dynamic_information(data: ScriptRequest):
    """This function is used to add dynamic information to the prompt

    Args:
        data (ScriptRequest): The script request
    """
    prompt = data.prompt
    prompt = (
        prompt.replace("{PREVIOUS_ARTIST}", data.previous_artist)
        .replace("{PRESENTER}", data.presenter)
        .replace("{STATION}", data.station)
        .replace("{NEXT_ARTIST}", data.next_artist)
        .replace("{NEXT_SONG}", data.next_song)
        .replace("{DYNAMIC}", get_news(title=data.next_artist))
    )
    return prompt
