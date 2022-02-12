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
import contextlib
from contextlib import suppress

db = sqlite3.connect("smallgames.sqlite") # Ouverture de la base de données
cursor = db.cursor()

class BattleShipCommand(commands.Cog):
    def __init__(self, client):
        self.client = client


    @cog_ext.cog_slash(name = "battleship", description = "Play BattleShip with a friend", options=[
        create_option(name = "other_player", description = "User you want to play with", option_type=6, required=True)
    ])
    async def battleship(self, ctx : SlashContext, other_player):

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
            ),
            create_button(
                style=ButtonStyle.blue,
                emoji="🔟",
                custom_id="ten",
                disabled=False
            )
            
        ]

        ButtonsLetters = [
            create_button(
                style=ButtonStyle.blue,
                emoji="🇦",
                custom_id="a",
                disabled=False
            ),
            create_button(
                style=ButtonStyle.blue,
                emoji='🇧',
                custom_id="b",
                disabled=False
            ),
            create_button(
                style=ButtonStyle.blue,
                emoji='🇨',
                custom_id="c",
                disabled=False
            ),
            create_button(
                style=ButtonStyle.blue,
                emoji="🇩",
                custom_id="d",
                disabled=False
            ),
            create_button(
                style=ButtonStyle.blue,
                emoji="🇪",
                custom_id="e",
                disabled=False
            ),
            create_button(
                style=ButtonStyle.blue,
                emoji="🇫",
                custom_id="f",
                disabled=False
            ),
            create_button(
                style=ButtonStyle.blue,
                emoji="🇬",
                custom_id="g",
                disabled=False
            ),
            create_button(
                style=ButtonStyle.blue,
                emoji="🇭",
                custom_id="h",
                disabled=False
            ),
            create_button(
                style=ButtonStyle.blue,
                emoji="🇮",
                custom_id="i",
                disabled=False
            ),
            create_button(
                style=ButtonStyle.blue,
                emoji="🇯",
                custom_id="j",
                disabled=False
            )
        ]

        HorVButtons = [
            create_button(
                style=ButtonStyle.blue,
                emoji='🇭',
                custom_id="horizontal",
                disabled=False
            ),
            create_button(
                style=ButtonStyle.blue,
                emoji='🇻',
                custom_id="vertical",
                disabled=False
            )
        ]

        CheckRow = create_actionrow(*ButtonCheck)

        NumberRow1 = create_actionrow(*ButtonsNumbers[0:5])
        NumberRow2 = create_actionrow(*ButtonsNumbers[5:])

        LetterRow1 = create_actionrow(*ButtonsLetters[0:5])
        LetterRow2 = create_actionrow(*ButtonsLetters[5:])

        NumberRow1Opponent = create_actionrow(*ButtonsNumbers[0:5])
        NumberRow2Opponent = create_actionrow(*ButtonsNumbers[5:])

        LetterRow1Opponent = create_actionrow(*ButtonsLetters[0:5])
        LetterRow2Opponent = create_actionrow(*ButtonsLetters[5:])

        HorVRow = create_actionrow(*HorVButtons)


        red = '🔴'
        yellow = ':yellow_circle:'
        white = '⚪'
        blue = '🔵'
        stop = '⬜'

        grille = [[white for i in range(11)] for j in range(11)]

        grille[0][0] = stop

        grille[0][1] = ':regional_indicator_a:'
        grille[0][2] = ':regional_indicator_b:'
        grille[0][3] = ':regional_indicator_c:'
        grille[0][4] = ':regional_indicator_d:'
        grille[0][5] = ':regional_indicator_e:'
        grille[0][6] = ':regional_indicator_f:'
        grille[0][7] = ':regional_indicator_g:'
        grille[0][8] = ':regional_indicator_h:'
        grille[0][9] = ':regional_indicator_i:'
        grille[0][10] = ':regional_indicator_j:'

        grille[1][0] = '1️⃣'
        grille[2][0] = '2️⃣'
        grille[3][0] = '3️⃣'
        grille[4][0] = '4️⃣'
        grille[5][0] = '5️⃣'
        grille[6][0] = '6️⃣'
        grille[7][0] = '7️⃣'
        grille[8][0] = '8️⃣'
        grille[9][0] = '9️⃣'
        grille[10][0] = '🔟'

        tab = ""
        for x in range(len(grille)):
            tab += "".join(grille[x]) + "\n"
        
        
        ### Tableau privé du challenger ###

        privatechallengergrille = [[white for i in range(11)] for j in range(11)]
        privatechallengergrille[0][0] = stop

        privatechallengergrille[0][1] = ':regional_indicator_a:'
        privatechallengergrille[0][2] = ':regional_indicator_b:'
        privatechallengergrille[0][3] = ':regional_indicator_c:'
        privatechallengergrille[0][4] = ':regional_indicator_d:'
        privatechallengergrille[0][5] = ':regional_indicator_e:'
        privatechallengergrille[0][6] = ':regional_indicator_f:'
        privatechallengergrille[0][7] = ':regional_indicator_g:'
        privatechallengergrille[0][8] = ':regional_indicator_h:'
        privatechallengergrille[0][9] = ':regional_indicator_i:'
        privatechallengergrille[0][10] = ':regional_indicator_j:'

        privatechallengergrille[1][0] = '1️⃣'
        privatechallengergrille[2][0] = '2️⃣'
        privatechallengergrille[3][0] = '3️⃣'
        privatechallengergrille[4][0] = '4️⃣'
        privatechallengergrille[5][0] = '5️⃣'
        privatechallengergrille[6][0] = '6️⃣'
        privatechallengergrille[7][0] = '7️⃣'
        privatechallengergrille[8][0] = '8️⃣'
        privatechallengergrille[9][0] = '9️⃣'
        privatechallengergrille[10][0] = '🔟'

        privatetabchallenger = ""
        for x in range(len(privatechallengergrille)):
            privatetabchallenger += "".join(privatechallengergrille[x]) + "\n"
        

        ### Tableau privé du challenged ###

        privatechallengedgrille = [[white for i in range(11)] for j in range(11)]
        privatechallengedgrille[0][0] = stop

        privatechallengedgrille[0][1] = ':regional_indicator_a:'
        privatechallengedgrille[0][2] = ':regional_indicator_b:'
        privatechallengedgrille[0][3] = ':regional_indicator_c:'
        privatechallengedgrille[0][4] = ':regional_indicator_d:'
        privatechallengedgrille[0][5] = ':regional_indicator_e:'
        privatechallengedgrille[0][6] = ':regional_indicator_f:'
        privatechallengedgrille[0][7] = ':regional_indicator_g:'
        privatechallengedgrille[0][8] = ':regional_indicator_h:'
        privatechallengedgrille[0][9] = ':regional_indicator_i:'
        privatechallengedgrille[0][10] = ':regional_indicator_j:'

        privatechallengedgrille[1][0] = '1️⃣'
        privatechallengedgrille[2][0] = '2️⃣'
        privatechallengedgrille[3][0] = '3️⃣'
        privatechallengedgrille[4][0] = '4️⃣'
        privatechallengedgrille[5][0] = '5️⃣'
        privatechallengedgrille[6][0] = '6️⃣'
        privatechallengedgrille[7][0] = '7️⃣'
        privatechallengedgrille[8][0] = '8️⃣'
        privatechallengedgrille[9][0] = '9️⃣'
        privatechallengedgrille[10][0] = '🔟'

        privatetabchallenged = ""
        for x in range(len(privatechallengedgrille)):
            privatetabchallenged += "".join(privatechallengedgrille[x]) + "\n"

        
        ### Tableau public du challenger ###

        publicchallengergrille = [[white for i in range(11)] for j in range(11)]
        publicchallengergrille[0][0] = stop

        publicchallengergrille[0][1] = ':regional_indicator_a:'
        publicchallengergrille[0][2] = ':regional_indicator_b:'
        publicchallengergrille[0][3] = ':regional_indicator_c:'
        publicchallengergrille[0][4] = ':regional_indicator_d:'
        publicchallengergrille[0][5] = ':regional_indicator_e:'
        publicchallengergrille[0][6] = ':regional_indicator_f:'
        publicchallengergrille[0][7] = ':regional_indicator_g:'
        publicchallengergrille[0][8] = ':regional_indicator_h:'
        publicchallengergrille[0][9] = ':regional_indicator_i:'
        publicchallengergrille[0][10] = ':regional_indicator_j:'

        publicchallengergrille[1][0] = '1️⃣'
        publicchallengergrille[2][0] = '2️⃣'
        publicchallengergrille[3][0] = '3️⃣'
        publicchallengergrille[4][0] = '4️⃣'
        publicchallengergrille[5][0] = '5️⃣'
        publicchallengergrille[6][0] = '6️⃣'
        publicchallengergrille[7][0] = '7️⃣'
        publicchallengergrille[8][0] = '8️⃣'
        publicchallengergrille[9][0] = '9️⃣'
        publicchallengergrille[10][0] = '🔟'

        publictabchallenger = ""
        for x in range(len(publicchallengergrille)):
            publictabchallenger += "".join(publicchallengergrille[x]) + "\n"
        

        ### Tableau public du challenged ###

        publicchallengedgrille = [[white for i in range(11)] for j in range(11)]
        publicchallengedgrille[0][0] = stop

        publicchallengedgrille[0][1] = ':regional_indicator_a:'
        publicchallengedgrille[0][2] = ':regional_indicator_b:'
        publicchallengedgrille[0][3] = ':regional_indicator_c:'
        publicchallengedgrille[0][4] = ':regional_indicator_d:'
        publicchallengedgrille[0][5] = ':regional_indicator_e:'
        publicchallengedgrille[0][6] = ':regional_indicator_f:'
        publicchallengedgrille[0][7] = ':regional_indicator_g:'
        publicchallengedgrille[0][8] = ':regional_indicator_h:'
        publicchallengedgrille[0][9] = ':regional_indicator_i:'
        publicchallengedgrille[0][10] = ':regional_indicator_j:'

        publicchallengedgrille[1][0] = '1️⃣'
        publicchallengedgrille[2][0] = '2️⃣'
        publicchallengedgrille[3][0] = '3️⃣'
        publicchallengedgrille[4][0] = '4️⃣'
        publicchallengedgrille[5][0] = '5️⃣'
        publicchallengedgrille[6][0] = '6️⃣'
        publicchallengedgrille[7][0] = '7️⃣'
        publicchallengedgrille[8][0] = '8️⃣'
        publicchallengedgrille[9][0] = '9️⃣'
        publicchallengedgrille[10][0] = '🔟'

        publictabchallenged = ""
        for x in range(len(publicchallengedgrille)):
            publictabchallenged += "".join(publicchallengedgrille[x]) + "\n"

        ChallengerUser = ctx.author

        if ChallengerUser == other_player :
            embedsolo = discord.Embed(description = "You can't play with yourself", 
                                    colour = discord.Colour.dark_green())

            await ctx.send(embed = embedsolo)

            return

        elif other_player.bot or ChallengerUser.bot :
            embedsolo = discord.Embed(description = "Nobody can play with a bot", 
                                    colour = discord.Colour.dark_blue())

            await ctx.send(embed = embedsolo)

            return

        
        else:

            EmbedStartGame = discord.Embed(description = f"<@{other_player.id}>, <@{ChallengerUser.id}> want to play a **BattleShip** game against you. You got 15 seconds to accept the invitation !", 
                                            colour = discord.Colour.blurple())

            rep = await ctx.send(embed = EmbedStartGame, components=[CheckRow])

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

            cursor.execute(f"SELECT VictoryCountBTS, LoseCountBTS FROM battleship WHERE user_id = {ChallengerUser.id}")
            DonneeChallengerExist = cursor.fetchone() # vérif si les données existent pour le joueur jaune

            if DonneeChallengerExist is None : # si les données existent pas pour le joueur jaune
                
                sql = ("INSERT INTO battleship(user_id, VictoryCountBTS, LoseCountBTS) VALUES(?,?,?)")
                val = (ChallengerUser.id, zerovictoire, zerodefaite)
                cursor.execute(sql, val)
                db.commit()
                pass


            # Rouge

            cursor.execute(f"SELECT VictoryCountBTS, LoseCountBTS FROM battleship WHERE user_id = {other_player.id}")
            DonneeChallengedExist = cursor.fetchone() # vérif si les données existent pour le joueur rouge

            if DonneeChallengedExist is None : # si les données existent pas pour le joueur rouge
                
                sql = ("INSERT INTO battleship(user_id, VictoryCountBTS, LoseCountBTS) VALUES(?,?,?)")
                val = (other_player.id, zerovictoire, zerodefaite)
                cursor.execute(sql, val)
                db.commit()
                pass

            ### Suite du code ###

            # Embeds et messages de préparation des bateaux #

            EmbedJeu = discord.Embed(description = f"Alright !! Let's go !\nCheck your DM's\nYou have to place your boats !\n\n`1 boat of 5\n1 boat of 4\n2 boats of 3\n1 boat of 2`",
                                    colour = discord.Colour.blurple())
            EmbedsPlacement = {

                "EmbedPlacement5" : discord.Embed(description = "We will start to the 5 cases boat.\n\nDo you want the boat Horizontal or Vertical ?",
                                                colour = discord.Colour.blurple()),
                "EmbedPlacement4" : discord.Embed(description = "Now we place the boat of 4 cases\n\nDo you want the boat Horizontal or Vertical ?",
                                                colour = discord.Colour.blurple()),
                "EmbedPlacement31" : discord.Embed(description = "Now, the first 3 cases boat.\n\nDo you want the boat Horizontal or Vertical ?",
                                                colour = discord.Colour.blurple()),
                "EmbedPlacement32" : discord.Embed(description = "Now, the second 3 cases boat.\n\nDo you want the boat Horizontal or Vertical ?",
                                                colour = discord.Colour.blurple()),
                "EmbedPlacement2" : discord.Embed(description = "Finally, the last, the 2 cases boat\n\nDo you want the boat Horizontal or Vertical ?",
                                                colour = discord.Colour.blurple())
            }
            

            EmbedPlacementChannel = discord.Embed(title = "Please Wait",
                                                description = "Players are placing their boat",
                                                colour = discord.Colour.blurple())
            

            EmbedReglesChannel = discord.Embed(title = "Game rules :",
                                                description = f"On player 1 move, the player 2 grid will be updated.\nIf player 1 plays, it will hit the player 2 grid, so it will be updated on player two grid.",
                                                colour = discord.Colour.blurple())
            EmbedReglesChannel.add_field(name = f"{red}",
                                        value = "if the ship sank",
                                        inline = False)
            EmbedReglesChannel.add_field(name = f"{yellow}",
                                        value = "if the player fired at the enemy ship but it doesn't sank",
                                        inline = False)
            EmbedReglesChannel.add_field(name = f"{blue}",
                                        value = "If the player missed the ship (flowed)",
                                        inline = False)
            EmbedReglesChannel.add_field(name = f"{white}",
                                        value = "The player didn't fired in this location",
                                        inline = False)
            
            
            
            await rep.edit(embed = EmbedJeu, components=[])
            
            ChallengerChannelGrille = await ctx.channel.send(f"<@{ChallengerUser.id}> public grid :\n{publictabchallenger}")
            ChallengedChannelGrille = await ctx.channel.send(f"<@{other_player.id}> public grid :\n{publictabchallenged}")
            EmplacementChannelTemporaire = await ctx.channel.send(embed = EmbedPlacementChannel)


            ChallengerPublicGrille = await ChallengerUser.send(ChallengedChannelGrille.content)
            ChallengedPublicGrille = await other_player.send(ChallengerChannelGrille.content)



            ChallengerPrivateGrille = await ChallengerUser.send(privatetabchallenger)
            ChallengedPrivateGrille = await other_player.send(privatetabchallenged)


            EmbedEmplacementLigne = discord.Embed(title = "In which line ?",
                                            description = "React to the right reaction to choose your line",
                                            colour = discord.Colour.blurple())

            EmbedEmplacementLigneFin = discord.Embed(title = "Where to finish ?",
                                            description = "React to the right reaction to choose your end line",
                                            colour = discord.Colour.blurple())


            EmbedEmplacementColonne = discord.Embed(title = "In which column ?",
                                            description = "React to the right reaction to choose your column",
                                            colour = discord.Colour.blurple())

            EmbedEmplacementColonneFin = discord.Embed(title = "Where to finish ?",
                                            description = "React to the right reaction to choose your end column",
                                            colour = discord.Colour.blurple())

            EmbedEmplacementImpossible = discord.Embed(title = "Impossible to place your boat",
                                                    description = "The task to place again this boat will restart",
                                                    colour = discord.Colour.red())

            
            # Embed et variables une fois la game commencée #

            EmbedChoosing1stplayer = discord.Embed(title = "Choosing 1st player",
                                                    description = "I will tell you who start in just a sec",
                                                    colour = discord.Colour.orange())

            Embed1stPlayer = discord.Embed(description = f"<@{ChallengerUser.id}> **__NOW__**\n<@{other_player.id}> **NEXT**",
                                            colour = discord.Colour.purple())
            
            Embed2ndPlayer = discord.Embed(description = f"<@{other_player.id}> **__NOW__**\n<@{ChallengerUser.id}> **NEXT**",
                                            colour = discord.Colour.purple())

            EmbedTouchLine = discord.Embed(title = "line to touch",
                                        description = "React to the right reaction to choose your hit line",
                                        colour = discord.Colour.blurple())
            
            EmbedTouchColumn = discord.Embed(title = "Column to touch",
                                        description = "React to the right reaction to choose your hit column",
                                        colour = discord.Colour.blurple())
            PlacementBateaux = {
            'Bateau5Challenger' : [],
            'Bateau4Challenger' : [],
            'Bateau31Challenger' : [],
            'Bateau32Challenger' : [],
            'Bateau2Challenger' : [],
            
            'Bateau5Challenged' : [],
            'Bateau4Challenged' : [],
            'Bateau31Challenged' : [],
            'Bateau32Challenged' : [],
            'Bateau2Challenged' : []
            }

            # Embed pour la fin de game, connaitre gagnant #

            EmbedChallengerWinner = discord.Embed(description = f"<@{ChallengerUser.id}> WON !!\nGG WP to <@{ChallengerUser.id}> and <@{other_player.id}>",
                                                colour = discord.Colour.green())
            
            EmbedChallengedWinner = discord.Embed(description = f"<@{other_player.id}> WON !!\nGG WP to <@{other_player.id}> and <@{ChallengerUser.id}>",
                                                colour = discord.Colour.green())

            EmbedPrivateWin = discord.Embed(title = "You won !",
                                                    description = f"GG WP to <@{ChallengerUser.id}> and <@{other_player.id}>",
                                                    colour = discord.Colour.green())
            
            EmbedPrivateLost = discord.Embed(title = "You lost !",
                                                    description = f"GG WP to <@{ChallengerUser.id}> and <@{other_player.id}>",
                                                    colour = discord.Colour.red())

            ### Affichage des règles et du temps de chargement en boucle ###

            async def ExplicationChannel():
                TourChangementRegles = 1
                while TourChangementRegles < 3:
                    await asyncio.sleep(10)
                    await EmplacementChannelTemporaire.edit(embed = EmbedReglesChannel)
                    await asyncio.sleep(10)
                    await EmplacementChannelTemporaire.edit(embed = EmbedPlacementChannel)
                    TourChangementRegles = TourChangementRegles + 1

            
            async def ChallengerTask():
                
                BateauAPoser = 0
                while BateauAPoser < 5 :
                    if BateauAPoser == 0 :
                        TailleBateau = 5
                        TourBateau = 0
                    elif BateauAPoser == 1:
                        TailleBateau = 4
                        TourBateau = 0
                    elif BateauAPoser == 2 or BateauAPoser == 3:
                        TailleBateau = 3
                        if BateauAPoser == 2:
                            TourBateau = 1
                        else:
                            TourBateau = 2
                    elif BateauAPoser == 4 :
                        TailleBateau = 2
                        TourBateau = 0
                    

                    if TourBateau != 0:
                        MessagePlacementChallengerTemporaire = await ChallengerUser.send(embed = EmbedsPlacement[f'EmbedPlacement{TailleBateau}{TourBateau}'], components=[HorVRow])
                    else:
                        MessagePlacementChallengerTemporaire = await ChallengerUser.send(embed = EmbedsPlacement[f'EmbedPlacement{TailleBateau}'], components=[HorVRow])

                    def CheckBateau5(ctx: ComponentContext):
                        return ctx.component_id == "horizontal" or ctx.component_id == "vertical"

                    HorVPayload : ComponentContext = await manage_components.wait_for_component(self.client, messages=MessagePlacementChallengerTemporaire, components=HorVRow, check=CheckBateau5)

                    HorizontalOuVertical = []

                    if HorVPayload.component_id == "horizontal":
                        HorizontalOuVertical.append(1)
                    else:
                        HorizontalOuVertical.append(0)
                    
                    await HorVPayload.edit_origin(embed = EmbedEmplacementLigne, components = [NumberRow1, NumberRow2])

                    def PositionLigne(ctx : ComponentContext):
                        return ctx.custom_id == "one" or ctx.custom_id == "two" or ctx.custom_id == "three" or ctx.custom_id == "four" or ctx.custom_id == "five" or ctx.custom_id == "six" or ctx.custom_id == "seven" or ctx.custom_id == "eight" or ctx.custom_id == "nine" or ctx.custom_id == "ten"
                    
                    LignePayload : ComponentContext = await manage_components.wait_for_component(self.client, messages=MessagePlacementChallengerTemporaire, components = [NumberRow1, NumberRow2], check=PositionLigne)

                    if LignePayload.component_id == "one":
                        LigneChallenger = 1
                    elif LignePayload.component_id == "two":
                        LigneChallenger = 2
                    elif LignePayload.component_id == "three":
                        LigneChallenger = 3
                    elif LignePayload.component_id == "four":
                        LigneChallenger = 4
                    elif LignePayload.component_id == "five":
                        LigneChallenger = 5
                    elif LignePayload.component_id == "six":
                        LigneChallenger = 6
                    elif LignePayload.component_id == "seven":
                        LigneChallenger = 7
                    elif LignePayload.component_id == "eight":
                        LigneChallenger = 8
                    elif LignePayload.component_id == "nine":
                        LigneChallenger = 9
                    elif LignePayload.component_id == "ten":
                        LigneChallenger = 10
                    
                    await LignePayload.edit_origin(embed = EmbedEmplacementColonne, components = [LetterRow1, LetterRow2])

                    def PositionColonne(ctx : ComponentContext):
                        return ctx.custom_id == "a" or ctx.custom_id == "b" or ctx.custom_id == "c" or ctx.custom_id == "d" or ctx.custom_id == "e" or ctx.custom_id == "f" or ctx.custom_id == "g" or ctx.custom_id == "h" or ctx.custom_id == "i" or ctx.custom_id == "j"

                    ColonnePayload : ComponentContext = await manage_components.wait_for_component(self.client, messages=MessagePlacementChallengerTemporaire, components = [LetterRow1, LetterRow2], check=PositionColonne)

                    if ColonnePayload.custom_id == "a":
                        colonneChallenger = 1
                    elif ColonnePayload.custom_id == "b":
                        colonneChallenger = 2
                    elif ColonnePayload.custom_id == "c":
                        colonneChallenger = 3
                    elif ColonnePayload.custom_id == "d":
                        colonneChallenger = 4
                    elif ColonnePayload.custom_id == "e":
                        colonneChallenger = 5
                    elif ColonnePayload.custom_id == "f":
                        colonneChallenger = 6
                    elif ColonnePayload.custom_id == "g":
                        colonneChallenger = 7
                    elif ColonnePayload.custom_id == "h":
                        colonneChallenger = 8
                    elif ColonnePayload.custom_id == "i":
                        colonneChallenger = 9
                    elif ColonnePayload.custom_id == "j":
                        colonneChallenger = 10

                    if HorizontalOuVertical[0] == 1 :

                        while True:
                            for CheckIndex in range(1, TailleBateau):
                                if (colonneChallenger-CheckIndex >= 1) and (colonneChallenger+CheckIndex <= 10):
                                    try:
                                        if (privatechallengergrille[LigneChallenger][colonneChallenger-CheckIndex] == white) and (privatechallengergrille[LigneChallenger][colonneChallenger+CheckIndex] == white):
                                            Choix = True
                                        else:
                                            Choix = False
                                            break
                                    except IndexError:
                                        Choix = False
                                        break
                                else :
                                    Choix = False
                                    break

                            if Choix == True :

                                BateauAPoser += 1

                                for colonnefintour in range(1,11):
                                    if colonnefintour < 6 :
                                        if (colonneChallenger-(TailleBateau-1) == colonnefintour) or (colonneChallenger+(TailleBateau-1) == colonnefintour) :
                                            LetterRow1['components'][colonnefintour-1]['disabled'] = False
                                        else :
                                            LetterRow1['components'][colonnefintour-1]['disabled'] = True
                                            LetterRow1['components'][colonnefintour-1]['style'] = ButtonStyle.grey
                                    else:
                                        if (colonneChallenger-(TailleBateau-1) == colonnefintour) or (colonneChallenger+(TailleBateau-1) == colonnefintour) :
                                            LetterRow2['components'][colonnefintour%6]['disabled'] = False
                                        else :
                                            LetterRow2['components'][colonnefintour%6]['disabled'] = True
                                            LetterRow2['components'][colonnefintour%6]['style'] = ButtonStyle.grey
                                
                                await ColonnePayload.edit_origin(embed = EmbedEmplacementColonneFin, components = [LetterRow1, LetterRow2])

                                def PositionColonneFinChallenger(ctx: ComponentContext):
                                    return ctx.custom_id == "a" or ctx.custom_id == "b" or ctx.custom_id == "c" or ctx.custom_id == "d" or ctx.custom_id == "e" or ctx.custom_id == "f" or ctx.custom_id == "g" or ctx.custom_id == "h" or ctx.custom_id == "i" or ctx.custom_id == "j"
                                
                                ColonneFinPayload : ComponentContext = await manage_components.wait_for_component(self.client, messages=MessagePlacementChallengerTemporaire, components = [LetterRow1, LetterRow2], check=PositionColonneFinChallenger)

                                if ColonneFinPayload.custom_id == "a" :
                                    ColonneFinChallenger = 1
                                elif ColonneFinPayload.custom_id == "b":
                                    ColonneFinChallenger = 2
                                elif ColonneFinPayload.custom_id == "c":
                                    ColonneFinChallenger = 3
                                elif ColonneFinPayload.custom_id == "d":
                                    ColonneFinChallenger = 4
                                elif ColonneFinPayload.custom_id == "e":
                                    ColonneFinChallenger = 5
                                elif ColonneFinPayload.custom_id == "f":
                                    ColonneFinChallenger = 6
                                elif ColonneFinPayload.custom_id == "g":
                                    ColonneFinChallenger = 7
                                elif ColonneFinPayload.custom_id == "h":
                                    ColonneFinChallenger = 8
                                elif ColonneFinPayload.custom_id == "i":
                                    ColonneFinChallenger = 9
                                elif ColonneFinPayload.custom_id == "j":
                                    ColonneFinChallenger = 10
                                
                                if ColonneFinChallenger < colonneChallenger:
                                    VariableTempo = ColonneFinChallenger
                                    ColonneFinChallenger = colonneChallenger
                                    colonneChallenger = VariableTempo

                                while colonneChallenger <= ColonneFinChallenger:
                                    privatechallengergrille[LigneChallenger][colonneChallenger] = yellow
                                    if TourBateau != 0:
                                        PlacementBateaux[f'Bateau{TailleBateau}{TourBateau}Challenger'].append(LigneChallenger)
                                        PlacementBateaux[f'Bateau{TailleBateau}{TourBateau}Challenger'].append(colonneChallenger)
                                    else:
                                        PlacementBateaux[f'Bateau{TailleBateau}Challenger'].append(LigneChallenger)
                                        PlacementBateaux[f'Bateau{TailleBateau}Challenger'].append(colonneChallenger)
                                    colonneChallenger = colonneChallenger+1

                                privatetabchallenger = ""
                                for x in range(len(privatechallengergrille)):
                                    privatetabchallenger += "".join(privatechallengergrille[x]) + "\n"

                                await ChallengerPrivateGrille.edit(content = privatetabchallenger)

                                await MessagePlacementChallengerTemporaire.delete()

                                for button in range(1,11):
                                    if button < 6 :
                                        LetterRow1['components'][button-1]['disabled'] = False
                                        LetterRow1['components'][button-1]['style'] = ButtonStyle.blue
                                    else:
                                        LetterRow2['components'][button%6]['disabled'] = False
                                        LetterRow2['components'][button%6]['style'] = ButtonStyle.blue
                                
                                break
                                
                            else:

                                await MessagePlacementChallengerTemporaire.delete()

                                for CheckIndex in range(1, TailleBateau):
                                    if colonneChallenger-CheckIndex >= 1 :
                                        try:
                                            if privatechallengergrille[LigneChallenger][colonneChallenger-CheckIndex] == white :
                                                Choix1 = True
                                            else:
                                                Choix1 = False
                                                break
                                        except IndexError:
                                            Choix1 = False
                                            break
                                    else :
                                        Choix1 = False
                                        break
                                
                                if Choix1 == False :
                                    for CheckIndex in range(1, TailleBateau):
                                        if colonneChallenger+CheckIndex <= 10 :
                                            try:
                                                if privatechallengergrille[LigneChallenger][colonneChallenger+CheckIndex] == white :
                                                    Choix2 = True
                                                else:
                                                    Choix2 = False
                                                    break
                                            except IndexError:
                                                Choix2 = False
                                                break
                                        else :
                                            Choix2 = False
                                            break
                                
                                else :

                                    BateauAPoser += 1

                                    ColonneFinChallenger = colonneChallenger-(TailleBateau-1)

                                    while ColonneFinChallenger <= colonneChallenger:
                                        privatechallengergrille[LigneChallenger][ColonneFinChallenger] = yellow
                                        if TourBateau != 0:
                                            PlacementBateaux[f'Bateau{TailleBateau}{TourBateau}Challenger'].append(LigneChallenger)
                                            PlacementBateaux[f'Bateau{TailleBateau}{TourBateau}Challenger'].append(ColonneFinChallenger)
                                        else:
                                            PlacementBateaux[f'Bateau{TailleBateau}Challenger'].append(LigneChallenger)
                                            PlacementBateaux[f'Bateau{TailleBateau}Challenger'].append(ColonneFinChallenger)
                                        ColonneFinChallenger = ColonneFinChallenger+1
                                    
                                    privatetabchallenger = ""
                                    for x in range(len(privatechallengergrille)):
                                        privatetabchallenger += "".join(privatechallengergrille[x]) + "\n"

                                    await ChallengerPrivateGrille.edit(content = privatetabchallenger)

                                    break

                                if Choix1 == False and Choix2 == True:

                                    BateauAPoser += 1

                                    ColonneFinChallenger = colonneChallenger+(TailleBateau-1)

                                    while colonneChallenger <= ColonneFinChallenger:
                                        privatechallengergrille[LigneChallenger][colonneChallenger] = yellow
                                        if TourBateau != 0:
                                            PlacementBateaux[f'Bateau{TailleBateau}{TourBateau}Challenger'].append(LigneChallenger)
                                            PlacementBateaux[f'Bateau{TailleBateau}{TourBateau}Challenger'].append(colonneChallenger)
                                        else:
                                            PlacementBateaux[f'Bateau{TailleBateau}Challenger'].append(LigneChallenger)
                                            PlacementBateaux[f'Bateau{TailleBateau}Challenger'].append(colonneChallenger)
                                        colonneChallenger = colonneChallenger+1
                                    
                                    privatetabchallenger = ""
                                    for x in range(len(privatechallengergrille)):
                                        privatetabchallenger += "".join(privatechallengergrille[x]) + "\n"

                                    await ChallengerPrivateGrille.edit(content = privatetabchallenger)

                                    break

                                if Choix1 == False and Choix2 == False :

                                    if TourBateau != 0:
                                        PlacementBateaux[f'Bateau{TailleBateau}{TourBateau}Challenger'] = []
                                        PlacementBateaux[f'Bateau{TailleBateau}{TourBateau}Challenger'] = []
                                    else:
                                        PlacementBateaux[f'Bateau{TailleBateau}Challenger'] = []
                                        PlacementBateaux[f'Bateau{TailleBateau}Challenger'] = []

                                    MessagePlacementChallengerTemporaire = await ChallengerUser.send(embed = EmbedEmplacementImpossible)
                                    await asyncio.sleep(2)

                                    await MessagePlacementChallengerTemporaire.delete()

                                    break
                    else:

                        while True:
                            for CheckIndex in range(1, TailleBateau):
                                if (LigneChallenger-CheckIndex >=1) and (LigneChallenger+CheckIndex <=10) :
                                    try:
                                        if (privatechallengergrille[LigneChallenger-CheckIndex][colonneChallenger] == white) and (privatechallengergrille[LigneChallenger+CheckIndex][colonneChallenger] == white) :
                                            Choix = True
                                        else:
                                            Choix = False
                                            break
                                    except IndexError:
                                        Choix = False
                                        break
                                else :
                                    Choix = False
                                    break
                            
                            if Choix == True :

                                BateauAPoser += 1

                                for lignefintour in range(1,11):
                                    if lignefintour < 6 :
                                        if (LigneChallenger-(TailleBateau-1) == lignefintour) or (LigneChallenger+(TailleBateau-1) == lignefintour) :
                                            NumberRow1['components'][lignefintour-1]['disabled'] = False
                                        else :
                                            NumberRow1['components'][lignefintour-1]['disabled'] = True
                                            NumberRow1['components'][lignefintour-1]['style'] = ButtonStyle.grey
                                    else:
                                        if (LigneChallenger-(TailleBateau-1) == lignefintour) or (LigneChallenger+(TailleBateau-1) == lignefintour) :
                                            NumberRow2['components'][lignefintour%6]['disabled'] = False
                                        else :
                                            NumberRow2['components'][lignefintour%6]['disabled'] = True
                                            NumberRow2['components'][lignefintour%6]['style'] = ButtonStyle.grey

                                await ColonnePayload.edit_origin(embed = EmbedEmplacementLigneFin, components=[NumberRow1,NumberRow2])

                                def PositionLigneFinChallenger(ctx: ComponentContext):
                                    return ctx.custom_id == "one" or ctx.custom_id == "two" or ctx.custom_id == "three" or ctx.custom_id == "four" or ctx.custom_id == "five" or ctx.custom_id == "six" or ctx.custom_id == "seven" or ctx.custom_id == "eight" or ctx.custom_id == "nine" or ctx.custom_id == "ten"
                                
                                LigneFinPayload : ComponentContext = await manage_components.wait_for_component(self.client, messages=MessagePlacementChallengerTemporaire, components = [NumberRow1, NumberRow2], check=PositionLigneFinChallenger)
                                
                                if LigneFinPayload.custom_id == "one" :
                                    LigneFinChallenger = 1
                                elif LigneFinPayload.custom_id == "two":
                                    LigneFinChallenger = 2
                                elif LigneFinPayload.custom_id == "three":
                                    LigneFinChallenger = 3
                                elif LigneFinPayload.custom_id == "four":
                                    LigneFinChallenger = 4
                                elif LigneFinPayload.custom_id == "five":
                                    LigneFinChallenger = 5
                                elif LigneFinPayload.custom_id == "six":
                                    LigneFinChallenger = 6
                                elif LigneFinPayload.custom_id == "seven":
                                    LigneFinChallenger = 7
                                elif LigneFinPayload.custom_id == "eight":
                                    LigneFinChallenger = 8
                                elif LigneFinPayload.custom_id == "nine":
                                    LigneFinChallenger = 9
                                elif LigneFinPayload.custom_id == "ten":
                                    LigneFinChallenger = 10

                                if LigneFinChallenger < LigneChallenger:
                                    VariableTempo = LigneFinChallenger
                                    LigneFinChallenger = LigneChallenger
                                    LigneChallenger = VariableTempo

                                while LigneChallenger <= LigneFinChallenger:
                                    privatechallengergrille[LigneChallenger][colonneChallenger] = yellow
                                    if TourBateau != 0:
                                        PlacementBateaux[f'Bateau{TailleBateau}{TourBateau}Challenger'].append(LigneChallenger)
                                        PlacementBateaux[f'Bateau{TailleBateau}{TourBateau}Challenger'].append(colonneChallenger)
                                    else :
                                        PlacementBateaux[f'Bateau{TailleBateau}Challenger'].append(LigneChallenger)
                                        PlacementBateaux[f'Bateau{TailleBateau}Challenger'].append(colonneChallenger)
                                    LigneChallenger = LigneChallenger+1

                                privatetabchallenger = ""
                                for x in range(len(privatechallengergrille)):
                                    privatetabchallenger += "".join(privatechallengergrille[x]) + "\n"

                                await ChallengerPrivateGrille.edit(content = privatetabchallenger)

                                await MessagePlacementChallengerTemporaire.delete()

                                for button in range(1,11):
                                    if button < 6 :
                                        NumberRow1['components'][button-1]['disabled'] = False
                                        NumberRow1['components'][button-1]['style'] = ButtonStyle.blue
                                    else:
                                        NumberRow2['components'][button%6]['disabled'] = False
                                        NumberRow2['components'][button%6]['style'] = ButtonStyle.blue

                                break

                            else :

                                await MessagePlacementChallengerTemporaire.delete()

                                for CheckIndex in range(1, TailleBateau):
                                    if LigneChallenger-CheckIndex >=1 :
                                        try:
                                            if privatechallengergrille[LigneChallenger-CheckIndex][colonneChallenger] == white :
                                                Choix1 = True
                                            else:
                                                Choix1 = False
                                                break
                                        except IndexError:
                                            Choix1 = False
                                            break
                                    else :
                                        Choix1 = False
                                        break
                                
                                if Choix1 == False :

                                    for CheckIndex in range(1, TailleBateau):
                                        if LigneChallenger+CheckIndex <=10 :
                                            try:
                                                if privatechallengergrille[LigneChallenger+CheckIndex][colonneChallenger] == white :
                                                    Choix2 = True
                                                else:
                                                    Choix2 = False
                                                    break
                                            except IndexError:
                                                Choix2 = False
                                                break
                                        else :
                                            Choix2 = False
                                            break
                                
                                else :

                                    BateauAPoser += 1

                                    LigneFinChallenger = LigneChallenger-(TailleBateau-1)

                                    while LigneFinChallenger <= LigneChallenger:
                                        privatechallengergrille[LigneFinChallenger][colonneChallenger] = yellow
                                        if TourBateau != 0:
                                            PlacementBateaux[f'Bateau{TailleBateau}{TourBateau}Challenger'].append(LigneFinChallenger)
                                            PlacementBateaux[f'Bateau{TailleBateau}{TourBateau}Challenger'].append(colonneChallenger)
                                        else:
                                            PlacementBateaux[f'Bateau{TailleBateau}Challenger'].append(LigneFinChallenger)
                                            PlacementBateaux[f'Bateau{TailleBateau}Challenger'].append(colonneChallenger)
                                        LigneFinChallenger = LigneFinChallenger+1
                                    
                                    privatetabchallenger = ""
                                    for x in range(len(privatechallengergrille)):
                                        privatetabchallenger += "".join(privatechallengergrille[x]) + "\n"

                                    await ChallengerPrivateGrille.edit(content = privatetabchallenger)

                                    break

                                if Choix1 == False and Choix2 == True :

                                    BateauAPoser += 1

                                    LigneFinChallenger = LigneChallenger+(TailleBateau-1)

                                    while LigneChallenger <= LigneFinChallenger:
                                        privatechallengergrille[LigneChallenger][colonneChallenger] = yellow
                                        if TourBateau != 0:
                                            PlacementBateaux[f'Bateau{TailleBateau}{TourBateau}Challenger'].append(LigneChallenger)
                                            PlacementBateaux[f'Bateau{TailleBateau}{TourBateau}Challenger'].append(colonneChallenger)
                                        else :
                                            PlacementBateaux[f'Bateau{TailleBateau}Challenger'].append(LigneChallenger)
                                            PlacementBateaux[f'Bateau{TailleBateau}Challenger'].append(colonneChallenger)
                                        LigneChallenger = LigneChallenger+1
                                    
                                    privatetabchallenger = ""
                                    for x in range(len(privatechallengergrille)):
                                        privatetabchallenger += "".join(privatechallengergrille[x]) + "\n"

                                    await ChallengerPrivateGrille.edit(content = privatetabchallenger)

                                    break

                                if Choix1 == False and Choix2 == False :

                                    if TourBateau != 0:
                                        PlacementBateaux[f'Bateau{TailleBateau}{TourBateau}Challenger'] = []
                                        PlacementBateaux[f'Bateau{TailleBateau}{TourBateau}Challenger'] = []
                                    else:
                                        PlacementBateaux[f'Bateau{TailleBateau}Challenger'] = []
                                        PlacementBateaux[f'Bateau{TailleBateau}Challenger'] = []

                                    MessagePlacementChallengerTemporaire = await ChallengerUser.send(embed = EmbedEmplacementImpossible)
                                    await asyncio.sleep(2)

                                    await MessagePlacementChallengerTemporaire.delete()

                                    break


            async def ChallengedTask():
                
                BateauAPoser = 0
                while BateauAPoser < 5 :
                    if BateauAPoser == 0 :
                        TailleBateau = 5
                        TourBateau = 0
                    elif BateauAPoser == 1:
                        TailleBateau = 4
                        TourBateau = 0
                    elif BateauAPoser == 2 or BateauAPoser == 3:
                        TailleBateau = 3
                        if BateauAPoser == 2:
                            TourBateau = 1
                        else:
                            TourBateau = 2
                    elif BateauAPoser == 4 :
                        TailleBateau = 2
                        TourBateau = 0
                    

                    if TourBateau != 0:
                        MessagePlacementChallengedTemporaire = await other_player.send(embed = EmbedsPlacement[f'EmbedPlacement{TailleBateau}{TourBateau}'], components=[HorVRow])
                    else:
                        MessagePlacementChallengedTemporaire = await other_player.send(embed = EmbedsPlacement[f'EmbedPlacement{TailleBateau}'], components=[HorVRow])

                    def CheckBateau5(ctx: ComponentContext):
                        return ctx.component_id == "horizontal" or ctx.component_id == "vertical"

                    HorVPayload : ComponentContext = await manage_components.wait_for_component(self.client, messages=MessagePlacementChallengedTemporaire, components=HorVRow, check=CheckBateau5)

                    HorizontalOuVertical = []

                    if HorVPayload.component_id == "horizontal":
                        HorizontalOuVertical.append(1)
                    else:
                        HorizontalOuVertical.append(0)
                    
                    await HorVPayload.edit_origin(embed = EmbedEmplacementLigne, components = [NumberRow1Opponent, NumberRow2Opponent])

                    def PositionLigne(ctx : ComponentContext):
                        return ctx.custom_id == "one" or ctx.custom_id == "two" or ctx.custom_id == "three" or ctx.custom_id == "four" or ctx.custom_id == "five" or ctx.custom_id == "six" or ctx.custom_id == "seven" or ctx.custom_id == "eight" or ctx.custom_id == "nine" or ctx.custom_id == "ten"
                    
                    LignePayload : ComponentContext = await manage_components.wait_for_component(self.client, messages=MessagePlacementChallengedTemporaire, components = [NumberRow1Opponent, NumberRow2Opponent], check=PositionLigne)

                    if LignePayload.component_id == "one":
                        LigneChallenged = 1
                    elif LignePayload.component_id == "two":
                        LigneChallenged = 2
                    elif LignePayload.component_id == "three":
                        LigneChallenged = 3
                    elif LignePayload.component_id == "four":
                        LigneChallenged = 4
                    elif LignePayload.component_id == "five":
                        LigneChallenged = 5
                    elif LignePayload.component_id == "six":
                        LigneChallenged = 6
                    elif LignePayload.component_id == "seven":
                        LigneChallenged = 7
                    elif LignePayload.component_id == "eight":
                        LigneChallenged = 8
                    elif LignePayload.component_id == "nine":
                        LigneChallenged = 9
                    elif LignePayload.component_id == "ten":
                        LigneChallenged = 10
                    
                    await LignePayload.edit_origin(embed = EmbedEmplacementColonne, components = [LetterRow1Opponent, LetterRow2Opponent])

                    def PositionColonne(ctx : ComponentContext):
                        return ctx.custom_id == "a" or ctx.custom_id == "b" or ctx.custom_id == "c" or ctx.custom_id == "d" or ctx.custom_id == "e" or ctx.custom_id == "f" or ctx.custom_id == "g" or ctx.custom_id == "h" or ctx.custom_id == "i" or ctx.custom_id == "j"

                    ColonnePayload : ComponentContext = await manage_components.wait_for_component(self.client, messages=MessagePlacementChallengedTemporaire, components = [LetterRow1Opponent, LetterRow2Opponent], check=PositionColonne)

                    if ColonnePayload.custom_id == "a":
                        colonneChallenged = 1
                    elif ColonnePayload.custom_id == "b":
                        colonneChallenged = 2
                    elif ColonnePayload.custom_id == "c":
                        colonneChallenged = 3
                    elif ColonnePayload.custom_id == "d":
                        colonneChallenged = 4
                    elif ColonnePayload.custom_id == "e":
                        colonneChallenged = 5
                    elif ColonnePayload.custom_id == "f":
                        colonneChallenged = 6
                    elif ColonnePayload.custom_id == "g":
                        colonneChallenged = 7
                    elif ColonnePayload.custom_id == "h":
                        colonneChallenged = 8
                    elif ColonnePayload.custom_id == "i":
                        colonneChallenged = 9
                    elif ColonnePayload.custom_id == "j":
                        colonneChallenged = 10

                    if HorizontalOuVertical[0] == 1 :

                        while True:
                            for CheckIndex in range(1, TailleBateau):
                                if (colonneChallenged-CheckIndex >= 1) and (colonneChallenged+CheckIndex <= 10):
                                    try:
                                        if (privatechallengedgrille[LigneChallenged][colonneChallenged-CheckIndex] == white) and (privatechallengedgrille[LigneChallenged][colonneChallenged+CheckIndex] == white):
                                            Choix = True
                                        else:
                                            Choix = False
                                            break
                                    except IndexError:
                                        Choix = False
                                        break
                                else :
                                    Choix = False
                                    break

                            if Choix == True :

                                BateauAPoser += 1

                                for colonnefintour in range(1,11):
                                    if colonnefintour < 6 :
                                        if (colonneChallenged-(TailleBateau-1) == colonnefintour) or (colonneChallenged+(TailleBateau-1) == colonnefintour) :
                                            LetterRow1Opponent['components'][colonnefintour-1]['disabled'] = False
                                        else :
                                            LetterRow1Opponent['components'][colonnefintour-1]['disabled'] = True
                                            LetterRow1Opponent['components'][colonnefintour-1]['style'] = ButtonStyle.grey
                                    else:
                                        if (colonneChallenged-(TailleBateau-1) == colonnefintour) or (colonneChallenged+(TailleBateau-1) == colonnefintour) :
                                            LetterRow2Opponent['components'][colonnefintour%6]['disabled'] = False
                                        else :
                                            LetterRow2Opponent['components'][colonnefintour%6]['disabled'] = True
                                            LetterRow2Opponent['components'][colonnefintour%6]['style'] = ButtonStyle.grey
                                
                                await ColonnePayload.edit_origin(embed = EmbedEmplacementColonneFin, components = [LetterRow1Opponent, LetterRow2Opponent])

                                def PositionColonneFinChallenged(ctx: ComponentContext):
                                    return ctx.custom_id == "a" or ctx.custom_id == "b" or ctx.custom_id == "c" or ctx.custom_id == "d" or ctx.custom_id == "e" or ctx.custom_id == "f" or ctx.custom_id == "g" or ctx.custom_id == "h" or ctx.custom_id == "i" or ctx.custom_id == "j"
                                
                                ColonneFinPayload : ComponentContext = await manage_components.wait_for_component(self.client, messages=MessagePlacementChallengedTemporaire, components = [LetterRow1Opponent, LetterRow2Opponent], check=PositionColonneFinChallenged)

                                if ColonneFinPayload.custom_id == "a" :
                                    ColonneFinChallenged = 1
                                elif ColonneFinPayload.custom_id == "b":
                                    ColonneFinChallenged = 2
                                elif ColonneFinPayload.custom_id == "c":
                                    ColonneFinChallenged = 3
                                elif ColonneFinPayload.custom_id == "d":
                                    ColonneFinChallenged = 4
                                elif ColonneFinPayload.custom_id == "e":
                                    ColonneFinChallenged = 5
                                elif ColonneFinPayload.custom_id == "f":
                                    ColonneFinChallenged = 6
                                elif ColonneFinPayload.custom_id == "g":
                                    ColonneFinChallenged = 7
                                elif ColonneFinPayload.custom_id == "h":
                                    ColonneFinChallenged = 8
                                elif ColonneFinPayload.custom_id == "i":
                                    ColonneFinChallenged = 9
                                elif ColonneFinPayload.custom_id == "j":
                                    ColonneFinChallenged = 10
                                
                                if ColonneFinChallenged < colonneChallenged:
                                    VariableTempo = ColonneFinChallenged
                                    ColonneFinChallenged = colonneChallenged
                                    colonneChallenged = VariableTempo

                                while colonneChallenged <= ColonneFinChallenged:
                                    privatechallengedgrille[LigneChallenged][colonneChallenged] = yellow
                                    if TourBateau != 0:
                                        PlacementBateaux[f'Bateau{TailleBateau}{TourBateau}Challenged'].append(LigneChallenged)
                                        PlacementBateaux[f'Bateau{TailleBateau}{TourBateau}Challenged'].append(colonneChallenged)
                                    else:
                                        PlacementBateaux[f'Bateau{TailleBateau}Challenged'].append(LigneChallenged)
                                        PlacementBateaux[f'Bateau{TailleBateau}Challenged'].append(colonneChallenged)
                                    colonneChallenged = colonneChallenged+1

                                privatetabChallenged = ""
                                for x in range(len(privatechallengedgrille)):
                                    privatetabChallenged += "".join(privatechallengedgrille[x]) + "\n"

                                await ChallengedPrivateGrille.edit(content = privatetabChallenged)

                                await MessagePlacementChallengedTemporaire.delete()

                                for button in range(1,11):
                                    if button < 6 :
                                        LetterRow1Opponent['components'][button-1]['disabled'] = False
                                        LetterRow1Opponent['components'][button-1]['style'] = ButtonStyle.blue
                                    else:
                                        LetterRow2Opponent['components'][button%6]['disabled'] = False
                                        LetterRow2Opponent['components'][button%6]['style'] = ButtonStyle.blue
                                
                                break
                                
                            else:

                                await MessagePlacementChallengedTemporaire.delete()

                                for CheckIndex in range(1, TailleBateau):
                                    if colonneChallenged-CheckIndex >= 1 :
                                        try:
                                            if privatechallengedgrille[LigneChallenged][colonneChallenged-CheckIndex] == white :
                                                Choix1 = True
                                            else:
                                                Choix1 = False
                                                break
                                        except IndexError:
                                            Choix1 = False
                                            break
                                    else :
                                        Choix1 = False
                                        break
                                
                                if Choix1 == False :
                                    for CheckIndex in range(1, TailleBateau):
                                        if colonneChallenged+CheckIndex <= 10 :
                                            try:
                                                if privatechallengedgrille[LigneChallenged][colonneChallenged+CheckIndex] == white :
                                                    Choix2 = True
                                                else:
                                                    Choix2 = False
                                                    break
                                            except IndexError:
                                                Choix2 = False
                                                break
                                        else :
                                            Choix2 = False
                                            break
                                
                                else :

                                    BateauAPoser += 1

                                    ColonneFinChallenged = colonneChallenged-(TailleBateau-1)

                                    while ColonneFinChallenged <= colonneChallenged:
                                        privatechallengedgrille[LigneChallenged][ColonneFinChallenged] = yellow
                                        if TourBateau != 0:
                                            PlacementBateaux[f'Bateau{TailleBateau}{TourBateau}Challenged'].append(LigneChallenged)
                                            PlacementBateaux[f'Bateau{TailleBateau}{TourBateau}Challenged'].append(ColonneFinChallenged)
                                        else:
                                            PlacementBateaux[f'Bateau{TailleBateau}Challenged'].append(LigneChallenged)
                                            PlacementBateaux[f'Bateau{TailleBateau}Challenged'].append(ColonneFinChallenged)
                                        ColonneFinChallenged = ColonneFinChallenged+1
                                    
                                    privatetabChallenged = ""
                                    for x in range(len(privatechallengedgrille)):
                                        privatetabChallenged += "".join(privatechallengedgrille[x]) + "\n"

                                    await ChallengedPrivateGrille.edit(content = privatetabChallenged)

                                    break

                                if Choix1 == False and Choix2 == True:

                                    BateauAPoser += 1

                                    ColonneFinChallenged = colonneChallenged+(TailleBateau-1)

                                    while colonneChallenged <= ColonneFinChallenged:
                                        privatechallengedgrille[LigneChallenged][colonneChallenged] = yellow
                                        if TourBateau != 0:
                                            PlacementBateaux[f'Bateau{TailleBateau}{TourBateau}Challenged'].append(LigneChallenged)
                                            PlacementBateaux[f'Bateau{TailleBateau}{TourBateau}Challenged'].append(colonneChallenged)
                                        else:
                                            PlacementBateaux[f'Bateau{TailleBateau}Challenged'].append(LigneChallenged)
                                            PlacementBateaux[f'Bateau{TailleBateau}Challenged'].append(colonneChallenged)
                                        colonneChallenged = colonneChallenged+1
                                    
                                    privatetabChallenged = ""
                                    for x in range(len(privatechallengedgrille)):
                                        privatetabChallenged += "".join(privatechallengedgrille[x]) + "\n"

                                    await ChallengedPrivateGrille.edit(content = privatetabChallenged)

                                    break

                                if Choix1 == False and Choix2 == False :

                                    if TourBateau != 0:
                                        PlacementBateaux[f'Bateau{TailleBateau}{TourBateau}Challenged'] = []
                                        PlacementBateaux[f'Bateau{TailleBateau}{TourBateau}Challenged'] = []
                                    else:
                                        PlacementBateaux[f'Bateau{TailleBateau}Challenged'] = []
                                        PlacementBateaux[f'Bateau{TailleBateau}Challenged'] = []

                                    MessagePlacementChallengedTemporaire = await other_player.send(embed = EmbedEmplacementImpossible)
                                    await asyncio.sleep(2)

                                    await MessagePlacementChallengedTemporaire.delete()

                                    break
                    else:

                        while True:
                            for CheckIndex in range(1, TailleBateau):
                                if (LigneChallenged-CheckIndex >=1) and (LigneChallenged+CheckIndex <=10) :
                                    try:
                                        if (privatechallengedgrille[LigneChallenged-CheckIndex][colonneChallenged] == white) and (privatechallengedgrille[LigneChallenged+CheckIndex][colonneChallenged] == white) :
                                            Choix = True
                                        else:
                                            Choix = False
                                            break
                                    except IndexError:
                                        Choix = False
                                        break
                                else :
                                    Choix = False
                                    break
                            
                            if Choix == True :

                                BateauAPoser += 1

                                for lignefintour in range(1,11):
                                    if lignefintour < 6 :
                                        if (LigneChallenged-(TailleBateau-1) == lignefintour) or (LigneChallenged+(TailleBateau-1) == lignefintour) :
                                            NumberRow1Opponent['components'][lignefintour-1]['disabled'] = False
                                        else :
                                            NumberRow1Opponent['components'][lignefintour-1]['disabled'] = True
                                            NumberRow1Opponent['components'][lignefintour-1]['style'] = ButtonStyle.grey
                                    else:
                                        if (LigneChallenged-(TailleBateau-1) == lignefintour) or (LigneChallenged+(TailleBateau-1) == lignefintour) :
                                            NumberRow2Opponent['components'][lignefintour%6]['disabled'] = False
                                        else :
                                            NumberRow2Opponent['components'][lignefintour%6]['disabled'] = True
                                            NumberRow2Opponent['components'][lignefintour%6]['style'] = ButtonStyle.grey

                                await ColonnePayload.edit_origin(embed = EmbedEmplacementLigneFin, components=[NumberRow1Opponent,NumberRow2Opponent])

                                def PositionLigneFinChallenged(ctx: ComponentContext):
                                    return ctx.custom_id == "one" or ctx.custom_id == "two" or ctx.custom_id == "three" or ctx.custom_id == "four" or ctx.custom_id == "five" or ctx.custom_id == "six" or ctx.custom_id == "seven" or ctx.custom_id == "eight" or ctx.custom_id == "nine" or ctx.custom_id == "ten"
                                
                                LigneFinPayload : ComponentContext = await manage_components.wait_for_component(self.client, messages=MessagePlacementChallengedTemporaire, components = [NumberRow1Opponent, NumberRow2Opponent], check=PositionLigneFinChallenged)
                                
                                if LigneFinPayload.custom_id == "one" :
                                    LigneFinChallenged = 1
                                elif LigneFinPayload.custom_id == "two":
                                    LigneFinChallenged = 2
                                elif LigneFinPayload.custom_id == "three":
                                    LigneFinChallenged = 3
                                elif LigneFinPayload.custom_id == "four":
                                    LigneFinChallenged = 4
                                elif LigneFinPayload.custom_id == "five":
                                    LigneFinChallenged = 5
                                elif LigneFinPayload.custom_id == "six":
                                    LigneFinChallenged = 6
                                elif LigneFinPayload.custom_id == "seven":
                                    LigneFinChallenged = 7
                                elif LigneFinPayload.custom_id == "eight":
                                    LigneFinChallenged = 8
                                elif LigneFinPayload.custom_id == "nine":
                                    LigneFinChallenged = 9
                                elif LigneFinPayload.custom_id == "ten":
                                    LigneFinChallenged = 10

                                if LigneFinChallenged < LigneChallenged:
                                    VariableTempo = LigneFinChallenged
                                    LigneFinChallenged = LigneChallenged
                                    LigneChallenged = VariableTempo

                                while LigneChallenged <= LigneFinChallenged:
                                    privatechallengedgrille[LigneChallenged][colonneChallenged] = yellow
                                    if TourBateau != 0:
                                        PlacementBateaux[f'Bateau{TailleBateau}{TourBateau}Challenged'].append(LigneChallenged)
                                        PlacementBateaux[f'Bateau{TailleBateau}{TourBateau}Challenged'].append(colonneChallenged)
                                    else :
                                        PlacementBateaux[f'Bateau{TailleBateau}Challenged'].append(LigneChallenged)
                                        PlacementBateaux[f'Bateau{TailleBateau}Challenged'].append(colonneChallenged)
                                    LigneChallenged = LigneChallenged+1

                                privatetabChallenged = ""
                                for x in range(len(privatechallengedgrille)):
                                    privatetabChallenged += "".join(privatechallengedgrille[x]) + "\n"

                                await ChallengedPrivateGrille.edit(content = privatetabChallenged)

                                await MessagePlacementChallengedTemporaire.delete()

                                for button in range(1,11):
                                    if button < 6 :
                                        NumberRow1Opponent['components'][button-1]['disabled'] = False
                                        NumberRow1Opponent['components'][button-1]['style'] = ButtonStyle.blue
                                    else:
                                        NumberRow2Opponent['components'][button%6]['disabled'] = False
                                        NumberRow2Opponent['components'][button%6]['style'] = ButtonStyle.blue

                                break

                            else :

                                await MessagePlacementChallengedTemporaire.delete()

                                for CheckIndex in range(1, TailleBateau):
                                    if LigneChallenged-CheckIndex >=1 :
                                        try:
                                            if privatechallengedgrille[LigneChallenged-CheckIndex][colonneChallenged] == white :
                                                Choix1 = True
                                            else:
                                                Choix1 = False
                                                break
                                        except IndexError:
                                            Choix1 = False
                                            break
                                    else :
                                        Choix1 = False
                                        break
                                
                                if Choix1 == False :

                                    for CheckIndex in range(1, TailleBateau):
                                        if LigneChallenged+CheckIndex <=10 :
                                            try:
                                                if privatechallengedgrille[LigneChallenged+CheckIndex][colonneChallenged] == white :
                                                    Choix2 = True
                                                else:
                                                    Choix2 = False
                                                    break
                                            except IndexError:
                                                Choix2 = False
                                                break
                                        else :
                                            Choix2 = False
                                            break
                                
                                else :

                                    BateauAPoser += 1

                                    LigneFinChallenged = LigneChallenged-(TailleBateau-1)

                                    while LigneFinChallenged <= LigneChallenged:
                                        privatechallengedgrille[LigneFinChallenged][colonneChallenged] = yellow
                                        if TourBateau != 0:
                                            PlacementBateaux[f'Bateau{TailleBateau}{TourBateau}Challenged'].append(LigneFinChallenged)
                                            PlacementBateaux[f'Bateau{TailleBateau}{TourBateau}Challenged'].append(colonneChallenged)
                                        else:
                                            PlacementBateaux[f'Bateau{TailleBateau}Challenged'].append(LigneFinChallenged)
                                            PlacementBateaux[f'Bateau{TailleBateau}Challenged'].append(colonneChallenged)
                                        LigneFinChallenged = LigneFinChallenged+1
                                    
                                    privatetabChallenged = ""
                                    for x in range(len(privatechallengedgrille)):
                                        privatetabChallenged += "".join(privatechallengedgrille[x]) + "\n"

                                    await ChallengedPrivateGrille.edit(content = privatetabChallenged)

                                    break

                                if Choix1 == False and Choix2 == True :

                                    BateauAPoser += 1

                                    LigneFinChallenged = LigneChallenged+(TailleBateau-1)

                                    while LigneChallenged <= LigneFinChallenged:
                                        privatechallengedgrille[LigneChallenged][colonneChallenged] = yellow
                                        if TourBateau != 0:
                                            PlacementBateaux[f'Bateau{TailleBateau}{TourBateau}Challenged'].append(LigneChallenged)
                                            PlacementBateaux[f'Bateau{TailleBateau}{TourBateau}Challenged'].append(colonneChallenged)
                                        else :
                                            PlacementBateaux[f'Bateau{TailleBateau}Challenged'].append(LigneChallenged)
                                            PlacementBateaux[f'Bateau{TailleBateau}Challenged'].append(colonneChallenged)
                                        LigneChallenged = LigneChallenged+1
                                    
                                    privatetabChallenged = ""
                                    for x in range(len(privatechallengedgrille)):
                                        privatetabChallenged += "".join(privatechallengedgrille[x]) + "\n"

                                    await ChallengedPrivateGrille.edit(content = privatetabChallenged)

                                    break

                                if Choix1 == False and Choix2 == False :

                                    if TourBateau != 0:
                                        PlacementBateaux[f'Bateau{TailleBateau}{TourBateau}Challenged'] = []
                                        PlacementBateaux[f'Bateau{TailleBateau}{TourBateau}Challenged'] = []
                                    else:
                                        PlacementBateaux[f'Bateau{TailleBateau}Challenged'] = []
                                        PlacementBateaux[f'Bateau{TailleBateau}Challenged'] = []

                                    MessagePlacementChallengedTemporaire = await other_player.send(embed = EmbedEmplacementImpossible)
                                    await asyncio.sleep(2)

                                    await MessagePlacementChallengedTemporaire.delete()

                                    break



            await asyncio.gather(ChallengerTask(), ChallengedTask(), ExplicationChannel())

            await rep.delete()
            await EmplacementChannelTemporaire.delete()

            Choosing1st = await ctx.channel.send(embed = EmbedChoosing1stplayer)
            
            await asyncio.sleep(2)

            JoueurChoisiAleatoirement = random.randint(0, 1)

            for t in range(201):

                if t%2 == JoueurChoisiAleatoirement :
                
                    for ligne in range(1, 11):
                        if not white in publicchallengedgrille[ligne]:
                            if ligne < 6 :
                                NumberRow1['components'][ligne-1]['disabled'] = True
                                NumberRow1['components'][ligne-1]['style'] = ButtonStyle.grey
                            else:
                                NumberRow2['components'][ligne%6]['disabled'] = True
                                NumberRow2['components'][ligne%6]['style'] = ButtonStyle.grey
                    
                    await Choosing1st.edit(embed = Embed1stPlayer)

                    MessageHitTemporaire = await ChallengerUser.send(embed = EmbedTouchLine, components=[NumberRow1, NumberRow2])

                    def AttenteTapChallengerLigne(ctx : ComponentContext):
                        return ctx.custom_id == "one" or ctx.custom_id == "two" or ctx.custom_id == "three" or ctx.custom_id == "four" or ctx.custom_id == "five" or ctx.custom_id == "six" or ctx.custom_id == "seven" or ctx.custom_id == "eight" or ctx.custom_id == "nine" or ctx.custom_id == "ten"
                    
                    TirJoueurLigne : ComponentContext = await manage_components.wait_for_component(self.client, messages=MessageHitTemporaire, components = [NumberRow1, NumberRow2], check=AttenteTapChallengerLigne)

                    if TirJoueurLigne.component_id == "one":
                        HitLine = 1
                    elif TirJoueurLigne.component_id == "two":
                        HitLine = 2
                    elif TirJoueurLigne.component_id == "three":
                        HitLine = 3
                    elif TirJoueurLigne.component_id == "four":
                        HitLine = 4
                    elif TirJoueurLigne.component_id == "five":
                        HitLine = 5
                    elif TirJoueurLigne.component_id == "six":
                        HitLine = 6
                    elif TirJoueurLigne.component_id == "seven":
                        HitLine = 7
                    elif TirJoueurLigne.component_id == "eight":
                        HitLine = 8
                    elif TirJoueurLigne.component_id == "nine":
                        HitLine = 9
                    elif TirJoueurLigne.component_id == "ten":
                        HitLine = 10

                    for colonne in range(1, 11):
                        if publicchallengedgrille[HitLine][colonne] != white:
                            if colonne < 6 :
                                LetterRow1['components'][colonne-1]['disabled'] = True
                                LetterRow1['components'][colonne-1]['style'] = ButtonStyle.grey
                            else:
                                LetterRow2['components'][colonne%6]['disabled'] = True
                                LetterRow2['components'][colonne%6]['style'] = ButtonStyle.grey

                    await TirJoueurLigne.edit_origin(embed = EmbedTouchColumn, components=[LetterRow1, LetterRow2])

                    def AttenteTapChallengerColonne(ctx : ComponentContext):
                        return ctx.custom_id == "a" or ctx.custom_id == "b" or ctx.custom_id == "c" or ctx.custom_id == "d" or ctx.custom_id == "e" or ctx.custom_id == "f" or ctx.custom_id == "g" or ctx.custom_id == "h" or ctx.custom_id == "i" or ctx.custom_id == "j"

                    TirJoueurColonne : ComponentContext = await manage_components.wait_for_component(self.client, messages=MessageHitTemporaire, components = [LetterRow1, LetterRow2], check=AttenteTapChallengerColonne)

                    if TirJoueurColonne.custom_id == "a":
                        HitColumn = 1
                    elif TirJoueurColonne.custom_id == "b":
                        HitColumn = 2
                    elif TirJoueurColonne.custom_id == "c":
                        HitColumn = 3
                    elif TirJoueurColonne.custom_id == "d":
                        HitColumn = 4
                    elif TirJoueurColonne.custom_id == "e":
                        HitColumn = 5
                    elif TirJoueurColonne.custom_id == "f":
                        HitColumn = 6
                    elif TirJoueurColonne.custom_id == "g":
                        HitColumn = 7
                    elif TirJoueurColonne.custom_id == "h":
                        HitColumn = 8
                    elif TirJoueurColonne.custom_id == "i":
                        HitColumn = 9
                    elif TirJoueurColonne.custom_id == "j":
                        HitColumn = 10

                    await MessageHitTemporaire.delete()

                    if privatechallengedgrille[HitLine][HitColumn] == white :
                        privatechallengedgrille[HitLine][HitColumn] = blue
                        publicchallengedgrille[HitLine][HitColumn] = blue
                    
                    elif privatechallengedgrille[HitLine][HitColumn] == yellow :
                        privatechallengedgrille[HitLine][HitColumn] = red
                        publicchallengedgrille[HitLine][HitColumn] = yellow
                    
                    if (privatechallengedgrille[PlacementBateaux[f'Bateau5Challenged'][0]][PlacementBateaux[f'Bateau5Challenged'][1]] == red) and (privatechallengedgrille[PlacementBateaux[f'Bateau5Challenged'][2]][PlacementBateaux[f'Bateau5Challenged'][3]] == red) and (privatechallengedgrille[PlacementBateaux[f'Bateau5Challenged'][4]][PlacementBateaux[f'Bateau5Challenged'][5]] == red) and (privatechallengedgrille[PlacementBateaux[f'Bateau5Challenged'][6]][PlacementBateaux[f'Bateau5Challenged'][7]] == red) and (privatechallengedgrille[PlacementBateaux[f'Bateau5Challenged'][8]][PlacementBateaux[f'Bateau5Challenged'][9]] == red) :
                        publicchallengedgrille[PlacementBateaux[f'Bateau5Challenged'][0]][PlacementBateaux[f'Bateau5Challenged'][1]] = red
                        publicchallengedgrille[PlacementBateaux[f'Bateau5Challenged'][2]][PlacementBateaux[f'Bateau5Challenged'][3]] = red
                        publicchallengedgrille[PlacementBateaux[f'Bateau5Challenged'][4]][PlacementBateaux[f'Bateau5Challenged'][5]] = red
                        publicchallengedgrille[PlacementBateaux[f'Bateau5Challenged'][6]][PlacementBateaux[f'Bateau5Challenged'][7]] = red
                        publicchallengedgrille[PlacementBateaux[f'Bateau5Challenged'][8]][PlacementBateaux[f'Bateau5Challenged'][9]] = red
                    
                    if (privatechallengedgrille[PlacementBateaux[f'Bateau4Challenged'][0]][PlacementBateaux[f'Bateau4Challenged'][1]] == red) and (privatechallengedgrille[PlacementBateaux[f'Bateau4Challenged'][2]][PlacementBateaux[f'Bateau4Challenged'][3]] == red) and (privatechallengedgrille[PlacementBateaux[f'Bateau4Challenged'][4]][PlacementBateaux[f'Bateau4Challenged'][5]] == red) and (privatechallengedgrille[PlacementBateaux[f'Bateau4Challenged'][6]][PlacementBateaux[f'Bateau4Challenged'][7]] == red) :
                        publicchallengedgrille[PlacementBateaux[f'Bateau4Challenged'][0]][PlacementBateaux[f'Bateau4Challenged'][1]] = red
                        publicchallengedgrille[PlacementBateaux[f'Bateau4Challenged'][2]][PlacementBateaux[f'Bateau4Challenged'][3]] = red
                        publicchallengedgrille[PlacementBateaux[f'Bateau4Challenged'][4]][PlacementBateaux[f'Bateau4Challenged'][5]] = red
                        publicchallengedgrille[PlacementBateaux[f'Bateau4Challenged'][6]][PlacementBateaux[f'Bateau4Challenged'][7]] = red
                    
                    if (privatechallengedgrille[PlacementBateaux[f'Bateau31Challenged'][0]][PlacementBateaux[f'Bateau31Challenged'][1]] == red) and (privatechallengedgrille[PlacementBateaux[f'Bateau31Challenged'][2]][PlacementBateaux[f'Bateau31Challenged'][3]] == red) and (privatechallengedgrille[PlacementBateaux[f'Bateau31Challenged'][4]][PlacementBateaux[f'Bateau31Challenged'][5]] == red) :
                        publicchallengedgrille[PlacementBateaux[f'Bateau31Challenged'][0]][PlacementBateaux[f'Bateau31Challenged'][1]] = red
                        publicchallengedgrille[PlacementBateaux[f'Bateau31Challenged'][2]][PlacementBateaux[f'Bateau31Challenged'][3]] = red
                        publicchallengedgrille[PlacementBateaux[f'Bateau31Challenged'][4]][PlacementBateaux[f'Bateau31Challenged'][5]] = red
                    
                    if (privatechallengedgrille[PlacementBateaux[f'Bateau32Challenged'][0]][PlacementBateaux[f'Bateau32Challenged'][1]] == red) and (privatechallengedgrille[PlacementBateaux[f'Bateau32Challenged'][2]][PlacementBateaux[f'Bateau32Challenged'][3]] == red) and (privatechallengedgrille[PlacementBateaux[f'Bateau32Challenged'][4]][PlacementBateaux[f'Bateau32Challenged'][5]] == red) :
                        publicchallengedgrille[PlacementBateaux[f'Bateau32Challenged'][0]][PlacementBateaux[f'Bateau32Challenged'][1]] = red
                        publicchallengedgrille[PlacementBateaux[f'Bateau32Challenged'][2]][PlacementBateaux[f'Bateau32Challenged'][3]] = red
                        publicchallengedgrille[PlacementBateaux[f'Bateau32Challenged'][4]][PlacementBateaux[f'Bateau32Challenged'][5]] = red

                    if (privatechallengedgrille[PlacementBateaux[f'Bateau2Challenged'][0]][PlacementBateaux[f'Bateau2Challenged'][1]] == red) and (privatechallengedgrille[PlacementBateaux[f'Bateau2Challenged'][2]][PlacementBateaux[f'Bateau2Challenged'][3]] == red) :
                        publicchallengedgrille[PlacementBateaux[f'Bateau2Challenged'][0]][PlacementBateaux[f'Bateau2Challenged'][1]] = red
                        publicchallengedgrille[PlacementBateaux[f'Bateau2Challenged'][2]][PlacementBateaux[f'Bateau2Challenged'][3]] = red
                    
                    publictabchallenged = ""
                    for x in range(len(publicchallengedgrille)):
                        publictabchallenged += "".join(publicchallengedgrille[x]) + "\n"

                    privatetabchallenged = ""
                    for x in range(len(privatechallengedgrille)):
                        privatetabchallenged += "".join(privatechallengedgrille[x]) + "\n"


                    await ChallengedChannelGrille.edit(content = f"<@{other_player.id}> public grid :\n{publictabchallenged}")
                    await ChallengerPublicGrille.edit(content = ChallengedChannelGrille.content)

                    await ChallengedPrivateGrille.edit(content = privatetabchallenged)

                    for button in range(1,11):
                        if button < 6 :
                            NumberRow1['components'][button-1]['disabled'] = False
                            NumberRow1['components'][button-1]['style'] = ButtonStyle.blue

                            LetterRow1['components'][button-1]['disabled'] = False
                            LetterRow1['components'][button-1]['style'] = ButtonStyle.blue
                        else:
                            NumberRow2['components'][button%6]['disabled'] = False
                            NumberRow2['components'][button%6]['style'] = ButtonStyle.blue

                            LetterRow2['components'][button%6]['disabled'] = False
                            LetterRow2['components'][button%6]['style'] = ButtonStyle.blue

                else:

                    for ligne in range(1, 11):
                        if not white in publicchallengergrille[ligne]:
                            if ligne < 6 :
                                NumberRow1Opponent['components'][ligne-1]['disabled'] = True
                                NumberRow1Opponent['components'][ligne-1]['style'] = ButtonStyle.grey
                            else:
                                NumberRow2Opponent['components'][ligne%6]['disabled'] = True
                                NumberRow2Opponent['components'][ligne%6]['style'] = ButtonStyle.grey
                    
                    await Choosing1st.edit(embed = Embed2ndPlayer)

                    MessageHitTemporaire = await other_player.send(embed = EmbedTouchLine, components=[NumberRow1Opponent, NumberRow2Opponent])

                    def AttenteTapChallengerLigne(ctx : ComponentContext):
                        return ctx.custom_id == "one" or ctx.custom_id == "two" or ctx.custom_id == "three" or ctx.custom_id == "four" or ctx.custom_id == "five" or ctx.custom_id == "six" or ctx.custom_id == "seven" or ctx.custom_id == "eight" or ctx.custom_id == "nine" or ctx.custom_id == "ten"
                    
                    TirJoueurLigne : ComponentContext = await manage_components.wait_for_component(self.client, messages=MessageHitTemporaire, components = [NumberRow1Opponent, NumberRow2Opponent], check=AttenteTapChallengerLigne)

                    if TirJoueurLigne.component_id == "one":
                        HitLine = 1
                    elif TirJoueurLigne.component_id == "two":
                        HitLine = 2
                    elif TirJoueurLigne.component_id == "three":
                        HitLine = 3
                    elif TirJoueurLigne.component_id == "four":
                        HitLine = 4
                    elif TirJoueurLigne.component_id == "five":
                        HitLine = 5
                    elif TirJoueurLigne.component_id == "six":
                        HitLine = 6
                    elif TirJoueurLigne.component_id == "seven":
                        HitLine = 7
                    elif TirJoueurLigne.component_id == "eight":
                        HitLine = 8
                    elif TirJoueurLigne.component_id == "nine":
                        HitLine = 9
                    elif TirJoueurLigne.component_id == "ten":
                        HitLine = 10

                    for colonne in range(1, 11):
                        if publicchallengergrille[HitLine][colonne] != white:
                            if colonne < 6 :
                                LetterRow1Opponent['components'][colonne-1]['disabled'] = True
                                LetterRow1Opponent['components'][colonne-1]['style'] = ButtonStyle.grey
                            else:
                                LetterRow2Opponent['components'][colonne%6]['disabled'] = True
                                LetterRow2Opponent['components'][colonne%6]['style'] = ButtonStyle.grey

                    await TirJoueurLigne.edit_origin(embed = EmbedTouchColumn, components=[LetterRow1Opponent, LetterRow2Opponent])

                    def AttenteTapChallengerColonne(ctx : ComponentContext):
                        return ctx.custom_id == "a" or ctx.custom_id == "b" or ctx.custom_id == "c" or ctx.custom_id == "d" or ctx.custom_id == "e" or ctx.custom_id == "f" or ctx.custom_id == "g" or ctx.custom_id == "h" or ctx.custom_id == "i" or ctx.custom_id == "j"

                    TirJoueurColonne : ComponentContext = await manage_components.wait_for_component(self.client, messages=MessageHitTemporaire, components = [LetterRow1Opponent, LetterRow2Opponent], check=AttenteTapChallengerColonne)

                    if TirJoueurColonne.custom_id == "a":
                        HitColumn = 1
                    elif TirJoueurColonne.custom_id == "b":
                        HitColumn = 2
                    elif TirJoueurColonne.custom_id == "c":
                        HitColumn = 3
                    elif TirJoueurColonne.custom_id == "d":
                        HitColumn = 4
                    elif TirJoueurColonne.custom_id == "e":
                        HitColumn = 5
                    elif TirJoueurColonne.custom_id == "f":
                        HitColumn = 6
                    elif TirJoueurColonne.custom_id == "g":
                        HitColumn = 7
                    elif TirJoueurColonne.custom_id == "h":
                        HitColumn = 8
                    elif TirJoueurColonne.custom_id == "i":
                        HitColumn = 9
                    elif TirJoueurColonne.custom_id == "j":
                        HitColumn = 10

                    await MessageHitTemporaire.delete()

                    if privatechallengergrille[HitLine][HitColumn] == white :
                        privatechallengergrille[HitLine][HitColumn] = blue
                        publicchallengergrille[HitLine][HitColumn] = blue
                    
                    elif privatechallengergrille[HitLine][HitColumn] == yellow :
                        privatechallengergrille[HitLine][HitColumn] = red
                        publicchallengergrille[HitLine][HitColumn] = yellow
                    
                    if (privatechallengergrille[PlacementBateaux[f'Bateau5Challenged'][0]][PlacementBateaux[f'Bateau5Challenged'][1]] == red) and (privatechallengergrille[PlacementBateaux[f'Bateau5Challenged'][2]][PlacementBateaux[f'Bateau5Challenged'][3]] == red) and (privatechallengergrille[PlacementBateaux[f'Bateau5Challenged'][4]][PlacementBateaux[f'Bateau5Challenged'][5]] == red) and (privatechallengergrille[PlacementBateaux[f'Bateau5Challenged'][6]][PlacementBateaux[f'Bateau5Challenged'][7]] == red) and (privatechallengergrille[PlacementBateaux[f'Bateau5Challenged'][8]][PlacementBateaux[f'Bateau5Challenged'][9]] == red) :
                        publicchallengergrille[PlacementBateaux[f'Bateau5Challenged'][0]][PlacementBateaux[f'Bateau5Challenged'][1]] = red
                        publicchallengergrille[PlacementBateaux[f'Bateau5Challenged'][2]][PlacementBateaux[f'Bateau5Challenged'][3]] = red
                        publicchallengergrille[PlacementBateaux[f'Bateau5Challenged'][4]][PlacementBateaux[f'Bateau5Challenged'][5]] = red
                        publicchallengergrille[PlacementBateaux[f'Bateau5Challenged'][6]][PlacementBateaux[f'Bateau5Challenged'][7]] = red
                        publicchallengergrille[PlacementBateaux[f'Bateau5Challenged'][8]][PlacementBateaux[f'Bateau5Challenged'][9]] = red
                    
                    if (privatechallengergrille[PlacementBateaux[f'Bateau4Challenged'][0]][PlacementBateaux[f'Bateau4Challenged'][1]] == red) and (privatechallengergrille[PlacementBateaux[f'Bateau4Challenged'][2]][PlacementBateaux[f'Bateau4Challenged'][3]] == red) and (privatechallengergrille[PlacementBateaux[f'Bateau4Challenged'][4]][PlacementBateaux[f'Bateau4Challenged'][5]] == red) and (privatechallengergrille[PlacementBateaux[f'Bateau4Challenged'][6]][PlacementBateaux[f'Bateau4Challenged'][7]] == red) :
                        publicchallengergrille[PlacementBateaux[f'Bateau4Challenged'][0]][PlacementBateaux[f'Bateau4Challenged'][1]] = red
                        publicchallengergrille[PlacementBateaux[f'Bateau4Challenged'][2]][PlacementBateaux[f'Bateau4Challenged'][3]] = red
                        publicchallengergrille[PlacementBateaux[f'Bateau4Challenged'][4]][PlacementBateaux[f'Bateau4Challenged'][5]] = red
                        publicchallengergrille[PlacementBateaux[f'Bateau4Challenged'][6]][PlacementBateaux[f'Bateau4Challenged'][7]] = red
                    
                    if (privatechallengergrille[PlacementBateaux[f'Bateau31Challenged'][0]][PlacementBateaux[f'Bateau31Challenged'][1]] == red) and (privatechallengergrille[PlacementBateaux[f'Bateau31Challenged'][2]][PlacementBateaux[f'Bateau31Challenged'][3]] == red) and (privatechallengergrille[PlacementBateaux[f'Bateau31Challenged'][4]][PlacementBateaux[f'Bateau31Challenged'][5]] == red) :
                        publicchallengergrille[PlacementBateaux[f'Bateau31Challenged'][0]][PlacementBateaux[f'Bateau31Challenged'][1]] = red
                        publicchallengergrille[PlacementBateaux[f'Bateau31Challenged'][2]][PlacementBateaux[f'Bateau31Challenged'][3]] = red
                        publicchallengergrille[PlacementBateaux[f'Bateau31Challenged'][4]][PlacementBateaux[f'Bateau31Challenged'][5]] = red
                    
                    if (privatechallengergrille[PlacementBateaux[f'Bateau32Challenged'][0]][PlacementBateaux[f'Bateau32Challenged'][1]] == red) and (privatechallengergrille[PlacementBateaux[f'Bateau32Challenged'][2]][PlacementBateaux[f'Bateau32Challenged'][3]] == red) and (privatechallengergrille[PlacementBateaux[f'Bateau32Challenged'][4]][PlacementBateaux[f'Bateau32Challenged'][5]] == red) :
                        publicchallengergrille[PlacementBateaux[f'Bateau32Challenged'][0]][PlacementBateaux[f'Bateau32Challenged'][1]] = red
                        publicchallengergrille[PlacementBateaux[f'Bateau32Challenged'][2]][PlacementBateaux[f'Bateau32Challenged'][3]] = red
                        publicchallengergrille[PlacementBateaux[f'Bateau32Challenged'][4]][PlacementBateaux[f'Bateau32Challenged'][5]] = red

                    if (privatechallengergrille[PlacementBateaux[f'Bateau2Challenged'][0]][PlacementBateaux[f'Bateau2Challenged'][1]] == red) and (privatechallengergrille[PlacementBateaux[f'Bateau2Challenged'][2]][PlacementBateaux[f'Bateau2Challenged'][3]] == red) :
                        publicchallengergrille[PlacementBateaux[f'Bateau2Challenged'][0]][PlacementBateaux[f'Bateau2Challenged'][1]] = red
                        publicchallengergrille[PlacementBateaux[f'Bateau2Challenged'][2]][PlacementBateaux[f'Bateau2Challenged'][3]] = red
                    
                    publictabchallenger = ""
                    for x in range(len(publicchallengergrille)):
                        publictabchallenger += "".join(publicchallengergrille[x]) + "\n"

                    privatetabchallenger = ""
                    for x in range(len(privatechallengergrille)):
                        privatetabchallenger += "".join(privatechallengergrille[x]) + "\n"


                    await ChallengerChannelGrille.edit(content = f"<@{ChallengerUser.id}> public grid :\n{publictabchallenger}")
                    await ChallengedPublicGrille.edit(content = ChallengerChannelGrille.content)

                    await ChallengerPrivateGrille.edit(content = privatetabchallenger)

                    for button in range(1,11):
                        if button < 6 :
                            NumberRow1Opponent['components'][button-1]['disabled'] = False
                            NumberRow1Opponent['components'][button-1]['style'] = ButtonStyle.blue

                            LetterRow1Opponent['components'][button-1]['disabled'] = False
                            LetterRow1Opponent['components'][button-1]['style'] = ButtonStyle.blue
                        else:
                            NumberRow2Opponent['components'][button%6]['disabled'] = False
                            NumberRow2Opponent['components'][button%6]['style'] = ButtonStyle.blue

                            LetterRow2Opponent['components'][button%6]['disabled'] = False
                            LetterRow2Opponent['components'][button%6]['style'] = ButtonStyle.blue

                if (yellow not in privatechallengedgrille[1]) and (yellow not in privatechallengedgrille[2]) and (yellow not in privatechallengedgrille[3]) and (yellow not in privatechallengedgrille[4]) and (yellow not in privatechallengedgrille[5]) and (yellow not in privatechallengedgrille[6]) and (yellow not in privatechallengedgrille[7]) and (yellow not in privatechallengedgrille[8]) and (yellow not in privatechallengedgrille[9]) and (yellow not in privatechallengedgrille[10]) :
                    
                    # BDD + fin game. Win pour Challenger
                    
                    await Choosing1st.edit(embed = EmbedChallengerWinner)

                    await ChallengerUser.send(embed = EmbedPrivateWin)
                    await other_player.send(embed = EmbedPrivateLost)

                    cursor.execute(f"SELECT VictoryCountBTS, LoseCountBTS FROM battleship WHERE user_id = {ChallengerUser.id}")
                    add1victorychallenger = cursor.fetchall()
                    ajouter1victoirechallenger = int(add1victorychallenger[0][0])+1
                    sql = ("UPDATE battleship SET VictoryCountBTS = ? WHERE user_id = ?")
                    val = (ajouter1victoirechallenger, ChallengerUser.id)
                    cursor.execute(sql, val)
                    db.commit()

                    cursor.execute(f"SELECT VictoryCountBTS, LoseCountBTS FROM battleship WHERE user_id = {other_player.id}")
                    add1defeatchallenged = cursor.fetchall()
                    ajouter1défaitechallenged = int(add1defeatchallenged[0][1])+1
                    sql = ("UPDATE battleship SET LoseCountBTS = ? WHERE user_id = ?")
                    val = (ajouter1défaitechallenged, other_player.id)
                    cursor.execute(sql, val)
                    db.commit()

                    return
                
                if (yellow not in privatechallengergrille[1]) and (yellow not in privatechallengergrille[2]) and (yellow not in privatechallengergrille[3]) and (yellow not in privatechallengergrille[4]) and (yellow not in privatechallengergrille[5]) and (yellow not in privatechallengergrille[6]) and (yellow not in privatechallengergrille[7]) and (yellow not in privatechallengergrille[8]) and (yellow not in privatechallengergrille[9]) and (yellow not in privatechallengergrille[10]) :
                    
                    # BDD + fin game. Win pour Challenged

                    await Choosing1st.edit(embed = EmbedChallengedWinner)

                    await other_player.send(embed = EmbedPrivateWin)
                    await ChallengerUser.send(embed = EmbedPrivateLost)

                    cursor.execute(f"SELECT VictoryCountBTS, LoseCountBTS FROM battleship WHERE user_id = {other_player.id}")
                    add1victorchallenged = cursor.fetchall()
                    ajouter1victoirechallenged = int(add1victorchallenged[0][0])+1
                    sql = ("UPDATE battleship SET VictoryCountBTS = ? WHERE user_id = ?")
                    val = (ajouter1victoirechallenged, other_player.id)
                    cursor.execute(sql, val)
                    db.commit()

                    cursor.execute(f"SELECT VictoryCountBTS, LoseCountBTS FROM battleship WHERE user_id = {ChallengerUser.id}")
                    add1defeatchallenger = cursor.fetchall()
                    ajouter1défaitechallenger = int(add1defeatchallenger[0][1])+1
                    sql = ("UPDATE battleship SET LoseCountBTS = ? WHERE user_id = ?")
                    val = (ajouter1défaitechallenger, ChallengerUser.id)
                    cursor.execute(sql, val)
                    db.commit()

                    return

def setup(client):
    client.add_cog(BattleShipCommand(client))
    print("BattleShip games command cog ready !")
