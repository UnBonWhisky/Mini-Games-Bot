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
import sqlite3

from discord_slash.context import SlashContext

db = sqlite3.connect("smallgames.sqlite") # Ouverture de la base de données
cursor = db.cursor()

class TicTacToeCommand(commands.Cog):
    def __init__(self, client):
        self.client = client

    @cog_ext.cog_slash(name = "tictactoe", description = "Play Tic-Tac-Toe with a friend", options=[
        create_option(name = "circleuser", description = "User you want to play with", option_type=6, required=True)
    ])
    async def tictactoe(self, ctx : SlashContext, circleuser):

        ### déclaration des variables ###

        ButtonCheck = [
            create_button(
                style=ButtonStyle.grey,
                emoji='✅',
                disabled=False
            )
        ]

        ButtonsNumbers = [
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
            ),
            create_button(
                style=ButtonStyle.blue,
                emoji='8️⃣',
                custom_id="eight",
                disabled=False
            ),
            create_button(
                style=ButtonStyle.blue,
                emoji='9️⃣',
                custom_id="nine",
                disabled=False
            )
        ]

        CheckRow = create_actionrow(*ButtonCheck)
        NumberRow1 = create_actionrow(*ButtonsNumbers[:3])
        NumberRow2 = create_actionrow(*ButtonsNumbers[3:6])
        NumberRow3 = create_actionrow(*ButtonsNumbers[6:])

        cross = '❌'
        circle = '⭕'

        number1 = '1️⃣'
        number2 = '2️⃣'
        number3 = '3️⃣'
        number4 = '4️⃣'
        number5 = '5️⃣'
        number6 = '6️⃣'
        number7 = '7️⃣'
        number8 = '8️⃣'
        number9 = '9️⃣'

        blanc = '⬜'

        grille = [[number1, blanc, number2, blanc, number3],
                [blanc, blanc, blanc, blanc, blanc],
                [number4, blanc, number5, blanc, number6],
                [blanc, blanc, blanc, blanc, blanc],
                [number7, blanc, number8, blanc, number9]]

        tab = ""
        for x in range(len(grille)):
            tab += "".join(grille[x]) + "\n"
        
        tabcomplet = tab

        crossuser = ctx.author

        if crossuser == circleuser :
            embedsolo = discord.Embed(description = "You can't play with yourself", 
                                    colour = discord.Colour.dark_green())

            await ctx.message.channel.send(embed = embedsolo)
            return

        elif crossuser.bot or circleuser.bot :
            embedsolo = discord.Embed(description = "Nobody can play with a bot", 
                                    colour = discord.Colour.dark_blue())

            await ctx.message.channel.send(embed = embedsolo)
            return

        else:

            EmbedStartGame = discord.Embed(description = f"<@{circleuser.id}>, <@{crossuser.id}> want to play **Tic Tac Toe Game** against you. You got 15 seconds to accept the invitation !", 
                                            colour = discord.Colour.blurple())

            rep = await ctx.send(embed = EmbedStartGame, components=[CheckRow])

        def check(ctx: ComponentContext):
                return ctx.author_id == circleuser.id

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

            # Cross

            cursor.execute(f"SELECT VictoryCountTTT, LoseCountTTT FROM tictactoe WHERE user_id = {crossuser.id}")
            donneecrossexist = cursor.fetchone() # vérif si les données existent pour le joueur croix

            if donneecrossexist is None : # si les données existent pas pour le joueur croix
                
                sql = ("INSERT INTO tictactoe(user_id, VictoryCountTTT, LoseCountTTT) VALUES(?,?,?)")
                val = (crossuser.id, zerovictoire, zerodefaite)
                cursor.execute(sql, val)
                db.commit()


            # Circle

            cursor.execute(f"SELECT VictoryCountTTT, LoseCountTTT FROM tictactoe WHERE user_id = {circleuser.id}")
            donneecircleexist = cursor.fetchone() # vérif si les données existent pour le joueur cercle

            if donneecircleexist is None : # si les données existent pas pour le joueur cerlce
                
                sql = ("INSERT INTO tictactoe(user_id, VictoryCountTTT, LoseCountTTT) VALUES(?,?,?)")
                val = (circleuser.id, zerovictoire, zerodefaite)
                cursor.execute(sql, val)
                db.commit()

            QuiCommence = random.randint(0,1)

            if QuiCommence == 0 :
                PremierJoueur = crossuser
                crossuser = circleuser
                circleuser = PremierJoueur
            
            embedjeu = discord.Embed(description = f"Alright !! Let's go !\nThe cross player (<@{crossuser.id}>) starts !",
                                    colour = discord.Colour.blue())

            embedjoueurs = discord.Embed(description = f"{cross} <@{crossuser.id}>\n{circle} <@{circleuser.id}>", 
                                    colour = discord.Colour.blue())

            await rep.edit(embed = embedjeu, components=[])

            tab = await ctx.channel.send("The game will start in just a second !")

            await asyncio.sleep(5)

            await rep.edit(embed = embedjoueurs)

            for t in range (9):

                if t %2 == 0:

                    embedjeucross = discord.Embed(description = f"{cross} <@{crossuser.id}> **__NOW__**\n{circle} <@{circleuser.id}> **NEXT**", 
                                                colour = discord.Colour.blue())

                    await rep.edit(embed = embedjeucross)

                    if (grille[0][0]) != number1:
                        NumberRow1['components'][0]["disabled"] = True
                    if (grille[0][2]) != number2:
                        NumberRow1['components'][1]["disabled"] = True
                    if (grille[0][4]) != number3:
                        NumberRow1['components'][2]["disabled"] = True
                    if (grille[2][0]) != number4:
                        NumberRow2['components'][0]["disabled"] = True
                    if (grille[2][2]) != number5:
                        NumberRow2['components'][1]["disabled"] = True
                    if (grille[2][4]) != number6:
                        NumberRow2['components'][2]["disabled"] = True
                    if (grille[4][0]) != number7:
                        NumberRow3['components'][0]["disabled"] = True
                    if (grille[4][2]) != number8:
                        NumberRow3['components'][1]["disabled"] = True
                    if (grille[4][4]) != number9:
                        NumberRow3['components'][2]["disabled"] = True

                    tableau = ""
                    for x in range(len(grille)):
                        tableau += "".join(grille[x]) + "\n"
                    
                    tableaucomplet = tableau

                    await tab.edit(content = f"{tableaucomplet}", components=[NumberRow1, NumberRow2, NumberRow3])

                    #def checkcross1(reaction, user):
                    #    return user == crossuser and ((str(reaction.emoji) == '1️⃣') or (str(reaction.emoji) == '2️⃣') or (str(reaction.emoji) == '3️⃣') or (str(reaction.emoji) == '4️⃣') or (str(reaction.emoji) == '5️⃣') or (str(reaction.emoji) == '6️⃣') or (str(reaction.emoji) == '7️⃣') or (str(reaction.emoji) == '8️⃣') or (str(reaction.emoji) == '9️⃣')) and reaction.message.id == tab.id

                    #reaction, user = await self.client.wait_for('reaction_add', check=checkcross1)

                    def checkcross1(ctx: ComponentContext):
                        return ctx.author_id == crossuser.id
                    
                    AttenteJeuCroix = await manage_components.wait_for_component(self.client, messages=tab, components=[NumberRow1, NumberRow2, NumberRow3], check = checkcross1)

                    if AttenteJeuCroix.component_id == "one" :
                        ligne = 0
                        colonne = 0
                    elif AttenteJeuCroix.component_id == "two" :
                        ligne = 0
                        colonne = 2
                    elif AttenteJeuCroix.component_id == "three" :
                        ligne = 0
                        colonne = 4
                    elif AttenteJeuCroix.component_id == "four" :
                        ligne = 2
                        colonne = 0
                    elif AttenteJeuCroix.component_id == "five" :
                        ligne = 2
                        colonne = 2
                    elif AttenteJeuCroix.component_id == "six" :
                        ligne = 2
                        colonne = 4
                    elif AttenteJeuCroix.component_id == "seven" :
                        ligne = 4
                        colonne = 0
                    elif AttenteJeuCroix.component_id == "eight" :
                        ligne = 4
                        colonne = 2
                    elif AttenteJeuCroix.component_id == "nine" :
                        ligne = 4
                        colonne = 4

                    await AttenteJeuCroix.defer(ignore=True)
                    
                    grille[ligne][colonne] = cross

                    tableau = ""
                    for x in range(len(grille)):
                        tableau += "".join(grille[x]) + "\n"
                    
                    tableaucomplet = tableau

                    #await tab.edit(content = f"{tableaucomplet}")
                
                else :

                    embedjeucross = discord.Embed(description = f"{cross} <@{crossuser.id}> **NEXT**\n{circle} <@{circleuser.id}> **__NOW__**", 
                                                colour = discord.Colour.blue())

                    await rep.edit(embed = embedjeucross)

                    if (grille[0][0]) != number1:
                        NumberRow1['components'][0]["disabled"] = True
                    if (grille[0][2]) != number2:
                        NumberRow1['components'][1]["disabled"] = True
                    if (grille[0][4]) != number3:
                        NumberRow1['components'][2]["disabled"] = True
                    if (grille[2][0]) != number4:
                        NumberRow2['components'][0]["disabled"] = True
                    if (grille[2][2]) != number5:
                        NumberRow2['components'][1]["disabled"] = True
                    if (grille[2][4]) != number6:
                        NumberRow2['components'][2]["disabled"] = True
                    if (grille[4][0]) != number7:
                        NumberRow3['components'][0]["disabled"] = True
                    if (grille[4][2]) != number8:
                        NumberRow3['components'][1]["disabled"] = True
                    if (grille[4][4]) != number9:
                        NumberRow3['components'][2]["disabled"] = True

                    tableau = ""
                    for x in range(len(grille)):
                        tableau += "".join(grille[x]) + "\n"
                    
                    tableaucomplet = tableau

                    await tab.edit(content = f"{tableaucomplet}", components=[NumberRow1, NumberRow2, NumberRow3])

                    #def checkcircle1(reaction, user):
                    #    return user == circleuser and ((str(reaction.emoji) == '1️⃣') or (str(reaction.emoji) == '2️⃣') or (str(reaction.emoji) == '3️⃣') or (str(reaction.emoji) == '4️⃣') or (str(reaction.emoji) == '5️⃣') or (str(reaction.emoji) == '6️⃣') or (str(reaction.emoji) == '7️⃣') or (str(reaction.emoji) == '8️⃣') or (str(reaction.emoji) == '9️⃣')) and reaction.message.id == tab.id

                    def checkcircle1(ctx: ComponentContext):
                        return ctx.author_id == circleuser.id
                    
                    #reaction, user = await self.client.wait_for('reaction_add', check=checkcircle1)

                    AttenteJeuRond = await manage_components.wait_for_component(self.client, messages=tab, components=[NumberRow1, NumberRow2, NumberRow3], check = checkcircle1)

                    if AttenteJeuRond.component_id == "one" :
                        ligne = 0
                        colonne = 0
                    elif AttenteJeuRond.component_id == "two" :
                        ligne = 0
                        colonne = 2
                    elif AttenteJeuRond.component_id == "three" :
                        ligne = 0
                        colonne = 4
                    elif AttenteJeuRond.component_id == "four" :
                        ligne = 2
                        colonne = 0
                    elif AttenteJeuRond.component_id == "five" :
                        ligne = 2
                        colonne = 2
                    elif AttenteJeuRond.component_id == "six" :
                        ligne = 2
                        colonne = 4
                    elif AttenteJeuRond.component_id == "seven" :
                        ligne = 4
                        colonne = 0
                    elif AttenteJeuRond.component_id == "eight" :
                        ligne = 4
                        colonne = 2
                    elif AttenteJeuRond.component_id == "nine" :
                        ligne = 4
                        colonne = 4

                    await AttenteJeuRond.defer(ignore=True)

                    
                    grille[ligne][colonne] = circle

                    tableau = ""
                    for x in range(len(grille)):
                        tableau += "".join(grille[x]) + "\n"
                    
                    tableaucomplet = tableau

                embedfinjeucross = discord.Embed(description = f"<@{crossuser.id}> WON !!\nGG WP to <@{crossuser.id}> and <@{circleuser.id}>",
                                                colour = discord.Colour.blue())

                embedfinjeucircle = discord.Embed(description = f"<@{circleuser.id}> WON !!\nGG WP to <@{circleuser.id}> and <@{crossuser.id}>",
                                                colour = discord.Colour.blue())

                embedfinjeuegalite = discord.Embed(description = f"IT'S A TIE !!\nGG WP to <@{crossuser.id}> and <@{circleuser.id}>",
                                                colour = discord.Colour.blue())

                for x in range(len(grille)):
                    for y in range(len(grille[x])-4):
                        
                        # Si cross gagne en vertical

                        if grille[x][y] == cross and grille[x][y+2] == cross and grille[x][y+4] == cross :
                            await rep.delete()
                            await tab.edit(content = f"{tableaucomplet}", components=[])
                            await ctx.channel.send(embed = embedfinjeucross, components=[])

                            cursor.execute(f"SELECT VictoryCountTTT, LoseCountTTT FROM tictactoe WHERE user_id = {crossuser.id}")
                            add1victorycross = cursor.fetchall()
                            ajouter1victoirecroix = int(add1victorycross[0][0])+1
                            sql = ("UPDATE tictactoe SET VictoryCountTTT = ? WHERE user_id = ?")
                            val = (ajouter1victoirecroix, crossuser.id)
                            cursor.execute(sql, val)
                            db.commit()

                            cursor.execute(f"SELECT VictoryCountTTT, LoseCountTTT FROM tictactoe WHERE user_id = {circleuser.id}")
                            add1defeatcircle = cursor.fetchall()
                            ajouter1défaitecercle = int(add1defeatcircle[0][1])+1
                            sql = ("UPDATE tictactoe SET LoseCountTTT = ? WHERE user_id = ?")
                            val = (ajouter1défaitecercle, circleuser.id)
                            cursor.execute(sql, val)
                            db.commit()

                            return
                        
                        # Si circle gagne en vertical

                        elif grille[x][y] == circle and grille[x][y+2] == circle and grille[x][y+4] == circle :
                            await rep.delete()
                            await tab.edit(content = f"{tableaucomplet}", components=[])
                            await ctx.channel.send(embed = embedfinjeucircle, components=[])

                            cursor.execute(f"SELECT VictoryCountTTT, LoseCountTTT FROM tictactoe WHERE user_id = {circleuser.id}")
                            add1victorycircle = cursor.fetchall()
                            ajouter1victoirecercle = int(add1victorycircle[0][0])+1
                            sql = ("UPDATE tictactoe SET VictoryCountTTT = ? WHERE user_id = ?")
                            val = (ajouter1victoirecercle, circleuser.id)
                            cursor.execute(sql, val)
                            db.commit()

                            cursor.execute(f"SELECT VictoryCountTTT, LoseCountTTT FROM tictactoe WHERE user_id = {crossuser.id}")
                            add1defeatcross = cursor.fetchall()
                            ajouter1défaitecroix = int(add1defeatcross[0][1])+1
                            sql = ("UPDATE tictactoe SET LoseCountTTT = ? WHERE user_id = ?")
                            val = (ajouter1défaitecroix, crossuser.id)
                            cursor.execute(sql, val)
                            db.commit()

                            return

                
                for x in range(len(grille)-4):
                    for y in range(len(grille[x])):
                        
                        # Si cross gagne en horizontal

                        if grille[x][y] == cross and grille[x+2][y] == cross and grille[x+4][y] == cross :
                            await rep.delete()
                            await tab.edit(content = f"{tableaucomplet}", components=[])
                            await ctx.channel.send(embed = embedfinjeucross, components=[])

                            cursor.execute(f"SELECT VictoryCountTTT, LoseCountTTT FROM tictactoe WHERE user_id = {crossuser.id}")
                            add1victorycross = cursor.fetchall()
                            ajouter1victoirecroix = int(add1victorycross[0][0])+1
                            sql = ("UPDATE tictactoe SET VictoryCountTTT = ? WHERE user_id = ?")
                            val = (ajouter1victoirecroix, crossuser.id)
                            cursor.execute(sql, val)
                            db.commit()

                            cursor.execute(f"SELECT VictoryCountTTT, LoseCountTTT FROM tictactoe WHERE user_id = {circleuser.id}")
                            add1defeatcircle = cursor.fetchall()
                            ajouter1défaitecercle = int(add1defeatcircle[0][1])+1
                            sql = ("UPDATE tictactoe SET LoseCountTTT = ? WHERE user_id = ?")
                            val = (ajouter1défaitecercle, circleuser.id)
                            cursor.execute(sql, val)
                            db.commit()

                            return
                        
                        # Si circle gagne en horizontal

                        elif grille[x][y] == circle and grille[x+2][y] == circle and grille[x+4][y] == circle :
                            await rep.delete()
                            await tab.edit(content = f"{tableaucomplet}", components=[])
                            await ctx.channel.send(embed = embedfinjeucircle, components=[])

                            cursor.execute(f"SELECT VictoryCountTTT, LoseCountTTT FROM tictactoe WHERE user_id = {circleuser.id}")
                            add1victorycircle = cursor.fetchall()
                            ajouter1victoirecercle = int(add1victorycircle[0][0])+1
                            sql = ("UPDATE tictactoe SET VictoryCountTTT = ? WHERE user_id = ?")
                            val = (ajouter1victoirecercle, circleuser.id)
                            cursor.execute(sql, val)
                            db.commit()

                            cursor.execute(f"SELECT VictoryCountTTT, LoseCountTTT FROM tictactoe WHERE user_id = {crossuser.id}")
                            add1defeatcross = cursor.fetchall()
                            ajouter1défaitecroix = int(add1defeatcross[0][1])+1
                            sql = ("UPDATE tictactoe SET LoseCountTTT = ? WHERE user_id = ?")
                            val = (ajouter1défaitecroix, crossuser.id)
                            cursor.execute(sql, val)
                            db.commit()

                            return

                
                for x in range(len(grille)-4):
                    for y in range(len(grille[x])-4):
                        
                        # Si cross gagne en diagonale positive

                        if grille[x][y] == cross and grille[x+2][y+2] == cross and grille[x+4][y+4] == cross :
                            await rep.delete()
                            await tab.edit(content = f"{tableaucomplet}", components=[])
                            await ctx.channel.send(embed = embedfinjeucross, components=[])

                            cursor.execute(f"SELECT VictoryCountTTT, LoseCountTTT FROM tictactoe WHERE user_id = {crossuser.id}")
                            add1victorycross = cursor.fetchall()
                            ajouter1victoirecroix = int(add1victorycross[0][0])+1
                            sql = ("UPDATE tictactoe SET VictoryCountTTT = ? WHERE user_id = ?")
                            val = (ajouter1victoirecroix, crossuser.id)
                            cursor.execute(sql, val)
                            db.commit()

                            cursor.execute(f"SELECT VictoryCountTTT, LoseCountTTT FROM tictactoe WHERE user_id = {circleuser.id}")
                            add1defeatcircle = cursor.fetchall()
                            ajouter1défaitecercle = int(add1defeatcircle[0][1])+1
                            sql = ("UPDATE tictactoe SET LoseCountTTT = ? WHERE user_id = ?")
                            val = (ajouter1défaitecercle, circleuser.id)
                            cursor.execute(sql, val)
                            db.commit()

                            return
                        
                        # Si circle gagne en diagonale positive

                        elif grille[x][y] == circle and grille[x+2][y+2] == circle and grille[x+4][y+4] == circle :
                            await rep.delete()
                            await tab.edit(content = f"{tableaucomplet}", components=[])
                            await ctx.channel.send(embed = embedfinjeucircle, components=[])

                            cursor.execute(f"SELECT VictoryCountTTT, LoseCountTTT FROM tictactoe WHERE user_id = {circleuser.id}")
                            add1victorycircle = cursor.fetchall()
                            ajouter1victoirecercle = int(add1victorycircle[0][0])+1
                            sql = ("UPDATE tictactoe SET VictoryCountTTT = ? WHERE user_id = ?")
                            val = (ajouter1victoirecercle, circleuser.id)
                            cursor.execute(sql, val)
                            db.commit()

                            cursor.execute(f"SELECT VictoryCountTTT, LoseCountTTT FROM tictactoe WHERE user_id = {crossuser.id}")
                            add1defeatcross = cursor.fetchall()
                            ajouter1défaitecroix = int(add1defeatcross[0][1])+1
                            sql = ("UPDATE tictactoe SET LoseCountTTT = ? WHERE user_id = ?")
                            val = (ajouter1défaitecroix, crossuser.id)
                            cursor.execute(sql, val)
                            db.commit()

                            return

                
                for x in range(len(grille)-4):
                    for y in range(4, len(grille[x])):
                        
                        # Si cross gagne en diagonale négative

                        if grille[x][y] == cross and grille[x+2][y-2] == cross and grille[x+4][y-4] == cross :
                            await rep.delete()
                            await tab.edit(content = f"{tableaucomplet}", components=[])
                            await ctx.channel.send(embed = embedfinjeucross, components=[])

                            cursor.execute(f"SELECT VictoryCountTTT, LoseCountTTT FROM tictactoe WHERE user_id = {crossuser.id}")
                            add1victorycross = cursor.fetchall()
                            ajouter1victoirecroix = int(add1victorycross[0][0])+1
                            sql = ("UPDATE tictactoe SET VictoryCountTTT = ? WHERE user_id = ?")
                            val = (ajouter1victoirecroix, crossuser.id)
                            cursor.execute(sql, val)
                            db.commit()

                            cursor.execute(f"SELECT VictoryCountTTT, LoseCountTTT FROM tictactoe WHERE user_id = {circleuser.id}")
                            add1defeatcircle = cursor.fetchall()
                            ajouter1défaitecercle = int(add1defeatcircle[0][1])+1
                            sql = ("UPDATE tictactoe SET LoseCountTTT = ? WHERE user_id = ?")
                            val = (ajouter1défaitecercle, circleuser.id)
                            cursor.execute(sql, val)
                            db.commit()

                            return
                        
                        # Si circle gagne en diagonale négative

                        elif grille[x][y] == circle and grille[x+2][y-2] == circle and grille[x+4][y-4] == circle :
                            await rep.delete()
                            await tab.edit(content = f"{tableaucomplet}", components=[])
                            await ctx.send(embed = embedfinjeucircle, components=[])

                            cursor.execute(f"SELECT VictoryCountTTT, LoseCountTTT FROM tictactoe WHERE user_id = {circleuser.id}")
                            add1victorycircle = cursor.fetchall()
                            ajouter1victoirecercle = int(add1victorycircle[0][0])+1
                            sql = ("UPDATE tictactoe SET VictoryCountTTT = ? WHERE user_id = ?")
                            val = (ajouter1victoirecercle, circleuser.id)
                            cursor.execute(sql, val)
                            db.commit()

                            cursor.execute(f"SELECT VictoryCountTTT, LoseCountTTT FROM tictactoe WHERE user_id = {crossuser.id}")
                            add1defeatcross = cursor.fetchall()
                            ajouter1défaitecroix = int(add1defeatcross[0][1])+1
                            sql = ("UPDATE tictactoe SET LoseCountTTT = ? WHERE user_id = ?")
                            val = (ajouter1défaitecroix, crossuser.id)
                            cursor.execute(sql, val)
                            db.commit()

                            return

                if grille[0][0] != number1 and grille[0][2] != number2 and grille[0][4] != number3 and grille[2][0] != number4 and grille[2][2] != number5 and grille[2][4] != number6 and grille[4][0] != number7 and grille[4][2] != number8 and grille[4][4] != number9 :
                    await rep.delete()
                    await tab.edit(content = f"{tableaucomplet}", components=[])
                    await ctx.channel.send(embed = embedfinjeuegalite, components=[])

                    return


def setup(client):
    client.add_cog(TicTacToeCommand(client))
    print("Tic Tac Toe command cog ready !")