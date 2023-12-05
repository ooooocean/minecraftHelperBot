# minecraftHelperBot

import os
import mariadb
import discord
from dotenv import load_dotenv
from discord.ext import commands


# import re package to make data parsing easier
import re


load_dotenv()
TOKEN = os.getenv('DISCORD_TOKEN')
GUILD = os.getenv('DISCORD_GUILD')
database_params = {
    "user": os.getenv('USER'),
    "password": os.getenv('PASSWORD'),
    "host": os.getenv('HOST'),
    "database": os.getenv('DATABASE')
}

# allows for bot to detect all members belonging to the server.
intents = discord.Intents.all()
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

# converts overworld coords to nether coords
@bot.command(name='convert', description="Converts overworld coordinates to Nether coordinates.")
async def on_message(ctx):
    # define function to check coords
    def check_string_format_coords(string):
        pattern = '-?\d+,-?\d+,-?\d+'
        if re.match(pattern, string):
            return (True)

    print("Coordinate convert command triggered.")

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
        print(f"Success - converted overworld coords {overworld_coords_text} to nether coords {nether_coords_text}.")
        print("-----")
    else:
        await ctx.send("Wrong co-ordinate format. Please enter coords in the format 'x, y, z'.")

@bot.command(name='listcoords', description="Lists saved coordinates.")
async def on_message(ctx):
    print("List coordinates command triggered.")
    # connect to DB
    try:
        conn = mariadb.connect(**database_params)
        print(f"Connected to DB.")

        cursor = conn.cursor()

        # define sql for insertion
        sql = "SELECT id, xCoord, yCoord, zCoord, description FROM minecraftCoords WHERE serverId=? ORDER BY id ASC"
        data = (GUILD,)

        cursor.execute(sql, data)

        conn.commit()
        # assemble embed fields
        coords_embed_list = []
        description_embed_list = []
        id_list = []
        for item in cursor:
            coords_embed_list.append(str(item[1]) + ', ' + str(item[2]) + ', ' + str(item[3]))
            description_embed_list.append(item[4])
            id_list.append(item[0])
        print("Data obtained successfully.")

        # Close Connection
        cursor.close()
        conn.close()
        print("Connection closed.")

    except mariadb.Error as e:
        print(f"Error connecting to the database: {e}")
        await ctx.send("There was a problem connecting to the database :(")

    # generate embed object for display
    embed_object = discord.Embed(title="Coordinates List",
                                 description="this looks kind of boring...ping any suggestions over OWO")
    embed_object.add_field(name="Description",
                           value='\n'.join(description_embed_list),
                           inline=True)
    embed_object.add_field(name="Coords",
                           value='\n'.join(coords_embed_list),
                           inline=True)

    embed_object.set_thumbnail(url="https://images-wixmp-ed30a86b8c4ca887773594c2.wixmp.com/f/7c15a5ea-0f0a-4641-a73b-f504324da8ed/d4v2t3p-5bca9982-2e12-49bd-b821-d17e226b94ab.png/v1/fill/w_900,h_506,q_75,strp/minecraft_map_by_theswedishswede-d4v2t3p.png?token=eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJpc3MiOiJ1cm46YXBwOjdlMGQxODg5ODIyNjQzNzNhNWYwZDQxNWVhMGQyNmUwIiwic3ViIjoidXJuOmFwcDo3ZTBkMTg4OTgyMjY0MzczYTVmMGQ0MTVlYTBkMjZlMCIsImF1ZCI6WyJ1cm46c2VydmljZTppbWFnZS5vcGVyYXRpb25zIl0sIm9iaiI6W1t7InBhdGgiOiIvZi83YzE1YTVlYS0wZjBhLTQ2NDEtYTczYi1mNTA0MzI0ZGE4ZWQvZDR2MnQzcC01YmNhOTk4Mi0yZTEyLTQ5YmQtYjgyMS1kMTdlMjI2Yjk0YWIucG5nIiwid2lkdGgiOiI8PTkwMCIsImhlaWdodCI6Ijw9NTA2In1dXX0.pRk4hg347bq3tYPDGl76EuZixO5JTr_6_PG0V8vrZ64")
    await ctx.send(embed=embed_object)

@bot.command(name='addcoords', description="Adds coordinates in the format x,y,z,<description>.")
async def on_message(ctx):
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
        coords_info_list[3] = coords_info_list[3].strip()

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