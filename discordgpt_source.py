import os
from datetime import datetime
import aiohttp
import base64
import io
from io import BytesIO

import disnake
from disnake.ext import commands

from g4f.client import AsyncClient
import g4f
from g4f.Provider import ReplicateImage, DeepInfra, Llama

from gtts import gTTS
from pytube import YouTube
from rembg import remove
from PIL import Image

import nest_asyncio

import headers
#import easyocr
time = datetime.now()

activity = disnake.Activity(
name="!help / Currently working",
type=disnake.ActivityType.playing,
)

bot = commands.Bot(
command_prefix='!',
intents=disnake.Intents.all(),
help_command=None,
activity=activity
)

g4f.debug.logging = True
nest_asyncio.apply()

client = AsyncClient(image_provider=ReplicateImage)
headers.cleaner() # enable this optionally
@bot.event
async def on_ready():
    ready_to_work = f"{time}: Bot {bot.user} is ready to work!"
    logs_on_ready = [f"\n[INFO] {ready_to_work}"]
    with open('logs/logsDS.txt', 'a') as f:
        f.write('\n'.join(logs_on_ready))
        print(logs_on_ready.pop(0))

@bot.command()
async def help(ctx):
    await ctx.reply(embed=headers.help_msg())
    headers.logger("!help", ctx.author, ctx, " ")

@bot.slash_command(description="Will show you credits like used libs and author of this bot")
async def credits(inter):
    await inter.response.send_message(embed=headers.credits_msg())
    headers.logger("!credits", inter.author, inter, " ")

@bot.slash_command(description="Receive random cat image")
async def randomcat(inter):
    try:
        await inter.response.send_message(embed=headers.req_claim())
        async with aiohttp.ClientSession() as session:
            async with session.get('https://cataas.com/cat') as resp:
                if resp.status == 200:
                    data = io.BytesIO(await resp.read())
                    file = disnake.File(data, "cool_image.png")
                    embed = headers.req_done(" ").set_image(file=file)
                    await inter.edit_original_response(embed=embed)
                    headers.logger("!randomcat", inter.author, "inter", "data")
                else:
                    await inter.edit_original_response(embed=headers.req_failed(f"Failed to retrieve cat image (status code {resp.status})"))
    except aiohttp.ClientError as client_error:
        await inter.edit_original_response(embed=headers.req_failed(f"Client error: {client_error}"))
    except Exception as e:
        await inter.edit_original_response(embed=headers.req_failed(f"An error occurred: {e}"))


@bot.slash_command(description="Receive random cat gif")
async def randomcatgif(inter):
    try:
        await inter.response.send_message(embed=headers.req_claim())
        async with aiohttp.ClientSession() as session:
            url = 'https://cataas.com/cat/gif'
            async with session.get(url) as resp:
                if resp.status != 200:
                    raise Exception(f"Failed to retrieve GIF from {url}")
                data = io.BytesIO(await resp.read())
                file = disnake.File(data, "cool_gif.gif")
                embed = headers.req_done(" ").set_image(file=file)
                await inter.edit_original_response(embed=embed)
                headers.logger("!randomcatgif", inter.author, "inter", "data")
    except aiohttp.ClientError as client_error:
        await inter.edit_original_response(embed=headers.req_failed(f"Failed to connect to {url}: {client_error}"))
    except Exception as error:
        await inter.edit_original_response(embed=headers.req_failed(str(error)))


@bot.slash_command(description="Llama is open source LLM that allows you get really good results")
async def llama(inter, *, your_prompt: str):
    try:
        await inter.response.send_message(embed=headers.req_claim())
        response = await client.chat.completions.create(
            model=g4f.models.llama3_70b_instruct,
            provider=Llama,
            messages=[{"role": "user", "content": your_prompt}],
        )
        result = response.choices[0].message.content
        await inter.edit_original_response(embed=headers.req_done(result))
        headers.logger("!llama", inter.author, your_prompt, result)
    except Exception as e:
        error_message = str(e)
        await inter.edit_original_response(embed=headers.req_failed(error=error_message))
        headers.logger("!llama", inter.author, your_prompt, error_message)


@bot.slash_command(description="Lzlv-70b is open source model that actually doesnt have a censor")
async def lzlv(inter, *, your_prompt: str):
    try:
        await inter.response.send_message(embed=headers.req_claim())
        response = await client.chat.completions.create(
            model=g4f.models.lzlv_70b,
            provider=DeepInfra,
            messages=[{"role": "user", "content": your_prompt}],
            api_key="////"
        )
        response_content = response.choices[0].message.content
        await inter.edit_original_response(embed=headers.req_done(response_content))
        headers.logger("!lzlv", inter.author, your_prompt, response_content)
    except Exception as e:
        error_message = f"Error: {e}"
        await inter.edit_original_response(embed=headers.req_failed(error=error_message))
        headers.logger("!lzlv", inter.author, your_prompt, error_message)


