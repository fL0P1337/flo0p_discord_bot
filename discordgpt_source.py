# Import required modules
import os
import datetime
import aiohttp
import base64
import io
from io import BytesIO

# Import Discord modules
import disnake
from disnake.ext import commands

# Import G4F modules
from g4f.client import AsyncClient
import g4f
from g4f.Provider import ReplicateImage, DeepInfra, Bing, Reka
from g4f.cookies import set_cookies

# Import other modules
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

# Define bot activity
activity = disnake.Activity(
    name="!help / Currently working",
    type=disnake.ActivityType.playing,
)

# Create bot instance with custom prefix, intents, and activity
bot = commands.Bot(
    command_prefix='!',
    intents=disnake.Intents.all(),
    help_command=None,
    activity=activity,
)

# Enable G4F debug logging
g4f.debug.logging = True

# Apply nest_asyncio for asyncio compatibility
nest_asyncio.apply()

# Create G4F client instance with ReplicateImage provider
client = AsyncClient(image_provider=ReplicateImage)

# Create an OpenAI client with your deepinfra token and endpoint
deepinfra_client = AsyncOpenAI(
    api_key=headers.get_credential("DEEPINFRA_TOKEN"),
    base_url="https://api.deepinfra.com/v1/openai",
)

# Set Bing Cookies (!vision function)
set_cookies(".bing.com",
            {
                "_U" : headers.get_credential('BING_COOKIES')
})
set_cookies("chat.reka.ai",
            {
                "appSession" : headers.get_credential('REKA_COOKIES')
})

@bot.event
async def on_ready():
    # Log the bot's readiness to the console and log file
    current_time = datetime.datetime.now() # Get the current time
    ready_message = f"{current_time}: Bot {bot.user} is ready to work!"
    logs_on_ready = [f"\n[INFO] {ready_message}"]
    
    # Write the log message to the log file
    headers.log_event('bot_startup')
        
    # Print the log message to the console
    print(logs_on_ready.pop(0))

@bot.command()
async def help(ctx):
    # Send a help message to the user
    await ctx.reply(embed=headers.help_msg())
    
    # Log the command usage
    headers.log_event('command_usage', 'help', ctx)

@bot.slash_command(description="Will show you credits like used libs and author of this bot")
async def credits(inter):
    # Send a credits message to the user
    await inter.response.send_message(embed=headers.credits_msg())
    
    # Log the command usage
    headers.log_event('command_usage', 'credits', inter)

@bot.slash_command(description="Receive random cat image")
async def randomcat(inter):
    """
    Send a random cat image to the user.
    """
    try:
        # Send a initial response to let the user know we're working on it
        await inter.response.send_message(embed=headers.req_claim())
        
        # Create an aiohttp client session to make the API request
        async with aiohttp.ClientSession() as session:
            # Make a GET request to the Cataas API to retrieve a random cat image
            async with session.get('https://cataas.com/cat') as resp:
                # Check if the response was successful (200 OK)
                if resp.status == 200:
                    # Read the response data into a bytes buffer
                    data = io.BytesIO(await resp.read())
                    
                    # Create a disnake File object from the bytes buffer
                    file = disnake.File(data, "cool_image.png")
                    
                    # Create an embed with the image
                    embed = headers.req_done(" ").set_image(file=file)
                    
                    # Edit the initial response with the new embed
                    await inter.edit_original_response(embed=embed)
                    
                    # Log the successful request
                    headers.log_event('command_usage', 'randomcat', inter)
                else:
                    # If the response was not successful, send an error message
                    await inter.edit_original_response(embed=headers.req_failed(f"Failed to retrieve cat image (status code {resp.status})"))
    
    except aiohttp.ClientError as client_error:
        # Handle any aiohttp client errors (e.g. connection issues)
        await inter.edit_original_response(embed=headers.req_failed(f"Client error: {client_error}"))
    
    except Exception as e:
        # Catch any other unexpected errors
        await inter.edit_original_response(embed=headers.req_failed(f"An error occurred: {e}"))

@bot.slash_command(description="Receive random cat gif")
async def randomcatgif(inter):
    """
    Send a random cat GIF to the Discord channel
    """
    try:
        # Send a initial response to indicate that the bot is processing the request
        await inter.response.send_message(embed=headers.req_claim())
        
        # Create an aiohttp ClientSession to make a GET request to the cat GIF API
        async with aiohttp.ClientSession() as session:
            url = 'https://cataas.com/cat/gif'  # URL of the cat GIF API
            
            # Make a GET request to the API
            async with session.get(url) as resp:
                if resp.status != 200:
                    # Raise an exception if the response status is not 200 OK
                    raise Exception(f"Failed to retrieve GIF from {url}")
                
                # Read the response data into a BytesIO buffer
                data = io.BytesIO(await resp.read())
                
                # Create a disnake File object from the buffer
                file = disnake.File(data, "cool_gif.gif")
                
                # Create an embed with the GIF and send it as an edit to the original response
                embed = headers.req_done(" ").set_image(file=file)
                await inter.edit_original_response(embed=embed)
                
                # Log the successful request
                headers.log_event('command_usage', 'randomcatgif', inter)
    
    except aiohttp.ClientError as client_error:
        # Catch any aiohttp ClientErrors (e.g. connection errors) and send an error message
        await inter.edit_original_response(embed=headers.req_failed(f"Failed to connect to {url}: {client_error}"))
    
    except Exception as error:
        # Catch any other exceptions and send an error message
        await inter.edit_original_response(embed=headers.req_failed(str(error)))


