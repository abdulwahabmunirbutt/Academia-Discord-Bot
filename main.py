import discord
from keep_alive import keep_alive
from discord.ext import commands
import re
import requests
from bs4 import BeautifulSoup
from urllib.parse import unquote
from io import BytesIO
import asyncio

# Replace '1111525433662505000' with the desired channel ID
TARGET_CHANNEL_ID = 1172837110500302890

intents = discord.Intents.default()
intents.typing = False
intents.presences = False
intents.message_content = True

bot = commands.Bot(command_prefix='', intents=intents)  # No prefix

@bot.event
async def on_ready():
    print(f'We have logged in as {bot.user}')

@bot.event
async def on_message(message):
    if message.author == bot.user:
        return

    # Check if the message is sent to the target channel
    if message.channel.id != TARGET_CHANNEL_ID:
        return

    # Check if the message contains any URLs
    urls = re.findall(r'https?://[^\s]+', message.content)

    if not urls:
        return

    for url in urls:
        # Ensure the provided URL is from Academia
        if "www.academia.edu/" in url:
            try:
                response = requests.get(url)
                response.raise_for_status()
                soup = BeautifulSoup(response.content, 'html.parser')

                # Find the link starting with "https://www.academia.edu/attachments"
                download_link = soup.find('a', {'href': re.compile(r'^https://www.academia.edu/attachments')})

                # Check if the download link is found
                if download_link:
                    # Decode URL-encoded characters
                    decoded_link = unquote(download_link['href'])

                    # Extract the last part of the URL as the file name
                    file_name = decoded_link.split('/')[-1]

                    # Prepare the embed message
                    embed = discord.Embed(
                        title="Academia File Unlocked",
                        color=0x86ff00  # Customize the color here
                    )
                    embed.add_field(name="Question:", value=f"[Click here]({url})", inline=False)
                    embed.add_field(name="Answer:", value=f"[Click here]({decoded_link})", inline=False)
                    embed.set_footer(text="Powered by Abdul Wahab")  # Replace with your name
                    embed.set_thumbnail(url="https://cdn.discordapp.com/attachments/847880723289342003/847881117365567568/70a552e8e955049c8587b2d7606cd6a6.gif")  # Replace with your thumbnail URL
                    mention = message.author.mention

                    # Send the embed message with a mention
                    embed_message = await message.channel.send(content=mention, embed=embed)

                    # Introduce a delay before processing the download
                    await asyncio.sleep(2)

                    # Make a request to the decoded link
                    response = requests.get(decoded_link, stream=True)
                    response.raise_for_status()

                    # Prepare the file content
                    file_content = response.content

                    # Send the file back to the channel with the extracted file name
                    await message.channel.send(f"Here is your Academia file:", file=discord.File(file_content, filename=file_name))

                else:
                    raise Exception("Download link not found in the HTML source code.")

            except Exception as e:
                await message.channel.send(f"Error: {str(e)}")

    # Allow processing of commands after the event
    await bot.process_commands(message)

# Replace 'YOUR_BOT_TOKEN' with your actual bot token
keep_alive()
bot.run('MTE2NjYzNDMzNTY4NDc4ODMwNg.GSk7Wf.p9RyGn1PTPVec6yeCXk2q6_lY9XjUsP393i8Vc')