@bot.slash_command(description="SD-XL can draw you a picture from the text prompt")
async def sdxl(inter, *, your_prompt: str):
    try:
        # Send initial response with "claim" embed
        await inter.response.send_message(embed=headers.req_claim())

        # Generate image using Stability AI model
        resp_image = await client.images.generate(model="stability-ai/sdxl", prompt=your_prompt)
        image_url = resp_image.data[0].url

        # Convert image URL to bytes stream
        image_bytes = BytesIO(base64.b64decode(await headers.async_encode_base64(image_url)))

        # Edit original response with "done" embed and image attachment
        await inter.edit_original_response(
            embed=headers.req_done(" ").set_image(file=disnake.File(image_bytes, "result.png"))
        )

        # Log successful request
        headers.logger("!sdxl", inter.author, your_prompt, image_url)

    except Exception as genimage_error:
        # Edit original response with "failed" embed
        await inter.edit_original_response(embed=headers.req_failed(error=genimage_error))

        # Log failed request
        headers.logger("!sdxl", inter.author, your_prompt, genimage_error)


@bot.slash_command(description="Convert YouTube video into mp3!")
async def ytmp3(inter, *, youtube_link: str):
    try:
        await inter.response.send_message(embed=headers.req_claim())
        yt = YouTube(youtube_link)
        filename = f"files/ytmp3/converted_{yt.title}.mp3"
        audio_stream = yt.streams.filter(only_audio=True).first()
        audio_stream.download(filename=filename)
        
        await inter.edit_original_response(embed=headers.req_done("Видео загружено!\nНачинаю процесс конвертации..."))
        
        with open(filename, "rb") as fp:
            file = disnake.File(fp, yt.title + ".mp3")
            await inter.edit_original_response(embed=headers.req_done("Успешно сконвертировао!"), file=file)
        
        headers.logger("!ytmp3", inter.author, youtube_link, filename)
    
    except Exception as error:
        await inter.edit_original_response(embed=headers.req_failed(error))
        headers.logger("!ytmp3", inter.author, inter, error)

@bot.slash_command(description="Google text to speech will convert your message to speech!")
async def gtts(inter, language: str, *, message: str):
    try:
        tts = gTTS(text=message, lang=language)
        fp = BytesIO()
        tts.write_to_fp(fp)
        fp.seek(0)

        file = disnake.File(fp, f"{message}.mp3")
        await inter.response.send_message(embed=headers.req_done("Успешно!").set_image(file=file))

        headers.logger("!gtts", inter.author, f"{language} {message}")
    except Exception as error:
        await inter.response.send_message(headers.req_failed(error))
        headers.logger("!gtts", inter.author, message, error)


@bot.command(description="Remove background from any photos")
async def rembg(ctx):
    try:
        for attachment in ctx.message.attachments:
            await ctx.reply(embed=headers.req_claim())
            file_path = f"files/rembg/{attachment.filename}"
            await attachment.save(file_path)
            output_path = f"{file_path}_rembg.png"
            img = Image.open(file_path)
            output = remove(img)
            output.save(output_path)
            await ctx.reply(embed=headers.req_done(" ").set_image(file=disnake.File(output_path)))
            headers.logger("!rembg", ctx.author, attachment.filename, output_path)
    except Exception as error:
        await ctx.reply(embed=headers.req_failed(error))
        headers.logger("!rembg", ctx.author, attachment.filename, error)

bot.run(headers.get_bot_token())
""" OCR function
@bot.command(description="OCR allows you to grab text from images!")
async def imgtotxt(ctx):
    try:
        for attachment in ctx.message.attachments:
            await ctx.reply(embed=headers.req_claim())
            input_path = f"files/imgtotxt/{attachment.filename}"
            await attachment.save(input_path)
            reader = easyocr.Reader(['en', "ru"])
            result = reader.readtext(input_path, detail = 0)
            await ctx.reply(embed=headers.req_done(result))
            headers.logger("!imgtotxt", ctx.author, attachment.filename, result)
    except Exception as error:
            await ctx.reply(headers.req_failed(error))
            headers.logger("!imgtotxt", ctx.author, attachment.filename, error)
"""