@bot.slash_command(description="Llama is open source LLM that allows you get really good results")
async def llama(inter, *, your_prompt: str):
    """
    Handle the!llama command, which uses the Llama AI model to generate a response
    to a user-provided prompt.

    Args:
        inter: The interaction object from Discord.py
        your_prompt: The user-provided prompt to generate a response for
    """
    try:
        # Send a "loading" message to the user
        await inter.response.send_message(embed=headers.req_claim())

        # Create a completion request to the Llama AI model
        response = await deepinfra_client.chat.completions.create(
            # Use the Llama 3 70B instruct model
            model="meta-llama/Meta-Llama-3-70B-Instruct",
            # Provide the user's prompt as input
            messages=[{"role": "user", "content": your_prompt}],
        )

        # Extract the generated response from the API response
        result = response.choices[0].message.content

        # Edit the original response to show the generated result
        await inter.edit_original_response(embed=headers.req_done(result))

        # Log the interaction and result
        headers.log_event('command_usage', 'llama', inter)
        headers.log_event('bot_response', inter, result)
    except Exception as e:
        # Catch any exceptions and log the error
        error_message = str(e)
        await inter.edit_original_response(embed=headers.req_failed(error=error_message))
        headers.log_event('bot_response', inter, error_message)

@bot.slash_command(description="Lzlv-70b is open source model that actually doesn't have a censor")
async def lzlv(inter, *, your_prompt: str):
    """
    Handles the `/lzlv` slash command, which interacts with the Lzlv-70b model.
    """
    try:
        # Send an initial response to let the user know we're working on their request
        await inter.response.send_message(embed=headers.req_claim())
        
        # Create a completion request to the Lzlv-70b model
        response = await deepinfra_client.chat.completions.create(
            model="lizpreciatior/lzlv_70b_fp16_hf",  # specify the model to use
            messages=[{"role": "user", "content": your_prompt}],  # define the input message
        )
        
        # Extract the response content from the completion response
        response_content = response.choices[0].message.content
        
        # Edit the original response with the completed content
        await inter.edit_original_response(embed=headers.req_done(response_content))
        
        # Log the request and response details
        headers.log_event('command_usage', 'lzlv', inter)
        headers.log_event('bot_response', inter, response_content)
    
    except Exception as e:
        # Catch any exceptions that occur and handle them gracefully
        error_message = f"Error: {e}"
        await inter.edit_original_response(embed=headers.req_failed(error=error_message))

@bot.slash_command(description="Bing is LLM created by Microsoft, uses gpt-4 model")
async def bing(inter, *, your_prompt: str):
    """
    Handle the /bing command, which uses the Bing AI model to generate a response
    to a user-provided prompt.

    Args:
        inter: The interaction object from Discord.py
        your_prompt: The user-provided prompt to generate a response for
    """
    try:
        # Send a "loading" message to the user
        await inter.response.send_message(embed=headers.req_claim())

        # Create a completion request to the Bing AI model
        response = await client.chat.completions.create(
            # Use the Bing model
            model="Creative",
            # Provide the user's prompt as input
            messages=[{"role": "user", "content": your_prompt}],
            provider=Bing,
        )
        # Extract the generated response from the API response
        result = response.choices[0].message.content
        # Edit the original response to show the generated result
        await inter.edit_original_response(embed=headers.req_done(result))

        # Log the interaction and result
        headers.log_event('command_usage', 'bing', inter)
        headers.log_event('bot_response', inter, result)
    except Exception as e:
        # Catch any exceptions and log the error
        error_message = str(e)
        await inter.edit_original_response(embed=headers.req_failed(error=error_message))
        headers.log_event('bot_response', inter, error_message)

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
        headers.log_event('command_usage', 'sdxl', inter)
    except Exception as genimage_error:
        # Edit original response with "failed" embed
        await inter.edit_original_response(embed=headers.req_failed(error=genimage_error))

        # Log failed request
        headers.log_event('command_usage', 'randomcatgif', genimage_error)

