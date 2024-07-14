from dotenv import load_dotenv
import os
import sqlite3
import discord
from discord.ext import commands

load_dotenv()

con = sqlite3.connect("database.db")
cur = con.cursor()

intents = discord.Intents.default()
intents.message_content = True

client = commands.Bot(command_prefix='/', intents=intents)

player = False

@client.event
async def on_ready():
    print(f'We have logged in as {client.user}')

@client.command()
async def ping(ctx, members: commands.Greedy[discord.Member]):
    for member in members:
        await ctx.send(member.global_name)

@client.command()
async def log(ctx):
    if(not player):
        await ctx.send("No player currently being tracked... Use /track to add them.")
    else:
        await ctx.send(f"Currently tracking {player}")

@client.command()
async def track(ctx, username):
    player = username
    await ctx.send(f"Currently tracking {player}")
    
@client.command()
async def register(ctx, discordUser, leagueId):
    cur.execute("INSERT INTO players VALUES ? ?", discordUser, leagueId)
    con.commit()

@client.command()
async def logDB(ctx):
    res = cur.execute("SELECT * from players")
    print(res.fetchall())

client.run(os.getenv("DISCORD_BOT_TOKEN"))
