import discord
from discord import Intents
from discord.ext import commands,tasks
from discord.ext.commands import Bot
from discord.utils import get

from discord_slash import cog_ext, SlashContext, ComponentContext

from datetime import timezone, tzinfo, timedelta
import sqlite3
import random
import asyncio
import os

class DonationCommand(commands.Cog):
    def __init__(self, client):
        self.client = client

    @cog_ext.cog_slash(name = "donation", description = "If you want to thank me for my work :)")
    async def donation(self, ctx : SlashContext):

        EmbedDonation = discord.Embed(title = "Wanna support me ?",
                                    description = "it would help me a lot if you have the possibility to donate to me :\nOne time with [Buy me a coffee](https://www.buymeacoffee.com/UnBonWhisky)\nEach month with [Patreon](https://www.patreon.com/JeSuisUnBonWhisky)\n\nMy goal would be to earn a total of 120 € to have new stuff to host my bots\nThank you in advance,\nJeSuisUnBonWhisky#0001",
                                    colour = discord.Colour.gold())
        
        await ctx.send(embed = EmbedDonation, hidden=True)


def setup(client):
    client.add_cog(DonationCommand(client))
    print("Donation Command cog ready !")