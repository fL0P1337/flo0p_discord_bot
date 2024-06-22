# Import required modules
import datetime
import shutil
import os
from datetime import datetime
import disnake
import base64
import aiohttp
import json
import logging
time = datetime.now()

# Set up the logger
logger = logging.getLogger('discord_bot_logger')
logger.setLevel(logging.INFO)

# Create a file handler to log to a file
file_handler = logging.FileHandler('bot.log', encoding='utf-8')
file_handler.setLevel(logging.INFO)

# Create a formatter and attach it to the file handler
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
file_handler.setFormatter(formatter)

# Add the file handler to the logger
logger.addHandler(file_handler)

# Define a logger function to log command usages and bot startups
def log_event(event_type, *args, **kwargs):
    if event_type == 'command_usage':
        logger.info(f'Command "{args[0]}" used by {args[1].author} (ID: {args[1].author.id}) in channel {args[1].channel} (ID: {args[1].channel.id})')
    elif event_type == 'bot_startup':
        logger.info('Bot has started')
    elif event_type == 'user_prompt':
        logger.info(f'User {args[0].author} (ID: {args[0].author.id}) sent prompt: "{args[0].content}"')
    elif event_type == 'bot_response':
        logger.info(f'Bot responded to {args[0].author} (ID: {args[0].author.id}) with: "{args[1]}"')
    elif event_type == 'command_args':
        logger.info(f'Command "{args[0]}" received args: {args[1]}')

def load_credentials():
    # Load credentials from file
    credentials_file = os.path.join(os.path.dirname(__file__), 'credentials.json')
    with open(credentials_file, 'r') as f:
        credentials = json.load(f)
        for line in f.readlines():
            key, value = line.strip().split('=')
            credentials[key] = value.strip()  # Remove any whitespace
            print(f"Loaded credential: {key} = {value}")
    # Return a dictionary with the loaded credentials
    return credentials


def get_credential(key):
    # Load credentials and return the value for the given key
    credentials = load_credentials()
    return credentials.get(key)

def help_msg():
    embed = disnake.Embed(
        title="Welcome! Here's a list of available functions:",
        description="",
        color=0xF0C43F,
        timestamp=datetime.now()
    )

    embed.add_field(
        name="Image-Functions",
        value="/removebg - Remove background from any photos using AI\n",
        inline=False
    )

    embed.add_field(
        name="Text-to-Image Models",
        value="/stabblediffusion [your_prompt] - Stabble Diffusion XL can draw anything from your text prompt\n"
              "/vision [your_prompt] - Classify an image using text prompt, it can describe, read and etc\n",
        inline=False
    )
    
    embed.add_field(
        name="Text-Generation Models",
        value="/llama [your_prompt] - Llama is open source LLM that allows you get really good results\n"
              "/lzlv [your_prompt] - Lzlv-70b is open source model that actually doesn't have a censor\n"
              "/bing [your_prompt] - Bing is LLM created by Microsoft, uses gpt-4 model\n",
        inline=False
    )
    embed.add_field(
        name="Fun-Functions",
        value="/randomcat - Use this to receive random cat image \n"
              "/randomcatgif - Use this to receive random cat gif \n"
              "/yt2mp3 [youtube_link] - Convert YouTube video into mp3!\n",
        inline=False
    )
    embed.add_field(
        name="GitHub Repository",
        value="https://github.com/fL0P1337/flo0p_discord_bot\n",
        inline=False
    )

    return embed

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
        title=f"There's been an error! Try re-posting your request.\nError code:",
        description=error,
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


    
def cleaner():
    """Clean cached user files"""
    dirs_path = ["user_cache"]
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