@bot.command()
async def vision(ctx, your_prompt: str):
    try:
        # Check if the user has attached an image
        if not ctx.message.attachments:
            await ctx.reply(embed=headers.req_failed("Please attach an image to classify!"))
            return

        await ctx.reply(embed=headers.req_claim())

        # Download the attached image
        attachment = ctx.message.attachments[0]
        image_data = await attachment.read()

        # Use BytesIO object to store image data in memory
        image_stream = io.BytesIO(image_data)

        # Create the chat completion request
        response = await client.chat.completions.create(
            model="reka",
            provider=Reka,
            messages=[{"role": "user", "content": your_prompt}],
            image=image_stream
        )

        response_content = response.choices[0].message.content

        # Reset stream position to the beginning
        image_stream.seek(0)

        # Send the classification result back to the user
        await ctx.reply(embed=headers.req_done(response_content).set_image(file=disnake.File(fp=image_stream, filename="image.png")))
        headers.log_event('command_usage', 'vision', ctx)
        headers.log_event('bot_response', ctx, response_content)

    except aiohttp.ClientError as e:
        await ctx.reply(embed=headers.req_failed(f"Error connecting to API: {e}"))

    except Exception as e:
        await ctx.reply(embed=headers.req_failed(f"An error occurred: {e}"))
@bot.slash_command(description="Convert YouTube video into mp3!")
async def ytmp3(inter, *, youtube_link: str):
    """
    Converts a YouTube video into an MP3 file and sends it to the user.

    Args:
        inter: The interaction object
        youtube_link: The URL of the YouTube video to convert
    """
    try:
        # Send a initial response to let the user know we're processing their request
        await inter.response.send_message(embed=headers.req_claim())

        # Create a YouTube object from the provided link
        yt = YouTube(youtube_link)

        # Generate a filename for the MP3 file
        filename = f"user_cache/{yt.title}.mp3"

        # Get the first audio-only stream from the YouTube video
        audio_stream = yt.streams.filter(only_audio=True).first()

        # Download the audio stream to the generated filename
        audio_stream.download(filename=filename)

        # Send an update to the user letting them know the video has been downloaded
        await inter.edit_original_response(embed=headers.req_done("Video is downloaded!\nStarting to convert..."))

        # Open the downloaded MP3 file in binary read mode
        with open(filename, "rb") as fp:
            # Create a File object to send to Discord
            file = disnake.File(fp, yt.title + ".mp3")

            # Send the final response with the MP3 file attached
            await inter.edit_original_response(embed=headers.req_done("Succesfully converted!"), file=file)

        # Log the successful conversion
        headers.log_event('command_usage', 'ytmp3', inter)
        headers.log_event('bot_response', inter, youtube_link)
    except Exception as error:
        # Catch any exceptions that occur during the conversion process
        await inter.edit_original_response(embed=headers.req_failed(error))

@bot.slash_command(description="Google text to speech will convert your message to speech!")
async def gtts(inter, language: str, *, message: str):
    """
    Convert a given message to speech using Google Text-to-Speech (GTTS)
    
    Args:
        inter: Interaction object
        language: Language code for GTTS (e.g. "en" for English)
        message: Text to be converted to speech
    """
    try:
        # Create a GTTS object with the given message and language
        tts = gTTS(text=message, lang=language)
        
        # Create a BytesIO file buffer to store the audio data
        fp = BytesIO()
        
        # Write the audio data to the file buffer
        tts.write_to_fp(fp)
        
        # Reset the file buffer pointer to the beginning
        fp.seek(0)
        
        # Create a disnake.File object from the file buffer
        file = disnake.File(fp, f"{message}.mp3")
        
        # Send a response message with an embedded audio file
        await inter.response.send_message(embed=headers.req_done("Success!").set_image(file=file))
        
        # Log the successful request
        headers.log_event('command_usage', 'gtts', inter)

    except Exception as error:
        # Catch any exceptions that occur during the GTTS process
        await inter.response.send_message(headers.req_failed(error))

@bot.command(description="Remove background from any photos")
async def rembg(ctx):
    """
    Remove background from attached images
    """
    try:
        # Iterate over each attachment in the message
        for attachment in ctx.message.attachments:
            # Send a "processing" message to the user
            await ctx.reply(embed=headers.req_claim())
            
            # Read the attachment as bytes
            img_bytes = await attachment.read()
            
            # Open the image using PIL
            img = Image.open(BytesIO(img_bytes))
            
            # Remove the background from the image
            output = remove(img)
            
            # Save the output image to a BytesIO stream
            output_bytes = BytesIO()
            output.save(output_bytes, format="PNG")
            output_bytes.seek(0)
            
            # Create a new file object with the output image
            file = disnake.File(fp=output_bytes, filename=f"{attachment.filename}_rembg.png")
            
            # Send the output image back to the user
            await ctx.reply(embed=headers.req_done(" ").set_image(file=file))
            
            # Log the successful operation
            headers.log_event('command_usage', 'rembg', ctx)
            headers.log_event('bot_response', ctx, attachment.filename)
    except Exception as error:
        # Send an error message to the user if something goes wrong
        await ctx.reply(embed=headers.req_failed(error))
        
        # Log the error

# Run the bot
bot.run(headers.get_credential('BOT_TOKEN'))    