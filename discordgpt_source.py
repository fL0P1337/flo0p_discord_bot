# Import standard libraries
import os
import datetime
import aiohttp
import base64
import io
from io import BytesIO

# Import Discord libraries
import disnake
from disnake.ext import commands

# Import G4F libraries
from g4f.client import AsyncClient
import g4f
from g4f.Provider import ReplicateImage, HuggingChat, Bing, Reka
from g4f.cookies import set_cookies

# Import other libraries
from gtts import gTTS
from pytube import YouTube
from rembg import remove
from PIL import Image

# Import nest_asyncio for asyncio compatibility
import nest_asyncio

# Import custom headers module
import headers

# Import Openai module
from openai import AsyncOpenAI

# Import replicate module
import replicate


# Bot activity and instance creation
activity = disnake.Activity(name="!help / Currently working", type=disnake.ActivityType.playing)
bot = commands.Bot(command_prefix='!', intents=disnake.Intents.all(), help_command=None, activity=activity)

# Enable G4F debug logging and apply nest_asyncio
g4f.debug.logging = True
nest_asyncio.apply()

# Create G4F and OpenAI client instances
client = AsyncClient(image_provider=ReplicateImage)
deepinfra_client = AsyncOpenAI(api_key=headers.get_credential("DEEPINFRA_TOKEN"), base_url="https://api.deepinfra.com/v1/openai")

# Set cookies for Bing, Reka, and Huggingface
set_cookies(".bing.com", {"_U": headers.get_credential('BING_COOKIES')})
set_cookies("chat.reka.ai", {"appSession": headers.get_credential('REKA_COOKIES')})
set_cookies("huggingface.co", {"hf-chat": headers.get_credential('HUGGINGFACE_COOKIES')})

@bot.event
async def on_ready():
    current_time = datetime.datetime.now()
    ready_message = f"{current_time}: Bot {bot.user} is ready to work!"
    headers.log_event('bot_startup')
    print(f"\n[INFO] {ready_message}")

@bot.command()
async def help(ctx):
    await ctx.reply(embed=headers.help_msg())
    headers.log_event('command_usage', 'help', ctx)

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
                    headers.log_event('command_usage', 'randomcat', inter)
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
                headers.log_event('command_usage', 'randomcatgif', inter)
    except aiohttp.ClientError as client_error:
        await inter.edit_original_response(embed=headers.req_failed(f"Failed to connect to {url}: {client_error}"))
    except Exception as error:
        await inter.edit_original_response(embed=headers.req_failed(str(error)))

@bot.slash_command(description="Llama is open source LLM that allows you get really good results")
async def llama(inter, *, your_prompt: str):
    await inter.response.send_message(embed=headers.req_claim())
    try:
        response = await deepinfra_client.chat.completions.create(
            model="meta-llama/Meta-Llama-3-70B-Instruct",
            messages=[{"role": "user", "content": your_prompt}],
        )
        result = response.choices[0].message.content
        await inter.edit_original_response(embed=headers.req_done(result))
        headers.log_event('command_usage', 'llama', inter)
        headers.log_event('bot_response', inter, result)
    except Exception as e:
        error_message = str(e)
        await inter.edit_original_response(embed=headers.req_failed(error=error_message))
        headers.log_event('bot_response', inter, error_message)

@bot.slash_command(description="Lzlv-70b is open source model that actually doesn't have a censor")
async def lzlv(inter, *, your_prompt: str):
    await inter.response.send_message(embed=headers.req_claim())
    try:
        response = await deepinfra_client.chat.completions.create(
            model="lizpreciatior/lzlv_70b_fp16_hf",
            messages=[{"role": "user", "content": your_prompt}],
        )
        response_content = response.choices[0].message.content
        await inter.edit_original_response(embed=headers.req_done(response_content))
        headers.log_event('command_usage', 'lzlv', inter)
        headers.log_event('bot_response', inter, response_content)
    except Exception as e:
        error_message = f"Error: {e}"
        await inter.edit_original_response(embed=headers.req_failed(error=error_message))

