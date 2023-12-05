# minecraftHelperBot

import os
import mariadb
import sys
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
# database params

database_params = {
    "user": os.getenv('USER'),
    "password": os.getenv('PASSWORD'),
    "host": os.getenv('HOST'),
    "database": os.getenv('DATABASE')
}

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

# converts overworld coords to nether coords
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

@bot.command(name='coordslist')
async def on_message(ctx):
    # generate embed object for display
    embed_object = discord.Embed(title="test title",
                                 description= "test description")
    await ctx.send(embed=embed_object)

@bot.command(name='addcoords')
async def on_message(ctx):
    print("add coords command triggered")

    # write the message to a variable
    message_content = ctx.message.content

    # define content to remove
    command = bot_prefix + 'addcoords '

    # remove command text for parsing
    coords_info = message_content.replace(command, '')
    # define function to check message format
    def check_string_format_coords(string):
        pattern = '-?\d+,-?\d+,-?\d+,.*'
        if re.match(pattern, string):
            return (True)

    if check_string_format_coords(coords_info):
        # convert string to list
        coords_info_list = coords_info.split(',')

        # Attempt connection
        try:
            conn = mariadb.connect(**database_params)
            print(f"Connected to DB. Inserting the following data:")
            print(coords_info_list)

            cursor = conn.cursor()

            # define sql for insertion
            sql = "INSERT INTO minecraftCoords (serverId, xCoord, yCoord, zCoord, description) VALUES (?,?,?,?,?)"
            data = (GUILD,coords_info_list[0],coords_info_list[1],coords_info_list[2],coords_info_list[3])

            cursor.execute(sql,data)
            conn.commit()
            print("Data inserted successfully.")

            # Close Connection
            cursor.close()
            conn.close()
            print("Connection closed.")

            await ctx.send("Your coordinates have been successfully saved! Please run mc.coordslist to see the updated list.")

        except mariadb.Error as e:
            print(f"Error connecting to the database: {e}")
            await ctx.send("There was a problem connecting to the database :(")

    else:
        await ctx.send("Please input in the format 'x, y, z, <description>'.")



bot.run(TOKEN)
