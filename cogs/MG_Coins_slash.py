import discord
from discord import Intents
from discord.ext import commands,tasks
from discord.ext.commands import Bot, CommandInvokeError, UserNotFound, CommandOnCooldown
from discord.utils import get

from discord_slash import cog_ext, SlashContext, ComponentContext

from datetime import timezone, tzinfo, timedelta
import time
import math
import random
import asyncio
import os
import sqlite3

db = sqlite3.connect("smallgames.sqlite") # Ouverture de la base de données
cursor = db.cursor()

class MGCoins(commands.Cog):
    def __init__(self, client):
        self.client = client

    @cog_ext.cog_slash(name = "mgcoins", description = "Type this command to redeem your 5 MG Coins (1 time for 12h)")
    async def mgcoins(self, ctx):

        cursor.execute(f"SELECT coins FROM mgcoins WHERE user_id = {ctx.author.id}")
        ProfileCoins = cursor.fetchone() # On récupère les infos de son argent si elles existent

        if ProfileCoins is None : # si le joueur n'a pas de "porte feuille"

            defaultnumbercoins = 100
                
            sql = ("INSERT INTO mgcoins(user_id, coins) VALUES(?,?)")
            val = (ctx.author.id, defaultnumbercoins)
            cursor.execute(sql, val)
            db.commit()

        EmbedAjoutCoins = discord.Embed(title = "Want more MG Coins ?",
                                        description = f"<@{ctx.author.id}> if you want more mgcoins, you have to vote for me on Top.gg\n[You can click here to see the vote page and redeem your 5 MG Coins](https://top.gg/bot/781280845042155530/vote)\nThis can be done all 12 hours.",
                                        colour = discord.Colour.purple())
        EmbedAjoutCoins.set_footer(text = f"Made by JeSuisUnBonWhisky#0001")

        cursor.execute(f"SELECT timer FROM topggvotes WHERE user_id = {ctx.author.id}")
        AlreadyVoted = cursor.fetchone() # On récupère les infos de son argent si elles existent

        timestamp = int(time.time())

        if (AlreadyVoted is None) or (AlreadyVoted == []) :

            EmbedAjoutCoins.add_field(name = "No Cooldown",
                                    value = "You are not in cooldown for now. If you are, I am gonna tell it here before the next vote",
                                    inline = False)
        
        else:

            lasttime = int(AlreadyVoted[0])
            
            if (timestamp - 43200) > lasttime :

                EmbedAjoutCoins.add_field(name = "No Cooldown",
                                        value = "You are not in cooldown for now. If you are, I am gonna tell it here before the next vote",
                                        inline = False)
            
            else :

                hours = 0
                minutes = 0
                seconds = 43200 - (timestamp - lasttime)

                while seconds >= 60:
                    minutes += 1
                    seconds -= 60
                    if minutes >= 60:
                        minutes -= 60
                        hours += 1

                EmbedAjoutCoins.add_field(name = "You are in Cooldown",
                                        value = f"You are actually in cooldown. You will be able to vote the next time in :\n{hours} hours, {minutes} minutes, and {seconds} seconds.",
                                        inline = False)
        
        await ctx.send(embed = EmbedAjoutCoins, hidden=True)


def setup(client):
    client.add_cog(MGCoins(client))
    print("Mini Games Coins command cog ready !")