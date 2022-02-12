import discord
from discord import Intents
from discord.ext import commands,tasks
from discord.ext.commands import Bot, CommandInvokeError, UserNotFound
from discord.utils import get

from discord_slash import cog_ext, SlashContext, ComponentContext
from discord_slash.utils.manage_commands import create_option
from discord_slash.utils import manage_components
from discord_slash.utils.manage_components import create_button, create_actionrow
from discord_slash.model import ButtonStyle

from datetime import timezone, tzinfo, timedelta
import time as timeModule
import math
import random
import asyncio
import os
import unicodedata

def get_index_positions(list_of_elems, element):
    index_pos_list = []
    index_pos = 0
    while True:
        try:
            index_pos = list_of_elems.index(element, index_pos)
            index_pos_list.append(index_pos)
            index_pos += 1
        except ValueError as e:
            break
    return index_pos_list

class HungManCommand(commands.Cog):
    def __init__(self, client):
        self.client = client

    
    @cog_ext.cog_slash(name = "hangman", description = "Play Hangman with up to 9 friends")
    async def hangman(self, ctx : SlashContext):

        StartGameButtons = [
            create_button(
                style=ButtonStyle.blue,
                emoji="🎰",
                custom_id="addplayer",
                disabled=False
            ),
            create_button(
                style=ButtonStyle.blue,
                emoji="✅",
                custom_id="start",
                disabled=True
            )
        ]

        StartGameRow = create_actionrow(*StartGameButtons)

        authorofgame = ctx.author

        playerlist = [authorofgame.id]

        EmbedStartGame = discord.Embed(title="Hangman game !",
                                    description = f"You want to play a game of hangman !\nOthers players have to react to this message with 🎰 to join the game\nYou can play between 2 and 10 players\n\nWord chooser :\n<@{playerlist[0]}>",
                                    colour = discord.Colour.blurple())

        MessageStartGame = await ctx.send(embed = EmbedStartGame, components=[StartGameRow])

        await asyncio.sleep(0.1)

        def CheckAjoutAutresPlayer(ctx: ComponentContext):
            return ctx.custom_id == "addplayer"
            
        def CheckFinListeJoueurs(ctx: ComponentContext):
            return ctx.custom_id == "start"

        done, pending = await asyncio.wait([
            manage_components.wait_for_component(self.client, messages=MessageStartGame, components=StartGameRow, check = CheckAjoutAutresPlayer, timeout=10.0)
        ], return_when=asyncio.FIRST_COMPLETED)

        try:
            stuff = done.pop().result()
        except asyncio.TimeoutError:
            EmbedNobody = discord.Embed(description = "Nobody want to play with you. Try again a future time",
                                        colour = discord.Colour.red())
            
            await MessageStartGame.edit(embed = EmbedNobody, components=[])
            return

        for future in done:
            future.exception()
        
        for future in pending:
            future.cancel()

        playerlist.append(stuff.author_id)

        StartGameRow['components'][1]['disabled'] = False

        ListeJoueurs = ""

        for x in range(len(playerlist)):
            if x != 0 :
                ListeJoueurs += f"<@{playerlist[x]}>\n"

        EmbedStartGame = discord.Embed(title="Hangman game !",
                                description = f"You want to play a game of hangman !\nOthers players have to react to this message with 🎰 to join the game\nYou can play between 2 and 10 players\n\nWord chooser :\n<@{playerlist[0]}>\n\nPlayer list :\n{ListeJoueurs}",
                                colour = discord.Colour.blurple())

        await stuff.edit_origin(embed = EmbedStartGame, components=[StartGameRow])

        while (len(playerlist) < 10) :

            if (stuff.author_id == authorofgame.id) and (stuff.custom_id == "start") :
                break

            ##########

            done, pending = await asyncio.wait([
                    manage_components.wait_for_component(self.client, messages=MessageStartGame, components=StartGameRow, check = CheckAjoutAutresPlayer),
                    manage_components.wait_for_component(self.client, messages=MessageStartGame, components=StartGameRow, check = CheckFinListeJoueurs)
                ], return_when=asyncio.FIRST_COMPLETED)

            stuff = done.pop().result()

            for future in done:
                future.exception()
            
            for future in pending:
                future.cancel()
            
            ##########

            if (stuff.author_id in playerlist) and (stuff.custom_id == "addplayer") :
                await stuff.send(content="You are already in the players list !", hidden=True)
                continue
            elif (stuff.custom_id == "start") and (stuff.author_id != authorofgame.id) :
                await stuff.send(content=f"You are not able to start the game. Only <@{authorofgame.id}> is able to start it.", hidden=True)
                continue
            else:
                if stuff.author_id == authorofgame.id :
                    pass
                else:
                    playerlist.append(stuff.author_id)

            ListeJoueurs = ""

            for x in range(len(playerlist)):
                ListeJoueurs += f"<@{playerlist[x]}>\n"

            EmbedStartGame = discord.Embed(title="Hangman game !",
                                    description = f"You want to play a game of hangman !\nOthers players have to react to this message with 🎰 to join the game\nYou can play between 2 and 10 players\n\nWord chooser :\n<@{playerlist[0]}>\n\nPlayer list :\n{ListeJoueurs}",
                                    colour = discord.Colour.blurple())

            await stuff.edit_origin(embed = EmbedStartGame, components=[StartGameRow])

        
        ListeJoueurs = ""
        for x in range(len(playerlist)):
            if x != 0 :
                ListeJoueurs += f"<@{playerlist[x]}>\n"

        EmbedPartieEnCours = discord.Embed(title = "The game has started",
                                        description = f"List of players in game :\n{ListeJoueurs}\n\n<@{playerlist[0]}>, please send me your word in DM's",
                                        colour = discord.Colour.purple())
        
        await MessageStartGame.edit(embed = EmbedPartieEnCours, components = [])

        gameauthor = [playerlist[0]]
        playerlist.pop(0)

        def checkWordChooser(message):
            return (message.guild == None) and (message.author.id == gameauthor[0])

        EmbedSendWord = discord.Embed(description = f"Send me the word you want the other players search.\nPlease, don't use accent, numbers, and/or spaces in your word",
                                    colour = discord.Colour.gold())

        DMword = await self.client.fetch_user(gameauthor[0])
        
        await DMword.send(embed = EmbedSendWord)

        ChoosenWord = await self.client.wait_for('message', check=checkWordChooser)

        ChoosenWord = ChoosenWord.content
        ChoosenWord = ''.join((c for c in unicodedata.normalize('NFD', ChoosenWord) if unicodedata.category(c) != 'Mn'))
        ChoosenWord = ChoosenWord.upper()
        MotFinGame = ChoosenWord
        ChoosenWord = list(ChoosenWord)

        MotADeviner = "_".join(ChoosenWord)
        MotADeviner = list(MotADeviner)

        IncorrectCharacters = ["0","1","2","3","4","5","6","7","8","9"," "]

        
        while any(item in IncorrectCharacters for item in MotADeviner) :

            EmbedSendWordAgain = discord.Embed(description = f"Your word was incorrect !\nPlease, don't use **accents, numbers, and/or spaces** in your word",
                                        colour = discord.Colour.red())

            await DMword.send(embed = EmbedSendWordAgain)

            ChoosenWord = await self.client.wait_for('message', check=checkWordChooser)

            ChoosenWord = ChoosenWord.content
            ChoosenWord = ''.join((c for c in unicodedata.normalize('NFD', ChoosenWord) if unicodedata.category(c) != 'Mn'))
            ChoosenWord = ChoosenWord.upper()
            MotFinGame = ChoosenWord
            ChoosenWord = list(ChoosenWord)

            MotADeviner = "_".join(ChoosenWord)
            MotADeviner = list(MotADeviner)

        MotADevinerString = "".join(ChoosenWord)
        
        EmbedMotChoisiPrivate = discord.Embed(title = "The word has been chosen !",
                                    description = f"The word you chosen is\n{MotADevinerString}",
                                    colour = discord.Colour.gold())
        
        EmbedMotChoisiPublic = discord.Embed(title = "The word has been chosen !",
                                            description = f"<@{gameauthor[0]}> chosen the word. The game will start in a second.",
                                            colour = discord.Colour.gold())
        
        await DMword.send(embed=EmbedMotChoisiPrivate)
        GameMessage = await ctx.send(embed = EmbedMotChoisiPublic)

        try :
            await MessageStartGame.delete()
        except Exception:
            pass

        MotCacher = ""
        for x in range(len(ChoosenWord)):
            MotCacher += "_"
        MotCacher = " ".join(MotCacher)
        MotCacher = list(MotCacher)
        MotCacherString = "".join(MotCacher)

        ListeJoueurs = ""
        for x in range(len(playerlist)):
            if x != 0 :
                ListeJoueurs += f"<@{playerlist[x]}>\n"
        
        await asyncio.sleep(2)

        erreurs = 0
        tourdujoueur = 0

        gagner = 0

        while erreurs < 10 :

            EmbedChercherMot = discord.Embed(title = f"`{MotCacherString}`",
                                            description = f"<@{playerlist[tourdujoueur]}>'s turn. Type a letter\n\nErrors : {erreurs}/10",
                                            colour = discord.Colour.purple())
            
            await GameMessage.edit(embed = EmbedChercherMot)

            def checkLettreDuJoueur(message):
                return (len(message.content) == 1) and (message.author.id == playerlist[tourdujoueur]) and (message.channel.id == GameMessage.channel.id) and not any(item in message.content for item in IncorrectCharacters)
            
            BonneLettreMSG = await self.client.wait_for('message', check=checkLettreDuJoueur)

            BonneLettre = BonneLettreMSG.content
            BonneLettre = ''.join((c for c in unicodedata.normalize('NFD', BonneLettre) if unicodedata.category(c) != 'Mn'))
            BonneLettre = BonneLettre.upper()

            if any(item in BonneLettre for item in MotADeviner) :
                PositionOfGoodLettre = get_index_positions(MotADeviner, BonneLettre)

                for x in range(len(PositionOfGoodLettre)):
                    MotCacher[PositionOfGoodLettre[x]] = BonneLettre
                
                await BonneLettreMSG.add_reaction("✅")
            
            else:
                erreurs += 1
                await BonneLettreMSG.add_reaction("❌")
            

            if (not any(item in "_" for item in MotCacher)) and erreurs < 10:
                gagner = 1
                break

            MotCacherString = "".join(MotCacher)

            if tourdujoueur == len(playerlist)-1:
                tourdujoueur = 0
            else :
                tourdujoueur += 1

        ListeJoueurs = ""
        for x in range(len(playerlist)):
            ListeJoueurs += f"<@{playerlist[x]}>\n"

        if gagner == 1 :

            EmbedGagner = discord.Embed(title = "End of the game !!",
                                        description = f"**Players won** !!\n\nThe word was :\n**_{MotFinGame}_**",
                                        colour = discord.Colour.green())
            EmbedGagner.add_field(name = "Word Chooser :",
                                value = f"<@{gameauthor[0]}>",
                                inline = True)
            EmbedGagner.add_field(name = "Players :",
                                value = f"{ListeJoueurs}",
                                inline = True)
            
            await ctx.send(embed = EmbedGagner)
            return
        
        elif gagner == 0:

            EmbedPerdu = discord.Embed(title = "End of the game !!",
                                        description = f"**Word Chooser won** !!\n\nThe word was :\n**_{MotFinGame}_**",
                                        colour = discord.Colour.dark_green())
            EmbedPerdu.add_field(name = "Word Chooser :",
                                value = f"<@{gameauthor[0]}>",
                                inline = True)
            EmbedPerdu.add_field(name = "Players :",
                                value = f"{ListeJoueurs}",
                                inline = True)
            
            await ctx.send(embed = EmbedPerdu)
            return


def setup(client):
    client.add_cog(HungManCommand(client))
    print("Hang Man command cog ready !")