import discord
from discord import Intents
from discord.ext import commands,tasks
from discord.ext.commands import Bot, CommandInvokeError, UserNotFound
from discord.utils import get

from discord_slash import SlashCommand, SlashContext
from discord_slash.utils.manage_commands import create_option
from discord_slash.utils import manage_components
from discord_slash.model import ButtonStyle

import datetime
from datetime import timezone, tzinfo, timedelta
import time as timeModule
import math
import random
import asyncio
import os
import sqlite3
import json
from urllib import request
from urllib.error import HTTPError

os.chdir(os.path.dirname(os.path.abspath(__file__)))

intents = discord.Intents(guilds=True, messages=True, reactions=True)

TOKEN = '<Here you have to put your token>'

client = commands.AutoShardedBot(command_prefix = ')', intents=intents, activity = discord.Game(name="/help"))
client.remove_command('help')
slash = SlashCommand(client, sync_commands = True)


##### ON READY EVENT #####

@client.event
async def on_ready():
    db = sqlite3.connect('smallgames.sqlite')
    cursor = db.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS connect4(
        user_id TEXT,
        VictoryCountConnect4 TEXT,
        LoseCountConnect4 TEXT
        )
    """)
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS tictactoe(
        user_id TEXT,
        VictoryCountTTT TEXT,
        LoseCountTTT TEXT
        )
    """)
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS shifumi(
        user_id TEXT,
        VictoryCountSFM TEXT,
        LoseCountSFM TEXT
        )
    """)
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS battleship(
        user_id TEXT,
        VictoryCountBTS TEXT,
        LoseCountBTS TEXT
        )
    """)
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS mgcoins(
        user_id TEXT,
        coins TEXT
        )
    """)
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS headsortails(
        user_id TEXT,
        VictoryCountHT TEXT,
        LoseCountHT TEXT
        )
    """)
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS topggvotes(
        user_id TEXT,
        timer TEXT,
        countnumber TEXT
        )
    """)
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS giveawaytable(
        user_id TEXT
        )
    """)
    print('=== Mini-Games Bot Online ===')


##### GUILD JOIN AND REMOVE #####


@client.event
async def on_command_error(ctx, error):
    return


for filename in os.listdir(f"./cogs"):
    if filename.endswith('.py'):
        client.load_extension(f"cogs.{filename[:-3]}")

client.run(TOKEN)