@bot.slash_command(description="Bing is LLM created by Microsoft, uses gpt-4 model")
async def bing(inter, *, your_prompt: str):
    await inter.response.send_message(embed=headers.req_claim())
    try:
        response = await client.chat.completions.create(
            model="Copilot",
            messages=[{"role": "user", "content": your_prompt}],
            provider=Bing,
        )
        result = response.choices[0].message.content
        await inter.edit_original_response(embed=headers.req_done(result))
        headers.log_event('command_usage', 'bing', inter)
        headers.log_event('bot_response', inter, result)
    except Exception as e:
        error_message = str(e)
        await inter.edit_original_response(embed=headers.req_failed(error=error_message))
        headers.log_event('bot_response', inter, error_message)

@bot.slash_command(description="SD-XL can draw you a picture from the text prompt")
async def stabblediffusion(inter, *, your_prompt: str):
    await inter.response.send_message(embed=headers.req_claim())
    try:
        replicate_client = {
            "prompt": your_prompt,
            "negative_prompt": "censored, deformed, bad anatomy, disfigured, poorly drawn face, mutated, extra limb, ugly, poorly drawn hands, missing limb, floating limbs, disconnected limbs, disconnected head, malformed hands, long neck, mutated hands and fingers, bad hands, missing fingers, cropped, worst quality, low quality, mutation, poorly drawn, huge calf, bad hands, fused hand, missing hand, disappearing arms, disappearing thigh, disappearing calf, disappearing legs, missing fingers, fused fingers, abnormal eye proportion, Abnormal hands, abnormal legs, abnormal feet, abnormal fingers, (worst quality, low quality, normal quality:2), (blurry:1.2) <UnrealisticDream> <negative_hand-neg>",
            "aspect_ratio": "1:1",
            "output_quality": 100,
            "output_format": "png",
        }
        output = replicate.run("stability-ai/stable-diffusion-3", input=replicate_client)
        await inter.edit_original_response(embed=headers.req_done(" ").set_image(url=output[0]))
        headers.log_event('command_usage', 'stabblediffusion', inter)
    except Exception as genimage_error:
        await inter.edit_original_response(embed=headers.req_failed(error=genimage_error))
        headers.log_event('command_usage', 'stabblediffusion', genimage_error)

@bot.command()
async def vision(ctx, *, text: str):
    await ctx.reply(embed=headers.req_claim())
    try:
        # Here you can use any function to convert the text to image.
        response = await client.image.generate(prompt=text, provider=ReplicateImage)
        if isinstance(response, disnake.File):
            await ctx.send(embed=headers.req_done(" ").set_image(file=response))
        else:
            await ctx.send(embed=headers.req_done(" ").set_image(url=response[0]))
        headers.log_event('command_usage', 'vision', ctx)
        headers.log_event('bot_response', ctx, response)
    except Exception as e:
        await ctx.send(embed=headers.req_failed(error=str(e)))
        headers.log_event('command_usage', 'vision', str(e))

@bot.slash_command(description="Remove background from the image")
async def removebg(inter, file: disnake.Attachment):
    await inter.response.send_message(embed=headers.req_claim())
    image_data = await file.read()
    input_image = Image.open(io.BytesIO(image_data))
    output_image = remove(input_image)
    output_buffer = io.BytesIO()
    output_image.save(output_buffer, format="PNG")
    output_buffer.seek(0)
    await inter.edit_original_response(embed=headers.req_done(" ").set_image(file=disnake.File(output_buffer, "no_bg.png")))
    headers.log_event('command_usage', 'removebg', inter)

@bot.slash_command(description="Convert youtube video to audio")
async def yt2mp3(inter, url: str):
    await inter.response.send_message(embed=headers.req_claim())
    yt = YouTube(url)
    audio = yt.streams.filter(only_audio=True).first()
    audio_path = audio.download()
    await inter.edit_original_response(embed=headers.req_done(f"Audio is ready: {yt.title}").set_file(file=disnake.File(audio_path)))
    os.remove(audio_path)
    headers.log_event('command_usage', 'yt2mp3', inter)

# Run the bot
bot.run(headers.get_credential("DISCORD_TOKEN"))
