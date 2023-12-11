# minecraftHelperBot
"""A Discord bot that provides a variety of functions to improve QoL when playing Minecraft."""
# adding text to test for Jenkins build
import os
import time
import math
import re
import mariadb
import discord
from discord.ext import commands
from dotenv import load_dotenv
import matplotlib.pyplot as plt

load_dotenv()
TOKEN = os.getenv('DISCORD_TOKEN')
GUILD = os.getenv('DISCORD_GUILD')
database_params = {
    "user": os.getenv('USER'),
    "password": os.getenv('PASSWORD'),
    "host": os.getenv('HOST'),
    "database": os.getenv('DATABASE')
}

# get root dir
ROOT_DIR = os.path.dirname(
    os.path.abspath(__file__)
)
print(os.path.abspath('.'))

# allows for bot to detect all members belonging to the server.
intents = discord.Intents.all()
intents.members = True
intents.reactions = True
intents.messages = True

# Client is an object that represents a connection to Discord.
# This handles events, tracks state and interacts with discord APIs
client = discord.Client(intents=intents)
BOT_PREFIX = 'mc.'
bot = commands.Bot(command_prefix=BOT_PREFIX.lower(), intents=intents)

# get the server
localServer = discord.utils.get(client.guilds, id=GUILD)

# define function to check coords
def check_string_format_coords(string):
    """Checks a string to see if it is in the format x, y, z."""
    pattern = r'-?\d+,-?\d+,-?\d+'
    if re.match(pattern, string):
        return True
    return False


# define function to get data from database
def get_data_from_database():
    """Gets all information from the coordinates DB."""
    print("Initating connection to database.")
    try:
        conn = mariadb.connect(**database_params)
        print("Connected to database.")

        sql = "SELECT id, xCoord, yCoord, zCoord, description " \
              "FROM minecraftCoords " \
              "WHERE serverId=? " \
              "ORDER BY id ASC"

        cursor = conn.cursor()
        # execute SQL query with given parameters
        cursor.execute(sql, (GUILD,))

        query_results = []
        for item in cursor:
            query_results.append(item)

    except mariadb.Error as e:
        print(f"Error connecting to the database: {e}")

    return query_results

def generate_map(x_coords, z_coords, labels, filename):
    """Generates map for given coordinates and labels, saving them into a file."""
    print("Triggered map generation function.")
    # generate plot
    fig = plt
    fig.scatter(list(x_coords),
                list(z_coords),
                marker='+')

    # add point markers
    for i, item in enumerate(labels):
        plt.annotate(item, (x_coords[i], z_coords[i]))

    # add origin axes
    fig.axhline(0, color='black', linewidth=.2)
    fig.axvline(0, color='black', linewidth=.2)
    # add axes labels
    fig.xlabel("x")
    fig.ylabel("z", rotation=0)
    # add ticks
    fig.tick_params(axis='both',
                    which='both',
                    bottom=True,
                    top=True,
                    left=True,
                    right=True,
                    direction='in')

    print("Final plot completed.")

    fig.savefig(filename)
    print("Saving file.\n")
    return fig

@bot.event
async def on_ready():
    """Prints a ready message in the terminal upon connection."""
    print(f'Logged in as {bot.user} (ID: {bot.user.id})')
    print('------')


# converts overworld coords to nether coords
@bot.command(name='convert', description="Converts overworld coordinates to Nether coordinates.")
async def on_message(ctx):
    """Function that takes coordinates in the format x, y, z
    and divides them by 8 to obtain Nether coordinates."""

    print("Coordinate convert command triggered.")

    # write the message to a variable
    message_content = ctx.message.content

    # define content to remove
    command = BOT_PREFIX + 'convert '

    # remove command text for parsing
    overworld_coords_text = message_content.replace(command, '')
    overworld_coords_text = overworld_coords_text.replace(" ", "")
    # check if coords are in the right format
    if check_string_format_coords(overworld_coords_text):
        # convert coords to list
        overworld_coords = overworld_coords_text.split(',')
        overworld_coords = map(int, overworld_coords)
        # iterate through list and assign to new variable
        nether_coords = []
        for num in overworld_coords:
            c = int(num / 8)
            nether_coords.append(c)
        nether_coords = map(str, nether_coords)
        nether_coords_text = ', '.join(nether_coords)
        await ctx.send("Nether coords are:\n" + nether_coords_text)
        print(f"Success - converted overworld coords {overworld_coords_text} "
              f"to nether coords {nether_coords_text}.")
        print("-----")
    else:
        await ctx.send("Wrong co-ordinate format. Please enter coords in the format 'x, y, z'.")

