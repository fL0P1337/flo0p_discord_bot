import datetime
import shutil
import os
from datetime import datetime
import disnake
import base64
import aiohttp
time = datetime.now()

def get_bot_token(): #function to get discord bot token using bot_token.txt
     bot_token = open("bot_token.txt",)
     return bot_token.read()
def help_msg():
    embed = disnake.Embed(
        title="Welcome! Here's a list of available functions:",
        description="",
        color=0xF0C43F,
        timestamp=datetime.now()
    )

    embed.add_field(
        name="Image-Functions",
        value="!rembg - Remove background from any photos using AI\n"
              #"!imgtotxt - Extract text from image, supports Russian and English languages"
              ,
        inline=False
    )

    embed.add_field(
        name="Text-to-Image Models",
        value="/sdxl [your_prompt] - Stabble Diffusion XL can draw anything from your text prompt\n",
        inline=False
    )
    
    embed.add_field(
        name="Text-Generation Models",
        value="/llama [your_prompt] - Llama is open source LLM that allows you get really good results\n"
              "/lzlv [your_prompt] - Lzlv-70b is open source model that actually doesn't have a censor\n",
        inline=False
    )

    embed.add_field(
        name="Utility-Functions",
        value="/gtts [language: ru, en, fr, pt, es] [your_message] - Google text to speech will convert your message to speech!\n"
              "/ytmp3 [youtube_link] - Convert YouTube video into mp3!\n"
              "/credits - Will show you credits like used libs and author of this bot\n",
        inline=False
    )

    embed.add_field(
        name="Fun-Functions",
        value="/randomcat - Use this to receive random cat image \n"
              "/randomcatgif - Use this to receive random cat gif \n",
        inline=False
    )

    return embed

def credits_msg():
    """
    Create the /credits embed message content
    """
    credit_msg = disnake.Embed(
        title="Credits!",
        description=(
            "Used libraries:\n"
            "• disnake\n"
            "• pytube\n"
            "• g4f\n"
            "• nest_asyncio\n"
            "• gtts\n"
            "• rembg\n"
            "\nMade by: flo0p1337"
        ),
        color=0xF0C43F,
        timestamp=datetime.now()
    )
    return credit_msg

def req_claim():
    """Returns an embed message for request claim"""
    embed = disnake.Embed(
        title="Your request is being processed!",
        description="Wait for a response, you will be notified when the process is complete...",
        color=0xF0C43F,
        timestamp=datetime.now()
    )
    return embed

def req_failed(error):
    embed = disnake.Embed(
        title=f"There's been an error! Try re-posting your request.\nError code: {error}",
        colour=0xF0C43F,
        timestamp=datetime.now()
    )
    return embed

def req_done(description: str) -> disnake.Embed:
    """Create an embed message for done requests"""
    embed = disnake.Embed(
        title="Your answer is ready!",
        description=description,
        color=0xF0C43F,
        timestamp=datetime.now()
    )
    return embed

def logger(used_command, username, used_prompt, got_response):
    log_msg = f"\n[USER_CMD] {time.time()}: {username} used {used_command} with prompt -> {used_prompt} and got the response -> {got_response}"
    with open('logs/logsDS.txt', 'a') as f:
        f.write(log_msg + '\n')
    print(log_msg)
    
def cleaner():
    """Clean cached user files"""
    dirs_path = ["files/rembg", "files/gtts", "files/ytmp3"]
    for folder in dirs_path:
        for root, dirs, files in os.walk(folder):
            for file in files:
                file_path = os.path.join(root, file)
                try:
                    os.unlink(file_path)
                except Exception as e:
                    print(f"Failed to delete {file_path}. Reason: {e}")
            for dir in dirs:
                dir_path = os.path.join(root, dir)
                try:
                    shutil.rmtree(dir_path)
                except Exception as e:
                    print(f"Failed to delete {dir_path}. Reason: {e}")
    
async def async_encode_base64(image_url: str): #  Asynchronously takes a url of direct image, downloads, and encodes that into a bytes object using Base64 encoding
    b64_object_string = " " 
    async with aiohttp.ClientSession() as sess:
        async with sess.get(url=image_url) as resp:
            if resp.status == 200:
            # Convert image to bytes
                resp = await resp.read()
                bytestring = base64.b64encode(resp)
                    
    return bytestring