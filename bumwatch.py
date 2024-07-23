from dotenv import load_dotenv
import os
import sqlite3
import discord
from discord.ext import commands
from discord import app_commands
from league_methods import *


load_dotenv()

con = sqlite3.connect("database.db")
cur = con.cursor()

intents = discord.Intents.default()
intents.message_content = True
intents.guilds=True
intents.messages=True
client = commands.Bot(command_prefix='/', intents=intents)

guild = discord.Object(id=os.getenv("GUILD_ID"))


@client.event
async def on_guild_join(guild):
    await client.tree.sync(guild=guild)
    try:
        cur.execute("INSERT INTO guilds VALUES (?, ?, ?, ?)", (guild.id, None, None, None))
        con.commit()
    except Exception as e:
        print(e)

@client.event
async def on_guild_remove(guild):
    cur.execute("DELETE FROM guilds WHERE gid = ?", (guild.id,))

@client.event
async def on_ready():
    await client.tree.sync(guild=guild)
    print(f'We have logged in as {client.user}')

@client.tree.command(
    name="help",
    description="Show information about the bot",
    guild=guild
)
async def help(interaction:discord.Interaction):
    await interaction.response.send_message("Welcome to the next season of bumwatch! All participants use /register with their riot username and region. You can unregister with /unregister. "
                                            "Select one member of the party to start tracking with /track, which can be checked with /log. Start tracking using /start. Then after each game, a new episode of bumwatch will "
                                            "be aired, starring the players who performed the least that game.", ephemeral=True)

@client.tree.command(
    name="ping",
    description="testing",
    guild=guild
)
async def ping(interaction:discord.Interaction, member: discord.Member):
    await interaction.response.send_message(f"@{member.global_name}", ephemeral=False)
   
@client.tree.command(
    name="log",
    description="Logs current player being tracked",
    guild=guild

)
async def log(interaction:discord.Interaction):
    player = cur.execute("SELECT * FROM guilds WHERE gid = ?", (interaction.guild_id,)).fetchone()
    if(player == None):
        await interaction.response.send_message("No player currently being tracked... Use /track to add them.")
    else:
        await interaction.response.send_message(f"Currently tracking {player[2]}")

@client.tree.command(
    name="track",
    description="Adds player to be tracked",
        guild=guild
)
async def track(interaction:discord.Interaction, person: discord.Member):
    player = cur.execute("SELECT * FROM players WHERE discord = ?", (person.id,)).fetchone()
    if (player == None):
        await interaction.response.send_message(f"Player {person.display_name} is not registered. Use /register to register them.")
    else:
        cur.execute("INSERT INTO guilds VALUES (?,?,?,?) ON CONFLICT (gid) DO UPDATE SET pid = excluded.pid, region = excluded.region, player = excluded.player", (interaction.guild_id, player[2], player[3], person.display_name))
        # GID, PID, REGION, PLAYER
        con.commit()
        await interaction.response.send_message(f"Currently tracking {person.display_name}")

    
@client.tree.command(
        name="register",
        description="Register your riot account",
            guild=guild
)
@app_commands.describe(league_user="Username#Tagline")
@app_commands.rename(league_user="riot_id")
async def register(interaction: discord.Interaction, league_user: str, region: Region):
    try:
        riotID = search_riot_id(league_user)
        cur.execute("INSERT INTO players VALUES (?, ?, ?, ?) ON CONFLICT (discord) DO UPDATE SET riot = excluded.riot, region = excluded.region", (interaction.user.id, interaction.user.global_name, riotID, region.value[0]))
        con.commit()
        await interaction.response.send_message("Registered!", ephemeral=True)
    except Exception as e:
        await interaction.response.send_message("Unable to find player, make sure the entered Username#Tagline is correct!", ephemeral=True)
        print(e)


@client.tree.command(
    name="unregister",
    description="Unregister your riot account",
        guild=guild

)
async def unregister(interaction:discord.Interaction):
    cur.execute("DELETE FROM players WHERE discord = ?", (interaction.user.id,))
    con.commit()
    await interaction.response.send_message("Unregistered!", ephemeral=True)

@client.tree.command(
    name="logdb",
        guild=guild

)
async def logDB(interaction: discord.Interaction):
    res = cur.execute("SELECT * from players")
    print(res.fetchall())
    res = cur.execute("SELECT * from guilds")
    print(res.fetchall())
    await interaction.response.defer()

@client.tree.command(
    name="start",
    description="Start tracking games",
    guild=guild
)
async def startTracking(interaction: discord.Interaction):
    await interaction.response.send_message("Tracking started!")
    player = cur.execute("SELECT * FROM guilds WHERE gid = ?", (interaction.guild_id,)).fetchone()
    print("Started following player " + str(player[3]))
    while True:
        # print(player)
        message = await game_loop(player[1], player[2])
        if(not message):
            return
        if('prev_message' in locals()):
            await prev_message.delete()
        prev_message = await interaction.channel.send(message)

@client.tree.command(
        name="last_game",
        description="Show last game",
        guild=guild
)
async def lastGame(interaction: discord.Interaction):
    await interaction.response.defer()
    player = cur.execute("SELECT * FROM guilds WHERE gid = ?", (interaction.guild_id,)).fetchone()
    message = await last_game(player[1], player[2])
    await interaction.channel.send(message)

@client.tree.command(
        name="clear",
        description="Clear bumwatch channel",
        guild=guild
)
async def clear(interaction: discord.Interaction):
    channel = interaction.channel
    await interaction.response.defer()
    await channel.purge(limit=None)

client.run(os.getenv("DISCORD_BOT_TOKEN"))
