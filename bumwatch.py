from dotenv import load_dotenv
import os
import sqlite3
import discord
from discord.ext import commands
from discord import app_commands
from league_methods import *
from enum import Enum


load_dotenv()

con = sqlite3.connect("database.db")
cur = con.cursor()

intents = discord.Intents.default()
intents.message_content = True
client = commands.Bot(command_prefix='/', intents=intents)

player = None
guild=discord.Object(id=971400515600658464)

class Region(Enum):
    America = "americas",
    Europe = "europe",
    Asia = "asia",
    SEA = "sea"

class Player():
    def __init__(self,discord, username,riot,region):
        self.discord = discord
        self.username = username
        self.riot = riot
        self.region = region


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
                                            "Select one member of the party to start tracking with /track, which can be checked with /log. Then after each game, a new episode of bumwatch will "
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
    if(player == None):
        await interaction.response.send_message("No player currently being tracked... Use /track to add them.")
    else:
        await interaction.response.send_message(f"Currently tracking {player.username}")

@client.tree.command(
    name="track",
    description="Adds player to be tracked",
    guild=guild
)
async def track(interaction:discord.Interaction, person: discord.Member):
    global player
    player = cur.execute("SELECT * FROM players WHERE discord = ?", (person.id,)).fetchone()
    if (player == None):
        await interaction.response.send_message(f"Player {person.display_name} is not registered. Use /register to register them.")
    else:
        player = Player(player[0], player[1], player[2], player[3])
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
        riotID = search_riot_id(league_user, region.value[0])
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
async def logDB(ctx):
    res = cur.execute("SELECT * from players")
    print(res.fetchall())

client.run(os.getenv("DISCORD_BOT_TOKEN"))