@bot.command(name='coordsfind')
async def on_message(ctx): # pylint: disable=function-redefined
    """Takes in a set of coordinates and finds the closest location """
    print("Locate closest location command triggered.")

    # define content to remove
    command = BOT_PREFIX + 'coordsfind '

    # remove command text for parsing
    overworld_coords_text = ctx.message.content.replace(command, '')
    overworld_coords_text = overworld_coords_text.replace(" ", "")

    # check if coords are in the right format
    if check_string_format_coords(overworld_coords_text):
        # convert coords to list
        overworld_coords = overworld_coords_text.split(',')
        overworld_coords = list(map(int, overworld_coords))

        # extract data from database
        data = get_data_from_database()
        distance_list = []
        for item in data:
            coords = ', '.join(([str(item[1]), str(item[2]), str(item[3])]))
            distance_list.append([item[0],
                                  coords,
                                  item[4],
                                  math.dist((overworld_coords[0], overworld_coords[2]),
                                            (item[1], item[3]))])

        distance_list.sort(key = lambda row: row[3])

        # generate embed for sorted list

        embed_object = discord.Embed(title="Coordinates List (sorted by distance desc.)",
                                     description='meep morp')
        embed_object.add_field(name='ID',
                               value='\n'.join([str(x[0]) for x in distance_list]),
                               inline=True)
        embed_object.add_field(name="Description",
                               value='\n'.join(str(x[2]) for x in distance_list),
                               inline=True)
        embed_object.add_field(name="Coords",
                               value='\n'.join(str(x[1]) for x in distance_list),
                               inline=True)

        # insert user location into data list
        data.insert(0, ('',
                        overworld_coords[0],
                        overworld_coords[1],
                        overworld_coords[2],
                        "YOU"))

        filename = 'sortedmap.png'
        fig = generate_map([row[1] for row in data],
                     [row[3] for row in data],
                     [row[4] for row in data],
                     filename)

        plot_dir = os.path.join(ROOT_DIR, filename)

        # generate map for display in embed
        embed_map = discord.File(plot_dir, filename=filename)
        embed_object.set_image(url="attachment://" + filename)

        # remove the inserted element
        del data[0]
        fig.close()

        # Return the message object
        await ctx.send(embed=embed_object,
                       file = embed_map)

        os.remove(filename)
        print("Map deleted.\n------")

    else:
        await ctx.send("Wrong co-ordinate format. Please enter coords in the format 'x, y, z'.")

@bot.command(name='coordslist', description="Lists saved coordinates.")
async def on_message(ctx):  # pylint: disable=function-redefined
    """Lists saved coordinates by pulling from database and generates a map with the coordinates."""
    print("List coordinates command triggered.")
    # get data from database
    data = get_data_from_database()

    filename = 'map.png'

    # generate map from extracted data
    generate_map([row[1] for row in data],
                 [row[3] for row in data],
                 [row[4] for row in data],
                 filename)

    # define plot directory
    plot_dir = os.path.join(ROOT_DIR, filename)

    # check if file does not exist and if so, wait until it does
    if os.path.exists(plot_dir) is False:
        print("File has not been generated, waiting for file to generate.")
        while os.path.exists(plot_dir) is False:
            time.sleep(0.1)

    embed_object = discord.Embed(title="Coordinates List",
                                 description='meep')

    # generate map for display in embed
    embed_map = discord.File(plot_dir, filename=filename)
    embed_object.set_image(url="attachment://" + filename)

    embed_object.add_field(name='ID',
                           value='\n'.join([str(x[0]) for x in data]),
                           inline=True)
    embed_object.add_field(name="Description",
                           value='\n'.join(str(x[2]) for x in data),
                           inline=True)
    embed_object.add_field(name="Coords",
                           value='\n'.join(str(x[1]) for x in data),
                           inline=True)
    embed_object.set_image(url="attachment://" + filename)

    # Return the message object
    await ctx.send(embed=embed_object,
                   file=embed_map)
    print("Message sent with list of coordinates")

    os.remove(filename)
    print("Map deleted.\n------")

