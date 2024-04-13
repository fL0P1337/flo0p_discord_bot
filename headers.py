import datetime
import shutil
import os
from datetime import datetime
import disnake
time = datetime.now()
def get_bot_token():
     txt = open("token.txt",)
     return txt.read()
def help_msg(): # !help message content
    help_msg = disnake.Embed(
    title = "Welcome! Theres a list of available functions:",
    description ="!rembg - remove background from any photos using AI\n"
                #"!imgtotxt - extract text from image, supports Russian and English languages"
                "/chatgpt [your_prompt] - chatGPT will write whatever you ask!\n"
                "/gtts [language: ru, en, fr, pt, es] [your_message] - Google text to speach will convert your message to speach!\n"
                "/ytmp3 [youtube_link] - Convert YouTube video into mp3!\n"
                "/credits - Will show you credits like used libs and author of this bot\n"
                "/randomcat - Use this to receive random cat image \n"
                "/randomcatgif - Use this to receive random cat gif \n",
    colour = 0xF0C43F,
    timestamp = datetime.now(),
    )
    return help_msg
def credits_msg(): # /credits message content
    credit_msg = disnake.Embed(
        title="Credits!",
        description="Used libraries: disnake, pytube, g4f, nest_asyncio, gtts, rembg\n"
                    "Made by: flo0p1337",
        colour=0xF0C43F,
        timestamp=datetime.now(),
    )
    return credit_msg
def req_claim(): # embed for request claim message
    req_claim = disnake.Embed(
        title="Your request is being processed!",
        description="Wait a response, you will be notified when the process is complete....",
        colour=0xF0C43F,
        timestamp=datetime.now(),
    )
    return req_claim
def req_failed(error): # embed for exceptions
        req_failed = disnake.Embed(
        title="There's been an error! Try re-posting your request.\n"
              "Error code: ",
        description=error,
        colour=0xF0C43F,
        timestamp=datetime.now(),
            )
        return req_failed
def req_done (description): # embed for done requests
        req_done = disnake.Embed(
        title="Your answer is ready!",
        description=description,
        colour=0xF0C43F,
        timestamp=datetime.now(),
)
        return req_done
def logger(used_command, username, used_prompt, got_response): # logger function
    with open('logs/logsDS.txt', 'a') as f:
        log_msg = ['\n' +
                     str("[USER_CMD] ") + str(
            time) + ": " + str(
            username) + f" used {used_command} with prompt -> {used_prompt} and got the reponse -> {got_response}"]
        with open('logs/logsDS.txt', 'a') as f:
            f.write('\n'.join(log_msg))
        print(log_msg.pop(0))
def cleaner(): # cleaner function
    dirs_path = ["files/rembg","files/gtts","files/ytmp3"]
    for folder in dirs_path:
        for filename in os.listdir(folder):
            file_path = os.path.join(folder, filename)
            try:
                if os.path.isfile(file_path) or os.path.islink(file_path):
                    os.unlink(file_path)
                elif os.path.isdir(file_path):
                    shutil.rmtree(file_path)
            except Exception as e:
                print(f'Failed to delete {file_path}. Reason: {e}')
