import discord
from discord import Intents
from discord import message
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
import sqlite3

db = sqlite3.connect("smallgames.sqlite") # Ouverture de la base de données
cursor = db.cursor()

class Connect4Command(commands.Cog):
    def __init__(self, client):
        self.client = client

    @cog_ext.cog_slash(name = "connect4", description = "Play Connect 4 with a friend", options=[
        create_option(name = "other_player", description = "User you want to play with", option_type=6, required=True)
    ])
    async def connect4(self, ctx, other_player):

        ButtonCheck = [
            create_button(
                style=ButtonStyle.grey,
                emoji='✅',
                disabled=False
            )
        ]

        ButtonsColumns = [
            create_button(
                style=ButtonStyle.blue,
                emoji="1⃣",
                custom_id="one",
                disabled=False
            ),
            create_button(
                style=ButtonStyle.blue,
                emoji="2⃣",
                custom_id="two",
                disabled=False
            ),
            create_button(
                style=ButtonStyle.blue,
                emoji="3⃣",
                custom_id="three",
                disabled=False
            ),
            create_button(
                style=ButtonStyle.blue,
                emoji="4⃣",
                custom_id="four",
                disabled=False
            ),
            create_button(
                style=ButtonStyle.blue,
                emoji="5⃣",
                custom_id="five",
                disabled=False
            ),
            create_button(
                style=ButtonStyle.blue,
                emoji="6⃣",
                custom_id="six",
                disabled=False
            ),
            create_button(
                style=ButtonStyle.blue,
                emoji="7⃣",
                custom_id="seven",
                disabled=False
            )
        ]


        CheckRow = create_actionrow(*ButtonCheck)
        ColumnsRow1 = create_actionrow(*ButtonsColumns[0:4])
        ColumnsRow2 = create_actionrow(*ButtonsColumns[4:])

        red = '🔴'
        yellow = ':yellow_circle:'
        white = '⚪'

        grille = [[white for i in range(7)] for j in range(6)]
        grille.append(['1⃣','2⃣','3⃣','4⃣','5⃣','6⃣','7⃣'])
        tab = ""
        for x in range(len(grille)):
            tab += "".join(grille[x]) + "\n"

        tabcomplet = tab

        jaune = ctx.author

        ### code ###

        if jaune == other_player :
            embedsolo = discord.Embed(description = "You can't play with yourself", 
                                    colour = discord.Colour.dark_green())

            await ctx.send(embed = embedsolo)

            return

        elif other_player.bot or jaune.bot :
            embedsolo = discord.Embed(description = "Nobody can play with a bot", 
                                    colour = discord.Colour.dark_blue())

            await ctx.send(embed = embedsolo)

            return

        
        else:

            embedstartgame = discord.Embed(description = f"<@{other_player.id}>, <@{jaune.id}> want to play a **Connect 4 Game** against you. You got 15 seconds to accept the invitation !", 
                                            colour = discord.Colour.blurple())

            rep = await ctx.send(embed = embedstartgame, components=[CheckRow])

            def check(ctx: ComponentContext):
                return ctx.author_id == other_player.id

        try:
            await manage_components.wait_for_component(self.client, messages=rep, components=CheckRow, check=check, timeout=15.0)

        except asyncio.TimeoutError:

            embedrefused = discord.Embed(description = "He refused to play..", 
                                        colour = discord.Colour.dark_blue())

            await rep.edit(embed = embedrefused, components=[])

            await asyncio.sleep(5)

            await rep.delete()
            return
        
        else:

            ### Déclaration de la base de donnée ###

            zerovictoire = 0 # variable de victoire si le joueur n'a pas de profile
            zerodefaite = 0 # variable de défaite si le joueur n'a pas de profile

            # Jaune

            cursor.execute(f"SELECT VictoryCountConnect4, LoseCountConnect4 FROM connect4 WHERE user_id = {jaune.id}")
            donneejauneexist = cursor.fetchone() # vérif si les données existent pour le joueur jaune

            if donneejauneexist is None : # si les données existent pas pour le joueur jaune
                
                sql = ("INSERT INTO connect4(user_id, VictoryCountConnect4, LoseCountConnect4) VALUES(?,?,?)")
                val = (jaune.id, zerovictoire, zerodefaite)
                cursor.execute(sql, val)
                db.commit()
                pass


            # other_player

            cursor.execute(f"SELECT VictoryCountConnect4, LoseCountConnect4 FROM connect4 WHERE user_id = {other_player.id}")
            donneerougeexist = cursor.fetchone() # vérif si les données existent pour le joueur other_player

            if donneerougeexist is None : # si les données existent pas pour le joueur other_player
                
                sql = ("INSERT INTO connect4(user_id, VictoryCountConnect4, LoseCountConnect4) VALUES(?,?,?)")
                val = (other_player.id, zerovictoire, zerodefaite)
                cursor.execute(sql, val)
                db.commit()
                pass

            ### Suite du code ###

            QuiCommence = random.randint(0,1)

            if QuiCommence == 0 :
                PremierJoueur = jaune
                jaune = other_player
                other_player = PremierJoueur

            embedjeu = discord.Embed(description = f"Alright !! Let's go !\nThe yellow player (<@{jaune.id}>) starts !",
                                    colour = 0x050087)

            embedjoueurs = discord.Embed(description = f"{yellow} <@{jaune.id}>\n{red} <@{other_player.id}>", 
                                    colour = 0x050087)

            await rep.edit(embed = embedjeu, components=[])

            tab = await ctx.channel.send("I am preparing the game for you, please be patient !")

            await asyncio.sleep(5)

            await rep.edit(embed = embedjoueurs)
            await tab.edit(content = f"{tabcomplet}", components=[ColumnsRow1, ColumnsRow2])

            for t in range (42):

                if t % 2 == 0:

                    embedjeujaune = discord.Embed(description = f"{yellow} <@{jaune.id}> **__NOW__**\n{red} <@{other_player.id}> **NEXT**", 
                                                colour = 0xFFFF00)

                    await rep.edit(embed = embedjeujaune)

                    
                    if (grille[0][0]) != white:
                        ColumnsRow1['components'][0]['disabled'] = True
                    if (grille[0][1]) != white:
                        ColumnsRow1['components'][1]["disabled"] = True
                    if (grille[0][2]) != white:
                        ColumnsRow1['components'][2]["disabled"] = True
                    if (grille[0][3]) != white:
                        ColumnsRow1['components'][3]["disabled"] = True
                    if (grille[0][4]) != white:
                        ColumnsRow2['components'][0]["disabled"] = True
                    if (grille[0][5]) != white:
                        ColumnsRow2['components'][1]["disabled"] = True
                    if (grille[0][6]) != white:
                        ColumnsRow2['components'][2]["disabled"] = True

                    await tab.edit(content = f"{tabcomplet}", components=[ColumnsRow1, ColumnsRow2])

                    def checkjaune1(ctx: ComponentContext):
                        if ctx.author_id != jaune.id:
                            return ctx.author_id
                        else:
                            return ctx.author_id == jaune.id and ((ctx.component_id == "one") or (ctx.component_id == "two") or (ctx.component_id == "three") or (ctx.component_id == "four") or (ctx.component_id == "five") or (ctx.component_id == "six") or (ctx.component_id == "seven"))
                    
                    ButtonClick: ComponentContext = await manage_components.wait_for_component(self.client, messages=tab, components=[ColumnsRow1, ColumnsRow2], check=checkjaune1)

                    while ButtonClick.author_id != jaune.id:

                        await ButtonClick.send("You are either not a player or the one who should play. Please wait your turn if you are a player", hidden=True)

                        ButtonClick: ComponentContext = await manage_components.wait_for_component(self.client, messages=tab, components=[ColumnsRow1, ColumnsRow2], check=checkjaune1)
                    
                    await ButtonClick.defer(ignore=True)

                    ligne = 5

                    if ButtonClick.component_id == 'one':
                        colonne = 0
                    elif ButtonClick.component_id == 'two':
                        colonne = 1
                    elif ButtonClick.component_id == 'three':
                        colonne = 2
                    elif ButtonClick.component_id == 'four':
                        colonne = 3
                    elif ButtonClick.component_id == 'five':
                        colonne = 4
                    elif ButtonClick.component_id == 'six':
                        colonne = 5
                    elif ButtonClick.component_id == 'seven':
                        colonne = 6

                    while (grille[ligne][colonne]) != white :
                        ligne = ligne - 1
                        
                    grille[ligne][colonne] = yellow
                    tableau = ""
                    for x in range(len(grille)):
                        tableau += "".join(grille[x]) + "\n"

                    tabcomplet = tableau
                
                else:

                    embedjeurouge = discord.Embed(description = f"{yellow} <@{jaune.id}> **NEXT**\n{red} <@{other_player.id}> **__NOW__**", 
                                                colour = 0xFF0000)

                    await rep.edit(embed = embedjeurouge)
                    
                    if (grille[0][0]) != white:
                        ColumnsRow1['components'][0]['disabled'] = True
                    if (grille[0][1]) != white:
                        ColumnsRow1['components'][1]["disabled"] = True
                    if (grille[0][2]) != white:
                        ColumnsRow1['components'][2]["disabled"] = True
                    if (grille[0][3]) != white:
                        ColumnsRow1['components'][3]["disabled"] = True
                    if (grille[0][4]) != white:
                        ColumnsRow2['components'][0]["disabled"] = True
                    if (grille[0][5]) != white:
                        ColumnsRow2['components'][1]["disabled"] = True
                    if (grille[0][6]) != white:
                        ColumnsRow2['components'][2]["disabled"] = True

                    await tab.edit(content = f"{tabcomplet}", components=[ColumnsRow1, ColumnsRow2])

                    def checkrouge1(ctx: ComponentContext):
                        if ctx.author_id != other_player.id:
                            return ctx.author_id
                        else:
                            return ctx.author_id == other_player.id and ((ctx.component_id == "one") or (ctx.component_id == "two") or (ctx.component_id == "three") or (ctx.component_id == "four") or (ctx.component_id == "five") or (ctx.component_id == "six") or (ctx.component_id == "seven"))
                    
                    ButtonClick: ComponentContext = await manage_components.wait_for_component(self.client, messages=tab, components=[ColumnsRow1, ColumnsRow2], check=checkrouge1)

                    while ButtonClick.author_id != other_player.id:

                        await ButtonClick.send("You are either not a player or the one who should play. Please wait your turn if you are a player", hidden=True)

                        ButtonClick: ComponentContext = await manage_components.wait_for_component(self.client, messages=tab, components=[ColumnsRow1, ColumnsRow2], check=checkrouge1)


                    await ButtonClick.defer(ignore=True)

                    ligne = 5

                    if ButtonClick.component_id == 'one':
                        colonne = 0
                    elif ButtonClick.component_id == 'two':
                        colonne = 1
                    elif ButtonClick.component_id == 'three':
                        colonne = 2
                    elif ButtonClick.component_id == 'four':
                        colonne = 3
                    elif ButtonClick.component_id == 'five':
                        colonne = 4
                    elif ButtonClick.component_id == 'six':
                        colonne = 5
                    elif ButtonClick.component_id == 'seven':
                        colonne = 6

                    while (grille[ligne][colonne]) != white :
                        ligne = ligne - 1

                    grille[ligne][colonne] = red
                    tableau = ""
                    for x in range(len(grille)):
                        tableau += "".join(grille[x]) + "\n"

                    tabcomplet = tableau

                
                embedfinjeujaune = discord.Embed(description = f"<@{jaune.id}> WON !!\nGG WP to <@{jaune.id}> and <@{other_player.id}>",
                                                colour = 0xFFFF00)

                embedfinjeurouge = discord.Embed(description = f"<@{other_player.id}> WON !!\nGG WP to <@{other_player.id}> and <@{jaune.id}>",
                                                colour = 0xFF0000)

                embedfinjeuegalite = discord.Embed(description = f"IT'S A TIE !!\nGG WP to <@{jaune.id}> and <@{other_player.id}>",
                                                colour = 0x050087)
                
                for x in range(len(grille)):
                    for y in range(len(grille[x])-3):

                        # Si jaune gagne en horizontal

                        if grille[x][y] == yellow and grille[x][y+1] == yellow and grille[x][y+2] == yellow and grille[x][y+3] == yellow:
                            await rep.delete()
                            await ctx.channel.send(embed = embedfinjeujaune)

                            cursor.execute(f"SELECT VictoryCountConnect4, LoseCountConnect4 FROM connect4 WHERE user_id = {jaune.id}")
                            add1victoryjaune = cursor.fetchall()
                            ajouter1victoirejaune = int(add1victoryjaune[0][0])+1
                            sql = ("UPDATE connect4 SET VictoryCountConnect4 = ? WHERE user_id = ?")
                            val = (ajouter1victoirejaune, jaune.id)
                            cursor.execute(sql, val)
                            db.commit()

                            cursor.execute(f"SELECT VictoryCountConnect4, LoseCountConnect4 FROM connect4 WHERE user_id = {other_player.id}")
                            add1defeatrouge = cursor.fetchall()
                            ajouter1défaiterouge = int(add1defeatrouge[0][1])+1
                            sql = ("UPDATE connect4 SET LoseCountConnect4 = ? WHERE user_id = ?")
                            val = (ajouter1défaiterouge, other_player.id)
                            cursor.execute(sql, val)
                            db.commit()

                            return
                        
                        # Si other_player gagne en horizontal

                        elif grille[x][y] == red and grille[x][y+1] == red and grille[x][y+2] == red and grille[x][y+3] == red:
                            await rep.delete()
                            await ctx.channel.send(embed = embedfinjeurouge)

                            cursor.execute(f"SELECT VictoryCountConnect4, LoseCountConnect4 FROM connect4 WHERE user_id = {other_player.id}")
                            add1victoryrouge = cursor.fetchall()
                            ajouter1victoirerouge = int(add1victoryrouge[0][0])+1
                            sql = ("UPDATE connect4 SET VictoryCountConnect4 = ? WHERE user_id = ?")
                            val = (ajouter1victoirerouge, other_player.id)
                            cursor.execute(sql, val)
                            db.commit()

                            cursor.execute(f"SELECT VictoryCountConnect4, LoseCountConnect4 FROM connect4 WHERE user_id = {jaune.id}")
                            add1defeatjaune = cursor.fetchall()
                            ajouter1défaitejaune = int(add1defeatjaune[0][1])+1
                            sql = ("UPDATE connect4 SET LoseCountConnect4 = ? WHERE user_id = ?")
                            val = (ajouter1défaitejaune, jaune.id)
                            cursor.execute(sql, val)
                            db.commit()

                            return





                for x in range(len(grille)-3):
                    for y in range(len(grille[x])):

                        # Si jaune gagne en vertical

                        if grille[x][y] == yellow and grille[x+1][y] == yellow and grille[x+2][y] == yellow and grille[x+3][y] == yellow:
                            await rep.delete()
                            await ctx.channel.send(embed = embedfinjeujaune)

                            cursor.execute(f"SELECT VictoryCountConnect4, LoseCountConnect4 FROM connect4 WHERE user_id = {jaune.id}")
                            add1victoryjaune = cursor.fetchall()
                            ajouter1victoirejaune = int(add1victoryjaune[0][0])+1
                            sql = ("UPDATE connect4 SET VictoryCountConnect4 = ? WHERE user_id = ?")
                            val = (ajouter1victoirejaune, jaune.id)
                            cursor.execute(sql, val)
                            db.commit()

                            cursor.execute(f"SELECT VictoryCountConnect4, LoseCountConnect4 FROM connect4 WHERE user_id = {other_player.id}")
                            add1defeatrouge = cursor.fetchall()
                            ajouter1défaiterouge = int(add1defeatrouge[0][1])+1
                            sql = ("UPDATE connect4 SET LoseCountConnect4 = ? WHERE user_id = ?")
                            val = (ajouter1défaiterouge, other_player.id)
                            cursor.execute(sql, val)
                            db.commit()

                            return

                        # Si other_player gagne en vertical

                        elif grille[x][y] == red and grille[x+1][y] == red and grille[x+2][y] == red and grille[x+3][y] == red:
                            await rep.delete()
                            await ctx.channel.send(embed = embedfinjeurouge)

                            cursor.execute(f"SELECT VictoryCountConnect4, LoseCountConnect4 FROM connect4 WHERE user_id = {other_player.id}")
                            add1victoryrouge = cursor.fetchall()
                            ajouter1victoirerouge = int(add1victoryrouge[0][0])+1
                            sql = ("UPDATE connect4 SET VictoryCountConnect4 = ? WHERE user_id = ?")
                            val = (ajouter1victoirerouge, other_player.id)
                            cursor.execute(sql, val)
                            db.commit()

                            cursor.execute(f"SELECT VictoryCountConnect4, LoseCountConnect4 FROM connect4 WHERE user_id = {jaune.id}")
                            add1defeatjaune = cursor.fetchall()
                            ajouter1défaitejaune = int(add1defeatjaune[0][1])+1
                            sql = ("UPDATE connect4 SET LoseCountConnect4 = ? WHERE user_id = ?")
                            val = (ajouter1défaitejaune, jaune.id)
                            cursor.execute(sql, val)
                            db.commit()

                            return





                for x in range(len(grille)-3):
                    for y in range(len(grille[x])-3):

                        # Si jaune gagne en diagonale positive

                        if grille[x][y] == yellow and grille[x+1][y+1] == yellow and grille[x+2][y+2] == yellow and grille[x+3][y+3] == yellow:
                            await rep.delete()
                            await ctx.channel.send(embed = embedfinjeujaune)

                            cursor.execute(f"SELECT VictoryCountConnect4, LoseCountConnect4 FROM connect4 WHERE user_id = {jaune.id}")
                            add1victoryjaune = cursor.fetchall()
                            ajouter1victoirejaune = int(add1victoryjaune[0][0])+1
                            sql = ("UPDATE connect4 SET VictoryCountConnect4 = ? WHERE user_id = ?")
                            val = (ajouter1victoirejaune, jaune.id)
                            cursor.execute(sql, val)
                            db.commit()

                            cursor.execute(f"SELECT VictoryCountConnect4, LoseCountConnect4 FROM connect4 WHERE user_id = {other_player.id}")
                            add1defeatrouge = cursor.fetchall()
                            ajouter1défaiterouge = int(add1defeatrouge[0][1])+1
                            sql = ("UPDATE connect4 SET LoseCountConnect4 = ? WHERE user_id = ?")
                            val = (ajouter1défaiterouge, other_player.id)
                            cursor.execute(sql, val)
                            db.commit()

                            return

                        # Si other_player gagne en diagonale positive

                        elif grille[x][y] == red and grille[x+1][y+1] == red and grille[x+2][y+2] == red and grille[x+3][y+3] == red:
                            await rep.delete()
                            await ctx.channel.send(embed = embedfinjeurouge)

                            cursor.execute(f"SELECT VictoryCountConnect4, LoseCountConnect4 FROM connect4 WHERE user_id = {other_player.id}")
                            add1victoryrouge = cursor.fetchall()
                            ajouter1victoirerouge = int(add1victoryrouge[0][0])+1
                            sql = ("UPDATE connect4 SET VictoryCountConnect4 = ? WHERE user_id = ?")
                            val = (ajouter1victoirerouge, other_player.id)
                            cursor.execute(sql, val)
                            db.commit()

                            cursor.execute(f"SELECT VictoryCountConnect4, LoseCountConnect4 FROM connect4 WHERE user_id = {jaune.id}")
                            add1defeatjaune = cursor.fetchall()
                            ajouter1défaitejaune = int(add1defeatjaune[0][1])+1
                            sql = ("UPDATE connect4 SET LoseCountConnect4 = ? WHERE user_id = ?")
                            val = (ajouter1défaitejaune, jaune.id)
                            cursor.execute(sql, val)
                            db.commit()

                            return





                for x in range(len(grille)-3):
                    for y in range(3, len(grille[x])):

                        # Si jaune gagne en diagonale négative

                        if grille[x][y] == yellow and grille[x+1][y-1] == yellow and grille[x+2][y-2] == yellow and grille[x+3][y-3] == yellow:
                            await rep.delete()
                            await ctx.channel.send(embed = embedfinjeujaune)

                            cursor.execute(f"SELECT VictoryCountConnect4, LoseCountConnect4 FROM connect4 WHERE user_id = {jaune.id}")
                            add1victoryjaune = cursor.fetchall()
                            ajouter1victoirejaune = int(add1victoryjaune[0][0])+1
                            sql = ("UPDATE connect4 SET VictoryCountConnect4 = ? WHERE user_id = ?")
                            val = (ajouter1victoirejaune, jaune.id)
                            cursor.execute(sql, val)
                            db.commit()

                            cursor.execute(f"SELECT VictoryCountConnect4, LoseCountConnect4 FROM connect4 WHERE user_id = {other_player.id}")
                            add1defeatrouge = cursor.fetchall()
                            ajouter1défaiterouge = int(add1defeatrouge[0][1])+1
                            sql = ("UPDATE connect4 SET LoseCountConnect4 = ? WHERE user_id = ?")
                            val = (ajouter1défaiterouge, other_player.id)
                            cursor.execute(sql, val)
                            db.commit()

                            return

                        # Si other_player gagne en diagonale négative

                        elif grille[x][y] == red and grille[x+1][y-1] == red and grille[x+2][y-2] == red and grille[x+3][y-3] == red:
                            await rep.delete()
                            await ctx.channel.send(embed = embedfinjeurouge)

                            cursor.execute(f"SELECT VictoryCountConnect4, LoseCountConnect4 FROM connect4 WHERE user_id = {other_player.id}")
                            add1victoryrouge = cursor.fetchall()
                            ajouter1victoirerouge = int(add1victoryrouge[0][0])+1
                            sql = ("UPDATE connect4 SET VictoryCountConnect4 = ? WHERE user_id = ?")
                            val = (ajouter1victoirerouge, other_player.id)
                            cursor.execute(sql, val)
                            db.commit()

                            cursor.execute(f"SELECT VictoryCountConnect4, LoseCountConnect4 FROM connect4 WHERE user_id = {jaune.id}")
                            add1defeatjaune = cursor.fetchall()
                            ajouter1défaitejaune = int(add1defeatjaune[0][1])+1
                            sql = ("UPDATE connect4 SET LoseCountConnect4 = ? WHERE user_id = ?")
                            val = (ajouter1défaitejaune, jaune.id)
                            cursor.execute(sql, val)
                            db.commit()

                            return

                # S'il y a égalité entre les 2 joueurs

                if grille[0][0] != white and grille[0][1] != white and grille[0][2] != white and grille[0][3] != white and grille[0][4] != white and grille[0][5] != white and grille[0][6] != white :
                    await rep.delete()
                    await ctx.channel.send(embed = embedfinjeuegalite)

                    return


def setup(client):
    client.add_cog(Connect4Command(client))
    print("Connect 4 games command cog ready !")