@bot.command(name='coordsadd', description="Adds coordinates in the format x,y,z,<description>.")
async def on_message(ctx):  # pylint: disable=function-redefined
    """Takes coordinates in the format x, y, z, <description> and saves it to the database."""
    # write the message to a variable
    message_content = ctx.message.content

    # define content to remove
    command = BOT_PREFIX + 'coordsadd '

    # remove command text for parsing
    coords_info = message_content.replace(command, '')

    if check_string_format_coords(coords_info):
        # convert string to list
        coords_info_list = coords_info.split(',')
        coords_info_list[3] = coords_info_list[3].strip()

        # Attempt connection
        try:
            conn = mariadb.connect(**database_params)
            print("Connected to DB. Inserting the following data:")
            print(coords_info_list)

            cursor = conn.cursor()

            # define sql for insertion
            sql = "INSERT INTO minecraftCoords " \
                  "(serverId, xCoord, yCoord, zCoord, description) " \
                  "VALUES (?,?,?,?,?)"
            data = (GUILD, coords_info_list[0], coords_info_list[1],
                    coords_info_list[2], coords_info_list[3])

            cursor.execute(sql, data)
            conn.commit()
            print("Data inserted successfully.")

            # Close Connection
            cursor.close()
            conn.close()
            print("Connection closed.")

            await ctx.send("Your coordinates have been successfully saved! "
                           "Please run mc.coordslist to see the updated list.")

        except mariadb.Error as e:
            print(f"Error connecting to the database: {e}")
            await ctx.send("There was a problem connecting to the database :(")

    else:
        await ctx.send("Please input in the format 'x, y, z, <description>'.")

@bot.command(name='coordsdelete', description="Removes coordinates from the list"
                                              " by specifying the ID.")
async def on_message(ctx):  # pylint: disable=function-redefined
    """Function that takes in an ID from the coordinate list and deletes it from the database."""
    print('Delete coordinates function triggered.')
    # write the message to a variable
    message_content = ctx.message.content

    # define content to remove
    command = BOT_PREFIX + 'coordsdelete '

    # remove command text for parsing
    coords_id = message_content.replace(command, '')
    coords_id = coords_id.strip()

    # define function to check message format
    def check_string_format_coords_id(string):
        pattern = r'\d*'
        if re.match(pattern, string):
            return True
        return False

    if check_string_format_coords_id(coords_id):
        # Attempt connection
        try:
            conn = mariadb.connect(**database_params)
            print("Connected to DB. Inserting the following data:")

            cursor = conn.cursor()

            # define sql for insertion
            sql = "DELETE FROM minecraftCoords WHERE id=?"
            data = (coords_id,)

            cursor.execute(sql, data)
            conn.commit()
            print("Data deleted successfully.")

            # Close Connection
            cursor.close()
            conn.close()
            print("Connection closed.")

            await ctx.send(
                "Your coordinates have been successfully deleted! "
                "Please run mc.coordslist to see the updated list.")
            print('----')

        except mariadb.Error as e:
            print(f"Error connecting to the database: {e}")
            await ctx.send("There was a problem connecting to the database :(")

    else:
        await ctx.send("Please input in the format 'mc.coordsdelete <id>'.")


bot.run(TOKEN)
