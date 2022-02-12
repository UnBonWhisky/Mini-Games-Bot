import discord
import asyncio
from discord.ext.commands import Bot, CommandNotFound
from discord.ext import commands, tasks

from discord_slash import cog_ext, SlashContext, ComponentContext

import datetime
from datetime import timezone, tzinfo, timedelta
import time
from discord.utils import get
import logging
import os
import sqlite3

class invitecommand(commands.Cog):
    def __init__(self, client):
        self.client = client

    @cog_ext.cog_slash(name = "invite", description = "Anything you need to know if you want me on your server")
    async def invite(self, ctx : SlashContext):

        #creator = self.client.get_user(341257685901246466)
        botuser = self.client.get_user(781280845042155530)

        embed = discord.Embed(title="Join author's server here",
                              url='https://discord.gg/gqfFqJp',
                              description="For management, ideas I can code and others things to have a better bot",
                              colour = discord.Colour.purple()
                              )
        embed.set_footer(icon_url = f"https://cdn.discordapp.com/avatars/341257685901246466/a_09dadd494a375adaced572682c8ec96c.png?size=4096",
                         text = f"JeSuisUnBonWhisky#0001")
        embed.set_author (name = f"{botuser}",
                          icon_url = f'{botuser.avatar_url}')
        embed.add_field(name = "Add me to your server",
                        value = "[Click here to invite me \non your server](https://discord.com/api/oauth2/authorize?client_id=781280845042155530&permissions=105495587952&scope=bot%20applications.commands)",
                        inline = True)
        embed.add_field(name = "Vote me please",
                        value = "[You can vote me up on top.gg by \nclicking on this link](https://top.gg/bot/781280845042155530/vote)",
                        inline = True)
    
        await ctx.send(embed = embed, hidden=True)
    
def setup(client):
    client.add_cog(invitecommand(client))
    print("Invite command cog ready !")
