import datetime
import io
import os
from datetime import datetime
import aiohttp
import disnake
import g4f
import nest_asyncio
import python_weather
from disnake.ext import commands
from gtts import gTTS
from pytube import YouTube
from rembg import remove
from PIL import Image
nest_asyncio.apply()
time = datetime.now()
activity = disnake.Activity(
    name="!help / Currently working",
    type=disnake.ActivityType.playing,
)

bot = commands.Bot(command_prefix='!', intents=disnake.Intents.all(), help_command=None,activity=activity)
client = python_weather.Client(unit=python_weather.IMPERIAL,locale=python_weather.Locale.RUSSIAN)
def help_msg():
    help_msg = disnake.Embed(
    title = "Welcome! Theres a list of available functions:",
    description ="!rembg - remove background from any photos using AI\n"
                "/chatgpt [your_prompt] - chatGPT will write whatever you ask!\n"
                "/gtts [language: ru, en, fr, pt, es] [your_message] - Google text to speach will convert your message to speach!\n"
                "/ytmp3 [youtube_link] - Convert YouTube video into mp3!\n"
                "/weather [any_city] - Find current weather in any city of the world\n"
                "/credits - Will show you credits like used libs and author of this bot\n"
                "/randomcat - Most important function in this bot \n",
    colour = 0xF0C43F,
    timestamp = datetime.now(),
    )
    return help_msg
def credits_msg():
    credit_msg = disnake.Embed(
        title="Credits!",
        description="Used libraries: disnake, pytube, g4f, nest_asyncio, python_weather, gtts\n"
                    "Made by: flo0p1337",
        colour=0xF0C43F,
        timestamp=datetime.now(),
    )
    return credit_msg
def req_claim():
    req_claim = disnake.Embed(
        title="Ваш запрос обрабатывается!",
        description="Ожидайте ответа, вы будете уведомлены по завершению процесса...",
        colour=0xF0C43F,
        timestamp=datetime.now(),
    )
    return req_claim
def req_failed(error):
        disnake.Embed(
        title="Произошла ошибка! Попробуйте переоформить ваш запрос.\n"
              "Код ошибки: ",
        description=error,
        colour=0xF0C43F,
        timestamp=datetime.now(),
            )
def req_done (description):
        req_done = disnake.Embed(
        title="Ваш ответ готов!",
        description=description,
        colour=0xF0C43F,
        timestamp=datetime.now(),
)
        return req_done
def logger(used_command, username, used_prompt, got_response):
    with open('logs/logsDS.txt', 'a') as f:
        log_msg = ['\n' +
                     str("[USER_CMD] ") + str(
            time) + ": " + str(
            username) + f" used {used_command} with prompt -> {used_prompt} and got the reponse -> {got_response}"]
        with open('logs/logsDS.txt', 'a') as f:
            f.write('\n'.join(log_msg))
        print(log_msg.pop(0))