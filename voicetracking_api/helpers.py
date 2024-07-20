import requests
from datetime import datetime, timedelta
from openai import OpenAI
from config import settings

client = OpenAI(api_key=settings.OPENAI_KEY)


def get_last_week_dates():
    """This function returns all the dates a week ago

    Returns:
        tuple(str, str): Date 7 days ago and today
    """
    today = datetime.now()
    last_week = today - timedelta(days=7)
    return last_week.strftime("%Y-%m-%d"), today.strftime("%Y-%m-%d")


def get_news(title: str):
    api_key = settings.GNEWS_API_KEY  # please put this to .ENV # done

    from_date, to_date = get_last_week_dates()
    base_url = f'https://gnews.io/api/v4/search?q="{title}"&lang=en&country=us&max=3&apikey={api_key}'

    try:
        print(title)
        response = requests.get(base_url)
        try:
            data = response.json()["articles"][0]["description"]
            return data
        except Exception:
            return f"Latest Buzz on {title}"

    except requests.exceptions.RequestException as e:
        print("Error occurred:", e)
        return None


def gpt(prompt: str) -> str:
    with open("static/systemprompt.txt", "r") as sys_p:
        system_prompt = sys_p.read()
    response = client.chat.completions.create(
        model="gpt-4",
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": prompt},
        ],
    )

    # Retrieve the generated response
    message = response.choices[0].message.content
    return message
