import json
import os
import random

import requests
from openai import OpenAI
from gnews import GNews
from langchain_community.utilities import GoogleSerperAPIWrapper

openai_client = OpenAI(api_key=os.environ.get("OPENAI_KEY"))

search = GoogleSerperAPIWrapper(
    serper_api_key=os.environ.get("SERPER_API_KEY"), type="news", k=5
)


def get_elevenlab_voices():
    cherry_picked = {
        "Patrick": "6ojqEwe8C35npMRgRZxr",
        "Paul": "EXFJSSZT3nA081bVg99i",
        "Peter": "MGPAlYFBTf6viQcpoCVf",
        "Philip": "OJjYoSIpSUXCRMMxj5Je",
        "Pippa": "VqhODWFVNPDD7zn9N0p0",
        "Howard": "eiFEEKWFowmp1lZBzF5v",
        "Polly": "pTQ1CLytjIBKIIszzqV9",
        "Piers": "slOtqOiygfkR71FQ8H9s",
        "Pamela": "v5LtDujiFgAmwVYuEHrF",
    }

    values = [{"name": k, "voice_id": v} for k, v in cherry_picked.items()]
    return values


def speak_elevenlabs(text, filename, voice="Patrick"):
    voices = {
        "Patrick": "6ojqEwe8C35npMRgRZxr",
        "Paul": "EXFJSSZT3nA081bVg99i",
        "Peter": "MGPAlYFBTf6viQcpoCVf",
        "Philip": "OJjYoSIpSUXCRMMxj5Je",
        "Pippa": "VqhODWFVNPDD7zn9N0p0",
        "Howard": "eiFEEKWFowmp1lZBzF5v",
        "Polly": "pTQ1CLytjIBKIIszzqV9",
        "Piers": "slOtqOiygfkR71FQ8H9s",
        "Pamela": "v5LtDujiFgAmwVYuEHrF",
    }

    url = f"https://api.elevenlabs.io/v1/text-to-speech/{voices[voice]}?optimize_streaming_latency=0"

    payload = json.dumps(
        {
            "text": text,
            "model_id": "eleven_monolingual_v1",
            "voice_settings": {
                "stability": 0,
                "similarity_boost": 0,
                "style": 0.5,
                "use_speaker_boost": True,
            },
        }
    )

    headers = {
        "accept": "audio/mpeg",
        "xi-api-key": os.environ.get("ELEVEN_LABS_API_KEY"),
        "Content-Type": "application/json",
    }

    response = requests.request("POST", url, headers=headers, data=payload)

    if response.status_code == 200:
        with open(filename, "wb") as f:
            f.write(response.content)


def get_current_weather(location, unit="celsius"):
    data = (
        requests.get(
            f'https://api.weatherapi.com/v1/current.json?key={os.environ.get("WEATHER_API")}&q={location}'
        )
        .json()
        .get("current")
    )
    weather_info = {
        "location": location,
        "temperature": data.get("temp_c") if unit == "celsius" else data.get("temp_f"),
        "unit": unit,
    }
    return json.dumps(weather_info)


def get_news(topic: str, period="2d", maxResults=10):
    google_news = GNews(period=period, max_results=maxResults)
    try:
        news = google_news.get_news_by_topic(topic=topic)
        random.shuffle(news)
        news = news[0]

    except IndexError:
        news = {
            "title": "NFL fines former Commanders owner Dan Snyder $60M for workplace misconduct - The Athletic",
            "description": "NFL fines former Commanders owner Dan Snyder $60M for workplace misconduct  The AthleticCommanders' Dan Snyder fined $60M over findings in investigation  ESPNDaniel Snyder selling doesn't make things right. That's up to Josh Harris.  The Washington PostWashington Commanders sold to Josh Harris group  WUSA9NFL owners approve $6.05B sale of Commanders to Harris group - ESPN  ESPNView Full Coverage on Google News",
        }
    news_data = {"title": news.get("title"), "description": news.get("description")}

    return json.dumps(news_data)


def get_news_script(prompt: str):
    messages = [{"role": "user", "content": prompt}]

    functions = [
        {
            "name": "get_current_weather",
            "description": "Get the current weather in a given location of same day",
            "parameters": {
                "type": "object",
                "properties": {
                    "location": {
                        "type": "string",
                        "description": "The city and state, e.g. San Francisco, CA",
                    },
                    "unit": {"type": "string", "enum": ["celsius", "fahrenheit"]},
                },
                "required": ["location", "unit"],
            },
        },
        {
            "name": "get_news",
            "description": "Get news about a topic user specifies",
            "parameters": {
                "type": "object",
                "properties": {
                    "topic": {
                        "type": "string",
                        "enum": ["SPORTS", "WORLD", "ENTERTAINMENT"],
                    }
                },
            },
        },
    ]

    response = openai_client.chat.completions.create(
        model="gpt-4-0613",
        messages=messages,
        functions=functions,
        function_call="auto",
    )
    response_message = response.choices[0].message

    if getattr(response_message, "function_call", None):
        available_functions = {
            "get_current_weather": get_current_weather,
            "get_news": get_news,
        }

        function_name = response_message.function_call.name
        fuction_to_call = available_functions[function_name]
        function_args = json.loads(response_message.function_call.arguments)
        function_response = fuction_to_call(**function_args)

        messages.append(response_message)  # extend conversation with assistant's reply
        messages.extend(
            [
                {
                    "role": "function",
                    "name": function_name,
                    "content": function_response,
                },
                {
                    "role": "system",
                    "content": "You are a news reporter that creates a 5 second script from a title and a brief description of an article. The scripts you write dont have breaking news or stay tuned or good eventing or anything like that, they are just about the article itself. You also dont talk about how to follow up the article. You dont talk about your name.",
                },
            ]
        )

        if function_name == "get_current_weather":
            messages.append(
                {
                    "role": "user",
                    "content": "Create a 5 second script for a news reporter to read live about this weather situation",
                }
            )
        else:
            messages.append(
                {
                    "role": "user",
                    "content": "Create a 5 second script for a news reporter to read live about this news given the title and description. No hashtags",
                }
            )

        second_response = openai_client.chat.completions.create(
            model="gpt-4-0613",
            messages=messages,
        )

        return second_response.choices[0].message.content


def generate_bulletin(bulletin):
    response = openai_client.chat.completions.create(
        model="gpt-4-0613",
        messages=[
            {
                "role": "system",
                "content": "You are a news reporter that creates a news bulletin from a comma separated set of news. The scripts you write dont have breaking news or stay tuned or good evening or anything like that, they are just about the news. You also dont talk about how to follow up the articles. There is no intro and no outros",
            },
            {
                "role": "user",
                "content": "Create a script for a news reporter to read live about these news."
                + bulletin,
            },
        ],
    )

    # Retrieve the generated response
    message = response.choices[0].message.content
    return message
