import discord
from discord import Intents
from discord.ext import commands,tasks
from discord.ext.commands import Bot, CommandInvokeError, UserNotFound
from discord.utils import get

from discord_slash import cog_ext, SlashContext, ComponentContext
from discord_slash.utils.manage_commands import create_option

from datetime import timezone, tzinfo, timedelta
import time as timeModule
import math
import random
import asyncio
import os
import sqlite3

db = sqlite3.connect("smallgames.sqlite") # Ouverture de la base de données
cursor = db.cursor()

class ProfileCommand(commands.Cog):
    def __init__(self, client):
        self.client = client

    @cog_ext.cog_slash(name = "profile", description = "See your games stats !", options=[
        create_option(name = "profileuser", description = "User whose profile you want to see (facultative)", option_type=6, required=False)
    ])
    async def profile(self, ctx : SlashContext, profileuser=None):

        if profileuser is None: # Si la mention est vide
            profileuser = ctx.author # On récupère l'auteur du message

        ### MG Coins ###

        cursor.execute(f"SELECT coins FROM mgcoins WHERE user_id = {profileuser.id}")
        ProfileCoins = cursor.fetchone() # On récupère les infos de son argent si elles existent

        if ProfileCoins is None : # si le joueur n'a pas de "porte feuille"

            defaultnumbercoins = 100
                
            sql = ("INSERT INTO mgcoins(user_id, coins) VALUES(?,?)")
            val = (profileuser.id, defaultnumbercoins)
            cursor.execute(sql, val)
            db.commit()
        
        cursor.execute(f"SELECT coins FROM mgcoins WHERE user_id = {profileuser.id}")
        ProfileCoins = cursor.fetchone() # On récupère les infos de son argent si elles existent (mais elles existent maintenant)

        EmbedDatas = discord.Embed(description = f"You have **__{ProfileCoins[0]}__ MG Coins** in your wallet",
                                colour = discord.Colour.gold())
        EmbedDatas.set_author(name = f"{profileuser}", 
                            icon_url= profileuser.avatar_url)

        
        ### Connect 4 ###

        cursor.execute(f"SELECT VictoryCountConnect4, LoseCountConnect4 FROM connect4 WHERE user_id = {profileuser.id}")
        ProfileUserConnect4 = cursor.fetchall() # On récupère les infos du joueur Puissance 4 si elles existent

        if ProfileUserConnect4 == []:
            EmbedDatas.add_field(name = "About Connect 4 profile",
                                value = f"I am sorry but you don't have any datas on the **Connect 4** game.\nPlay a game to create a **Connect 4** profile",
                                inline = False)

        else:
            VictoireConnect4 = ProfileUserConnect4[0][0]
            DefaiteConnect4 = ProfileUserConnect4[0][1]

            try:
                ratio1Connect4 = round(int(VictoireConnect4)/int(DefaiteConnect4), 2)
            except Exception:
                if VictoireConnect4 != 0:
                    ratio1Connect4 = round(int(VictoireConnect4), 2)
                else:
                    ratio1Connect4 = 0

            try:
                ratio2Connect4 = round((int(VictoireConnect4) / (int(VictoireConnect4) + int(DefaiteConnect4)))*100, 1)
            except Exception:
                ratio2Connect4 = 0

            EmbedDatas.add_field(name = "Connect 4 Victories",
                                value = f"{VictoireConnect4}",
                                inline = True)
            EmbedDatas.add_field(name = "Connect 4 Defeats",
                                value = f"{DefaiteConnect4}",
                                inline = True)
            EmbedDatas.add_field(name="Ratio :",
                                value = f"{ratio1Connect4}\n{ratio2Connect4} %",
                                inline = True)

        
        ### TicTacToe ###
        
        cursor.execute(f"SELECT VictoryCountTTT, LoseCountTTT FROM tictactoe WHERE user_id = {profileuser.id}")
        ProfileUserTTT = cursor.fetchall() # On récupère les infos du joueur Morpion si elles existent

        if ProfileUserTTT == []:
            EmbedDatas.add_field(name = "About Tic Tac Toe profile",
                                value = f"I am sorry but you don't have any datas on the **Tic Tac Toe** game.\nPlay a game to create a **Tic Tac Toe** profile",
                                inline = False)

        else:
            VictoireTTT = ProfileUserTTT[0][0]
            DefaiteTTT = ProfileUserTTT[0][1]

            try:
                ratio1TTT = round(int(VictoireTTT)/int(DefaiteTTT), 2)
            except Exception:
                if VictoireTTT != 0:
                    ratio1TTT = round(int(VictoireTTT), 2)
                else:
                    ratio1TTT = 0

            try:
                ratio2TTT = round((int(VictoireTTT) / (int(VictoireTTT) + int(DefaiteTTT)))*100, 1)
            except Exception:
                ratio2TTT = 0

            EmbedDatas.add_field(name = "Tic Tac Toe Victories",
                                value = f"{VictoireTTT}",
                                inline = True)
            EmbedDatas.add_field(name = "Tic Tac Toe Defeats",
                                value = f"{DefaiteTTT}",
                                inline = True)
            EmbedDatas.add_field(name="Ratio :",
                                value = f"{ratio1TTT}\n{ratio2TTT} %",
                                inline = True)

        
        ### ShiFuMi ###

        cursor.execute(f"SELECT VictoryCountSFM, LoseCountSFM FROM shifumi WHERE user_id = {profileuser.id}")
        ProfileUserSFM = cursor.fetchall() # On récupère les infos du joueur ShiFuMi si elles existent

        if ProfileUserSFM == []:
            EmbedDatas.add_field(name = "About ShiFuMi profile",
                                value = f"I am sorry but you don't have any datas on the **Shi Fu Mi** game.\nPlay a game to create a **Shi Fu Mi** profile",
                                inline = False)

        else:
            VictoireSFM = ProfileUserSFM[0][0]
            DefaiteSFM = ProfileUserSFM[0][1]

            try:
                ratio1SFM = round(int(VictoireSFM)/int(DefaiteSFM), 2)
            except Exception:
                if VictoireSFM != 0 :
                    ratio1SFM = round(int(VictoireSFM), 2)
                else :
                    ratio1SFM = 0

            try:
                ratio2SFM = round((int(VictoireSFM) / (int(VictoireSFM) + int(DefaiteSFM)))*100, 1)
            except Exception:
                ratio2SFM = 0

            EmbedDatas.add_field(name = "Shi Fu Mi Victories",
                                value = f"{VictoireSFM}",
                                inline = True)
            EmbedDatas.add_field(name = "Shi Fu Mi Defeats",
                                value = f"{DefaiteSFM}",
                                inline = True)
            EmbedDatas.add_field(name="Ratio :",
                                value = f"{ratio1SFM}\n{ratio2SFM} %",
                                inline = True)

        
        ### BattleShip ###

        cursor.execute(f"SELECT VictoryCountBTS, LoseCountBTS FROM battleship WHERE user_id = {profileuser.id}")
        ProfileUserHT = cursor.fetchall() # On récupère les infos du joueur BattleShip si elles existent

        if ProfileUserHT == []:
            EmbedDatas.add_field(name = "About BattleShip profile",
                                value = f"I am sorry but you don't have any datas on the **BattleShip** \"game\".\nPlay a game to create a **BattleShip** profile",
                                inline = False)

        else:
            VictoireBTS = ProfileUserHT[0][0]
            DefaiteBTS = ProfileUserHT[0][1]

            try:
                ratio1BTS = round(int(VictoireBTS)/int(DefaiteBTS), 2)
            except Exception:
                if VictoireBTS != 0 :
                    ratio1BTS = round(int(VictoireBTS), 2)
                else :
                    ratio1BTS = 0

            try:
                ratio2BTS = round((int(VictoireBTS) / (int(VictoireBTS) + int(DefaiteBTS)))*100, 1)
            except Exception:
                ratio2BTS = 0

            EmbedDatas.add_field(name = "BattleShip Victories",
                                value = f"{VictoireBTS}",
                                inline = True)
            EmbedDatas.add_field(name = "BattleShip Defeats",
                                value = f"{DefaiteBTS}",
                                inline = True)
            EmbedDatas.add_field(name="Ratio :",
                                value = f"{ratio1BTS}\n{ratio2BTS} %",
                                inline = True)
        
        ### Heads Or Tails ###

        cursor.execute(f"SELECT VictoryCountHT, LoseCountHT FROM headsortails WHERE user_id = {profileuser.id}")
        ProfileUserHT = cursor.fetchall() # On récupère les infos du joueur Heads Or Tails si elles existent

        if ProfileUserHT == []:
            EmbedDatas.add_field(name = "About Heads Or Tails profile",
                                value = f"I am sorry but you don't have any datas on the **Heads Or Tails** \"game\".\nPlay a game to create a **Heads Or Tails** profile",
                                inline = False)

        else:
            VictoireHT = ProfileUserHT[0][0]
            DefaiteHT = ProfileUserHT[0][1]

            try:
                ratio1HT = round(int(VictoireHT)/int(DefaiteHT), 2)
            except Exception:
                if VictoireHT != 0:
                    ratio1HT = round(int(VictoireHT), 2)
                else:
                    ratio1HT = 0

            try:
                ratio2HT = round((int(VictoireHT) / (int(VictoireHT) + int(DefaiteHT)))*100, 1)
            except Exception:
                ratio2HT = 0

            EmbedDatas.add_field(name = "Heads Or Tails Victories",
                                value = f"{VictoireHT}",
                                inline = True)
            EmbedDatas.add_field(name = "Heads Or Tails Defeats",
                                value = f"{DefaiteHT}",
                                inline = True)
            EmbedDatas.add_field(name="Ratio :",
                                value = f"{ratio1HT}\n{ratio2HT} %",
                                inline = True)
        

        # Envoie des données complètes
        await ctx.send(embed = EmbedDatas, hidden=True)




def setup(client):
    client.add_cog(ProfileCommand(client))
    print("Profile command cog ready !")