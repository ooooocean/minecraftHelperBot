# minecraftHelperBot

import os
import re
import json
import random

# this loads the discord library
import discord
from dotenv import load_dotenv
from discord.ext import commands
from discord.ext.commands import Bot


# import numpy for arrays
import numpy as np

# import csv for reading/writing to temporary DB
from csv import writer

# import datetime for date updates
from datetime import datetime, timedelta
from datetime import timezone

# import re package to make data parsing easier
import re

# importing pandas for csv manipulation
import pandas as pd

# import time module for sleeps
import time

# this loads async
import asyncio

# math
import math

load_dotenv()
TOKEN = os.getenv('DISCORD_TOKEN')
GUILD = os.getenv('DISCORD_GUILD')

# allows for bot to detect all members belonging to the server.
intents = discord.Intents.default()
intents.members = True
intents.reactions = True
intents.messages = True

# Client is an object that represents a connection to Discord.
# This handles events, tracks state and interacts with discord APIs
client = discord.Client(intents=intents)
bot_prefix = 'mc.'
bot = commands.Bot(command_prefix=bot_prefix.lower(), intents=intents)

# get the server
localServer = discord.utils.get(client.guilds, id=GUILD)

@bot.event
async def on_ready():
    print(f'Logged in as {bot.user} (ID: {bot.user.id})')
    print('------')

@bot.command()
async def test(ctx):
    await ctx.send('test passed')

# Displays list of coords from saved csv
@bot.command()
async def coords(ctx):
    await ctx.send("Displaying list of coords.")



@bot.command(name='convert')
async def on_message(ctx):
    # define function to check coords
    def check_string_format_coords(string):
        pattern = '-?\d+,-?\d+,-?\d+'
        if re.match(pattern, string):
            return (True)

    print("coords command triggered")

    # write the message to a variable
    message_content = ctx.message.content

    # define content to remove
    command = bot_prefix + 'convert '

    # remove command text for parsing
    overworld_coords_text = message_content.replace(command,'')
    overworld_coords_text = overworld_coords_text.replace(" ","")
    print(overworld_coords_text)
    # check if coords are in the right format
    if check_string_format_coords(overworld_coords_text):
        # convert coords to list
        overworld_coords = overworld_coords_text.split(',')
        overworld_coords = map(int, overworld_coords)
        # iterate through list and assign to new variable
        nether_coords = []
        for num in overworld_coords:
            c = int(num/8)
            nether_coords.append(c)
        nether_coords = map(str, nether_coords)
        nether_coords_text = ', '.join(nether_coords)
        await ctx.send("Nether coords are:\n" + nether_coords_text)
    else:
        await ctx.send("Wrong co-ordinate format. Please enter coords in the format 'x, y, z'.")



bot.run(TOKEN)
