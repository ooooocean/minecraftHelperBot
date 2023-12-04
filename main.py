# minecraftHelperBot

import os
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

bot.run(TOKEN)
