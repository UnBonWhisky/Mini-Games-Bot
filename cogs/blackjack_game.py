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

db = sqlite3.connect("smallgames.sqlite") # Ouverture de la base de données
cursor = db.cursor()

class BlackJackCommand(commands.Cog):
    def __init__(self, client):
        self.client = client

    
    @cog_ext.cog_slash(name = "blackjack", description = "Play Blackjack with up to 7 friends")
    async def blackjack(self, ctx : SlashContext):

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

        TirageCartesButtons = [
            create_button(
                style=ButtonStyle.blue,
                emoji="✅",
                custom_id="anotherone",
                disabled=False
            ),
            create_button(
                style=ButtonStyle.blue,
                emoji='❌',
                custom_id="stop",
                disabled=False
            )
        ]


        StartGameRow = create_actionrow(*StartGameButtons)
        TirageCartesRow = create_actionrow(*TirageCartesButtons)

        authorofgame = ctx.author

        cursor.execute(f"SELECT coins FROM mgcoins WHERE user_id = {authorofgame.id}")
        ProfileCoins = cursor.fetchone() # On récupère les infos de son argent si elles existent

        if ProfileCoins is None : # si le joueur n'a pas de "porte feuille"

            defaultnumbercoins = 100
                
            sql = ("INSERT INTO mgcoins(user_id, coins) VALUES(?,?)")
            val = (authorofgame.id, defaultnumbercoins)
            cursor.execute(sql, val)
            db.commit()
        
        cursor.execute(f"SELECT coins FROM mgcoins WHERE user_id = {authorofgame.id}")
        ProfileCoins = cursor.fetchone() # On récupère les infos de son argent si elles existent (mais elles existent maintenant)

        if int(ProfileCoins[0]) < 5:
            EmbedNotEnoughMoney = discord.Embed(description = "You don't have anough money to play a game of black jack. Try to use ``)mgcoins`` command to win 5 coins (1 time per day)",
                                                colour = discord.Colour.red())
            
            await ctx.send(embed = EmbedNotEnoughMoney)
            return

        playerlist = [authorofgame.id]

        EmbedStartGame = discord.Embed(title="BlackJack game !",
                                    description = f"You want to play a game of blackjack !\nOthers players have to react to this message with 🎰 to join the game\nYou can play between 2 and 8 players (the game launcher is already count as a player)\n\nPlayers list :\n<@{playerlist[0]}>",
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
            ListeJoueurs += f"<@{playerlist[x]}>\n"

        EmbedStartGame = discord.Embed(title="BlackJack game !",
                                description = f"You want to play a game of blackjack !\nOthers players have to react to this message with 🎰 to join the game\nYou can play between 2 and 8 players (the game launcher is already count as a player)\nTo play, you must to have **5 MG Coins** on your profile\n\nPlayers list :\n{ListeJoueurs}",
                                colour = discord.Colour.blurple())

        await stuff.edit_origin(embed = EmbedStartGame, components=[StartGameRow])

        while (len(playerlist) < 8) :

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

            EmbedStartGame = discord.Embed(title="BlackJack game !",
                                    description = f"You want to play a game of blackjack !\nOthers players have to react to this message with 🎰 to join the game\nYou can play between 2 and 8 players (the game launcher is already count as a player)\n\nPlayers list :\n{ListeJoueurs}",
                                    colour = discord.Colour.blurple())

            await stuff.edit_origin(embed = EmbedStartGame, components=[StartGameRow])
        
        NotEnoughMoneyList = []

        for x in range(len(playerlist)):

            cursor.execute(f"SELECT coins FROM mgcoins WHERE user_id = {playerlist[x]}")
            ProfileCoins = cursor.fetchone() # On récupère les infos de son argent si elles existent

            if ProfileCoins is None : # si le joueur n'a pas de "porte feuille"

                defaultnumbercoins = 100
                    
                sql = ("INSERT INTO mgcoins(user_id, coins) VALUES(?,?)")
                val = (playerlist[x], defaultnumbercoins)
                cursor.execute(sql, val)
                db.commit()
            
            cursor.execute(f"SELECT coins FROM mgcoins WHERE user_id = {playerlist[x]}")
            ProfileCoins = cursor.fetchone() # On récupère les infos de son argent si elles existent (mais elles existent maintenant)

            if int(ProfileCoins[0]) >=5 :
                RetirerProfileCoins = int(ProfileCoins[0])-5
                sql = ("UPDATE mgcoins SET coins = ? WHERE user_id = ?")
                val = (RetirerProfileCoins, playerlist[x])
                cursor.execute(sql, val)
                db.commit()
            
            else:
                NotEnoughMoneyList.append(playerlist[x])
                playerlist.remove(playerlist[x])

        ListeJoueursUnable = ""

        for x in range(len(NotEnoughMoneyList)):
            ListeJoueursUnable += f"<@{NotEnoughMoneyList[x]}>\n"

        if len(playerlist) < 2:

            EmbedNotEnoughPlayer = discord.Embed(title = "Game Cancelled",
                                                description = f"The only one player which had enough money to play was :\n<@{playerlist[0]}>\n\nThe list of players which have not enough money is : \n{ListeJoueursUnable}",
                                                colour = discord.Colour.red())
            EmbedNotEnoughPlayer.add_field(name = "For those which have not enough money",
                                        value = "try ``)mgcoins`` command to have 5 more MG Coins",
                                        inline = False)
            await MessageStartGame.edit(embed = EmbedNotEnoughPlayer, components=[])
            return
        
        elif (NotEnoughMoneyList != []) and (len(playerlist) >= 2) :

            EmbedImpossiblePlayers = discord.Embed(title = "Not all players accepted",
                                                description = f"Here is the list of players which don't have enough MG Coins to play :\n{ListeJoueursUnable}\nThe game will start but without these players",
                                                colour = discord.Colour.purple())
            EmbedImpossiblePlayers.add_field(name = "For those which have not enough money",
                                            value = "try ``)mgcoins`` command to have 5 more MG Coins",
                                            inline = False)
            await MessageStartGame.edit(embed = EmbedImpossiblePlayers, components=[])
            await asyncio.sleep(5)

        ListeJoueurs = ""
        for x in range(len(playerlist)):
            ListeJoueurs += f"<@{playerlist[x]}>\n"

        EmbedPartieEnCours = discord.Embed(title = "The game has started",
                                        description = f"List of players in game :\n{ListeJoueurs}",
                                        colour = discord.Colour.purple())
        
        await MessageStartGame.edit(embed = EmbedPartieEnCours, components=[])

        ListeDesJoueurs = {}

        for x in range(len(playerlist)):

            ListeDesJoueurs[f"playerlist[{x}]"] = await self.client.fetch_user(playerlist[x])
            await asyncio.sleep(0.1)

        GainPieces = len(playerlist)*5

        DifferentesCartes = ['Ace of Hearts','Ace of Spades','Ace of Clubs','Ace of Diamonds','2 of Hearts','2 of Spades','2 of Clubs','2 of Diamonds','3 of Hearts','3 of Spades','3 of Clubs','3 of Diamonds','4 of Hearts','4 of Spades','4 of Clubs','4 of Diamonds','5 of Hearts','5 of Spades','5 of Clubs','5 of Diamonds','6 of Hearts','6 of Spades','6 of Clubs','6 of Diamonds','7 of Hearts','7 of Spades','7 of Clubs','7 of Diamonds','8 of Hearts','8 of Spades','8 of Clubs','8 of Diamonds','9 of Hearts','9 of Spades','9 of Clubs','9 of Diamonds','10 of Hearts','10 of Spades','10 of Clubs','10 of Diamonds','Valet of Hearts','Valet of Spades','Valet of Clubs','Valet of Diamonds','Queen of Hearts','Queen of Spades','Queen of Clubs','Queen of Diamonds','King of Hearts','King of Spades','King of Clubs','King of Diamonds']

        CartesDesJoueurs = {}

        MessageIDJoueurs = {}

        for x in range(len(playerlist)):

            CartesDesJoueurs[f'cartespv{x}'] = []
            CartesDesJoueurs[f'cartespubliques{x}'] = []

            for y in range(2):
                CarteChoisie = random.randint(0, len(DifferentesCartes)-1)
                CartesDesJoueurs[f'cartespv{x}'].append(DifferentesCartes[CarteChoisie])
                CartesDesJoueurs[f'cartespubliques{x}'].append('*** of ***')
                DifferentesCartes.remove(DifferentesCartes[CarteChoisie])
        
        for x in range(len(playerlist)):

            joueuractuel = ListeDesJoueurs[f"playerlist[{0}]"]

            EmbedCarteTable = discord.Embed(title = "Cards on the table :",
                                            colour = discord.Colour.purple())
            EmbedCarteTable.set_footer(text = f"{joueuractuel}'s turn")
            
            for y in range(len(playerlist)):

                if x == y:

                    YourScore = 0

                    for cards in range(len(CartesDesJoueurs[f'cartespv{x}'])):

                        if CartesDesJoueurs[f'cartespv{x}'][cards][:2] == "Ac":
                            YourScore += 11
                        if CartesDesJoueurs[f'cartespv{x}'][cards][:2] == "2 ":
                            YourScore += 2
                        if CartesDesJoueurs[f'cartespv{x}'][cards][:2] == "3 ":
                            YourScore += 3
                        if CartesDesJoueurs[f'cartespv{x}'][cards][:2] == "4 ":
                            YourScore += 4
                        if CartesDesJoueurs[f'cartespv{x}'][cards][:2] == "5 ":
                            YourScore += 5
                        if CartesDesJoueurs[f'cartespv{x}'][cards][:2] == "6 ":
                            YourScore += 6
                        if CartesDesJoueurs[f'cartespv{x}'][cards][:2] == "7 ":
                            YourScore += 7
                        if CartesDesJoueurs[f'cartespv{x}'][cards][:2] == "8 ":
                            YourScore += 8
                        if CartesDesJoueurs[f'cartespv{x}'][cards][:2] == "9 ":
                            YourScore += 9
                        if CartesDesJoueurs[f'cartespv{x}'][cards][:2] == "10":
                            YourScore += 10
                        if CartesDesJoueurs[f'cartespv{x}'][cards][:2] == "Va":
                            YourScore += 10
                        if CartesDesJoueurs[f'cartespv{x}'][cards][:2] == "Qu":
                            YourScore += 10
                        if CartesDesJoueurs[f'cartespv{x}'][cards][:2] == "Ki":
                            YourScore += 10
                        
                    for cards in range(len(CartesDesJoueurs[f'cartespv{x}'])):
                        if (YourScore > 21) and (CartesDesJoueurs[f'cartespv{x}'][cards][:2] == "Ac"):
                            YourScore -= 10
                            CartesDesJoueurs[f'cartespv{x}'][cards][:2].lower()

                    YourCards = ""

                    for cards in range(len(CartesDesJoueurs[f'cartespv{x}'])):
                        YourCards += f"``{CartesDesJoueurs[f'cartespv{x}'][cards]}``\n"

                    EmbedCarteTable.add_field(name = "Your cards :",
                                            value = f"{YourCards}",
                                            inline = False)
                    EmbedCarteTable.set_author(name = f"Your score : {YourScore}")
                
                else:

                    OtherCards = ""

                    for cards in range(len(CartesDesJoueurs[f'cartespubliques{x}'])):
                        OtherCards += f"``{CartesDesJoueurs[f'cartespubliques{x}'][cards]}``\n"

                    otherplayer = ListeDesJoueurs[f"playerlist[{y}]"]

                    EmbedCarteTable.add_field(name = f"{otherplayer} cards :",
                                            value = f"{OtherCards}",
                                            inline = False)
                
            MessageCartes = await ListeDesJoueurs[f"playerlist[{x}]"].send(embed = EmbedCarteTable)
            MessageIDJoueurs[f'{x}{x}'] = MessageCartes.id
            MessageIDJoueurs[f'{x}{x+1}'] = MessageCartes.channel.id

        
        pointsjoueurs = []

        
        for tour in range(len(playerlist)):

            def CheckWantCard(ctx: ComponentContext):
                return (ctx.author_id == ListeDesJoueurs[f"playerlist[{tour}]"].id) and (ctx.custom_id == 'anotherone' or ctx.custom_id == 'stop')

            EmbedAddCardToList = discord.Embed(title = "Do you want to hit another card ?",
                                            description = ":white_check_mark: : Yes I want\n:x: : No I stop here",
                                            colour = discord.Colour.purple())

            MessageAddCard = await ListeDesJoueurs[f"playerlist[{tour}]"].send(embed = EmbedAddCardToList, components = [TirageCartesRow])

            await asyncio.sleep(0.1)
            
            try:
                TirerCarte : ComponentContext = await manage_components.wait_for_component(self.client, messages=MessageAddCard, components=TirageCartesRow, check=CheckWantCard, timeout=60.0)
            except asyncio.TimeoutError:
                EmbedTropTard = discord.Embed(description = "You took too much time to choose. I pass your turn",
                                            colour = discord.Colour.red())
                await MessageAddCard.edit(embed = EmbedTropTard)
                TirerCarte.custom_id == "stop"
            
            if TirerCarte.custom_id == "stop" :

                YourScore = 0

                for cards in range(len(CartesDesJoueurs[f'cartespv{tour}'])):

                    if CartesDesJoueurs[f'cartespv{tour}'][cards][:2] == "Ac":
                        YourScore += 11
                    if CartesDesJoueurs[f'cartespv{tour}'][cards][:2] == "2 ":
                        YourScore += 2
                    if CartesDesJoueurs[f'cartespv{tour}'][cards][:2] == "3 ":
                        YourScore += 3
                    if CartesDesJoueurs[f'cartespv{tour}'][cards][:2] == "4 ":
                        YourScore += 4
                    if CartesDesJoueurs[f'cartespv{tour}'][cards][:2] == "5 ":
                        YourScore += 5
                    if CartesDesJoueurs[f'cartespv{tour}'][cards][:2] == "6 ":
                        YourScore += 6
                    if CartesDesJoueurs[f'cartespv{tour}'][cards][:2] == "7 ":
                        YourScore += 7
                    if CartesDesJoueurs[f'cartespv{tour}'][cards][:2] == "8 ":
                        YourScore += 8
                    if CartesDesJoueurs[f'cartespv{tour}'][cards][:2] == "9 ":
                        YourScore += 9
                    if CartesDesJoueurs[f'cartespv{tour}'][cards][:2] == "10":
                        YourScore += 10
                    if CartesDesJoueurs[f'cartespv{tour}'][cards][:2] == "Va":
                        YourScore += 10
                    if CartesDesJoueurs[f'cartespv{tour}'][cards][:2] == "Qu":
                        YourScore += 10
                    if CartesDesJoueurs[f'cartespv{tour}'][cards][:2] == "Ki":
                        YourScore += 10
                    if CartesDesJoueurs[f'cartespv{tour}'][cards][:2] == "ac":
                        YourScore += 1
                    
                await MessageAddCard.delete()
                
                pointsjoueurs.append(YourScore)

            while TirerCarte.custom_id == "anotherone" :

                CarteChoisie = random.randint(0, len(DifferentesCartes)-1)
                CartesDesJoueurs[f'cartespv{tour}'].append(DifferentesCartes[CarteChoisie])
                CartesDesJoueurs[f'cartespubliques{tour}'].append(DifferentesCartes[CarteChoisie])
                DifferentesCartes.remove(DifferentesCartes[CarteChoisie])

                await MessageAddCard.delete()

                for joueur in range(len(playerlist)):

                    joueuractuel = ListeDesJoueurs[f"playerlist[{tour}]"]

                    EmbedCarteTable = discord.Embed(title = "Cards on the table :",
                                                    colour = discord.Colour.purple())
                    EmbedCarteTable.set_footer(text = f"{joueuractuel}'s turn")
                    
                    for rang in range(len(playerlist)):

                        if joueur == rang and joueur == tour :

                            YourScore = 0

                            for cards in range(len(CartesDesJoueurs[f'cartespv{tour}'])):

                                if CartesDesJoueurs[f'cartespv{tour}'][cards][:2] == "Ac":
                                    YourScore += 11
                                if CartesDesJoueurs[f'cartespv{tour}'][cards][:2] == "2 ":
                                    YourScore += 2
                                if CartesDesJoueurs[f'cartespv{tour}'][cards][:2] == "3 ":
                                    YourScore += 3
                                if CartesDesJoueurs[f'cartespv{tour}'][cards][:2] == "4 ":
                                    YourScore += 4
                                if CartesDesJoueurs[f'cartespv{tour}'][cards][:2] == "5 ":
                                    YourScore += 5
                                if CartesDesJoueurs[f'cartespv{tour}'][cards][:2] == "6 ":
                                    YourScore += 6
                                if CartesDesJoueurs[f'cartespv{tour}'][cards][:2] == "7 ":
                                    YourScore += 7
                                if CartesDesJoueurs[f'cartespv{tour}'][cards][:2] == "8 ":
                                    YourScore += 8
                                if CartesDesJoueurs[f'cartespv{tour}'][cards][:2] == "9 ":
                                    YourScore += 9
                                if CartesDesJoueurs[f'cartespv{tour}'][cards][:2] == "10":
                                    YourScore += 10
                                if CartesDesJoueurs[f'cartespv{tour}'][cards][:2] == "Va":
                                    YourScore += 10
                                if CartesDesJoueurs[f'cartespv{tour}'][cards][:2] == "Qu":
                                    YourScore += 10
                                if CartesDesJoueurs[f'cartespv{tour}'][cards][:2] == "Ki":
                                    YourScore += 10
                                if CartesDesJoueurs[f'cartespv{tour}'][cards][:2] == "ac":
                                    YourScore += 1
                                
                            for cards in range(len(CartesDesJoueurs[f'cartespv{tour}'])):
                                if (YourScore > 21) and (CartesDesJoueurs[f'cartespv{tour}'][cards][:2] == "Ac"):
                                    YourScore -= 10
                                    CartesDesJoueurs[f'cartespv{tour}'][cards] = CartesDesJoueurs[f'cartespv{tour}'][cards].lower()

                            YourCards = ""

                            for cards in range(len(CartesDesJoueurs[f'cartespv{tour}'])):
                                YourCards += f"``{CartesDesJoueurs[f'cartespv{tour}'][cards]}``\n"

                            EmbedCarteTable.add_field(name = "Your cards :",
                                                    value = f"{YourCards}",
                                                    inline = False)
                            EmbedCarteTable.set_author(name = f"Your score : {YourScore}")

                        elif joueur == rang and joueur != tour :

                            YourOtherScore = 0

                            for cards in range(len(CartesDesJoueurs[f'cartespv{joueur}'])):

                                if CartesDesJoueurs[f'cartespv{joueur}'][cards][:2] == "Ac":
                                    YourOtherScore += 11
                                if CartesDesJoueurs[f'cartespv{joueur}'][cards][:2] == "2 ":
                                    YourOtherScore += 2
                                if CartesDesJoueurs[f'cartespv{joueur}'][cards][:2] == "3 ":
                                    YourOtherScore += 3
                                if CartesDesJoueurs[f'cartespv{joueur}'][cards][:2] == "4 ":
                                    YourOtherScore += 4
                                if CartesDesJoueurs[f'cartespv{joueur}'][cards][:2] == "5 ":
                                    YourOtherScore += 5
                                if CartesDesJoueurs[f'cartespv{joueur}'][cards][:2] == "6 ":
                                    YourOtherScore += 6
                                if CartesDesJoueurs[f'cartespv{joueur}'][cards][:2] == "7 ":
                                    YourOtherScore += 7
                                if CartesDesJoueurs[f'cartespv{joueur}'][cards][:2] == "8 ":
                                    YourOtherScore += 8
                                if CartesDesJoueurs[f'cartespv{joueur}'][cards][:2] == "9 ":
                                    YourOtherScore += 9
                                if CartesDesJoueurs[f'cartespv{joueur}'][cards][:2] == "10":
                                    YourOtherScore += 10
                                if CartesDesJoueurs[f'cartespv{joueur}'][cards][:2] == "Va":
                                    YourOtherScore += 10
                                if CartesDesJoueurs[f'cartespv{joueur}'][cards][:2] == "Qu":
                                    YourOtherScore += 10
                                if CartesDesJoueurs[f'cartespv{joueur}'][cards][:2] == "Ki":
                                    YourOtherScore += 10
                                if CartesDesJoueurs[f'cartespv{joueur}'][cards][:2] == "ac":
                                    YourOtherScore += 1
                                
                            for cards in range(len(CartesDesJoueurs[f'cartespv{joueur}'])):
                                if (YourOtherScore > 21) and (CartesDesJoueurs[f'cartespv{joueur}'][cards][:2] == "Ac"):
                                    YourOtherScore -= 10
                                    CartesDesJoueurs[f'cartespv{joueur}'][cards] = CartesDesJoueurs[f'cartespv{joueur}'][cards].lower()

                            YourCards = ""

                            for cards in range(len(CartesDesJoueurs[f'cartespv{joueur}'])):
                                YourCards += f"``{CartesDesJoueurs[f'cartespv{joueur}'][cards]}``\n"

                            EmbedCarteTable.add_field(name = "Your cards :",
                                                    value = f"{YourCards}",
                                                    inline = False)
                            EmbedCarteTable.set_author(name = f"Your score : {YourOtherScore}")
                        
                        else :
            
                            OtherCards = ""
                            for cards in range(len(CartesDesJoueurs[f'cartespubliques{rang}'])):
                                OtherCards += f"``{CartesDesJoueurs[f'cartespubliques{rang}'][cards]}``\n"

                            otherplayer = ListeDesJoueurs[f"playerlist[{rang}]"]

                            EmbedCarteTable.add_field(name = f"{otherplayer} cards :",
                                                    value = f"{OtherCards}",
                                                    inline = False)
                        
                    NewMessageCartes = await self.client.get_channel(MessageIDJoueurs[f'{joueur}{joueur+1}']).fetch_message(MessageIDJoueurs[f'{joueur}{joueur}'])
                    await NewMessageCartes.edit(embed = EmbedCarteTable)

                if YourScore > 21 :
                    pointsjoueurs.append(YourScore)
                    break

                else:

                    MessageAddCard = await ListeDesJoueurs[f"playerlist[{tour}]"].send(embed = EmbedAddCardToList, components = [TirageCartesRow])

                    await asyncio.sleep(0.1)

                    try:
                        TirerCarte : ComponentContext = await manage_components.wait_for_component(self.client, messages=MessageAddCard, components=TirageCartesRow, check=CheckWantCard, timeout=60.0)

                    except asyncio.TimeoutError:
                        EmbedTropTard = discord.Embed(description = "You took too much time to choose. I pass your turn",
                                                    colour = discord.Colour.red())
                        await MessageAddCard.edit(embed = EmbedTropTard)
                        TirerCarte.custom_id = 'stop'
                    
                    if TirerCarte.custom_id == 'stop' :

                        await MessageAddCard.delete()

                        pointsjoueurs.append(YourScore)
        
        EmbedPvFinJeu = discord.Embed(title = "Game is finished !",
                                    description = f"All of you finished to play\n Go in the channel [or click here]({MessageStartGame.jump_url}) to see the results",
                                    colour = discord.Colour.green())
        
        for x in range(len(playerlist)):

            await ListeDesJoueurs[f"playerlist[{x}]"].send(embed = EmbedPvFinJeu)
        
        finjeu = list(zip(*sorted(zip(pointsjoueurs, playerlist), reverse=True)))

        playeringame = []
        scoresingame = []

        for a, b in zip(finjeu[0], finjeu[1]):
            if a <= 21 :
                scoresingame.append(a)
                playeringame.append(b)
        
        if len(playeringame) > 0 :
            samescore = 0
            
            for x in range(len(scoresingame)):

                if x == 0:
                    samescore += 1

                else :

                    if scoresingame[0] == scoresingame[x]:

                        samescore += 1
            
            PiecesParPersonne = GainPieces / samescore

            if type(PiecesParPersonne) == float :
                PiecesParPersonne = round(PiecesParPersonne)
            
            Gagnants = ""
            for x in range(samescore):
                Gagnants += f"<@{playeringame[x]}>\n"
            
            EmbedFinDeJeu = discord.Embed(title = "Game is finished !",
                                        colour = discord.Colour.gold())
            
            if samescore > 1 :

                EmbedFinDeJeu.add_field(name = "**__Winners :__**",
                                        value = f"{Gagnants}You will be credited of **{PiecesParPersonne} MG Coins** in your wallet.",
                                        inline = False)
            else:
                EmbedFinDeJeu.add_field(name = "**__Winner :__**",
                                        value = f"{Gagnants}You will be credited of **{PiecesParPersonne} MG Coins** in your wallet.",
                                        inline = False)

            for x in range(len(playeringame)):
                cursor.execute(f"SELECT coins FROM mgcoins WHERE user_id = {playeringame[x]}")
                addmgcoins = cursor.fetchone()
                ajoutermgcoins = int(addmgcoins[0])+PiecesParPersonne
                sql = ("UPDATE mgcoins SET coins = ? WHERE user_id = ?")
                val = (ajoutermgcoins, playeringame[x])
                cursor.execute(sql, val)
                db.commit()

        
        else :
            EmbedFinDeJeu = discord.Embed(title = "Game is finished !",
                                        description = "No one had a score under 21 points\nAll of you lost your money, and none of you won anything.",
                                        colour = discord.Colour.purple())
            
        
        JoueursEtScores = ""
        for x in range(len(playerlist)):
            JoueursEtScores += f"<@{playerlist[x]}> : **{pointsjoueurs[x]}**\n"
        
        EmbedFinDeJeu.add_field(name = "__Score of each players :__",
                                value = f"{JoueursEtScores}",
                                inline = False)
        
        await MessageStartGame.edit(embed = EmbedFinDeJeu)



def setup(client):
    client.add_cog(BlackJackCommand(client))
    print("Black Jack command cog ready !")