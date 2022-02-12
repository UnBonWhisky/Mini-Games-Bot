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

class ShiFuMiCommand(commands.Cog):
    def __init__(self, client):
        self.client = client

    @cog_ext.cog_slash(name = "shifumi", description = "Play Shi-Fu-Mi with a friend", options=[
        create_option(name = "other_player", description = "User you want to play with", option_type=6, required=True)
    ])
    async def shifumi(self, ctx : SlashContext, other_player):

        ButtonCheck = [
            create_button(
                style=ButtonStyle.grey,
                emoji='✅',
                disabled=False
            )
        ]

        PlayButtons1 = [
            create_button(
                style=ButtonStyle.blue,
                emoji='✋',
                disabled=False,
                custom_id="feuille"
            ),
            create_button(
                style=ButtonStyle.blue,
                emoji='✊',
                disabled=False,
                custom_id="pierre"
            ),
            create_button(
                style=ButtonStyle.blue,
                emoji='🖖',
                disabled=False,
                custom_id="ciseaux"
            )
        ]

        PlayButtons2 = [
            create_button(
                style=ButtonStyle.blue,
                emoji='✋',
                disabled=False,
                custom_id="feuille"
            ),
            create_button(
                style=ButtonStyle.blue,
                emoji='✊',
                disabled=False,
                custom_id="pierre"
            ),
            create_button(
                style=ButtonStyle.blue,
                emoji='🖖',
                disabled=False,
                custom_id="ciseaux"
            )
        ]

        CheckRow = create_actionrow(*ButtonCheck)
        PlayRaw1 = create_actionrow(*PlayButtons1)
        PlayRaw2 = create_actionrow(*PlayButtons2)

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

            EmbedStartGame = discord.Embed(description = f"<@{other_player.id}>, <@{ChallengerUser.id}> want to play a **Shi-Fu-Mi** against you. You got 15 seconds to accept the invitation !", 
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

            cursor.execute(f"SELECT VictoryCountSFM, LoseCountSFM FROM shifumi WHERE user_id = {ChallengerUser.id}")
            DonneeChallengerExist = cursor.fetchone() # vérif si les données existent pour le joueur jaune

            if DonneeChallengerExist is None : # si les données existent pas pour le joueur jaune
                
                sql = ("INSERT INTO shifumi(user_id, VictoryCountSFM, LoseCountSFM) VALUES(?,?,?)")
                val = (ChallengerUser.id, zerovictoire, zerodefaite)
                cursor.execute(sql, val)
                db.commit()
                pass


            # Rouge

            cursor.execute(f"SELECT VictoryCountSFM, LoseCountSFM FROM shifumi WHERE user_id = {other_player.id}")
            DonneeChallengedExist = cursor.fetchone() # vérif si les données existent pour le joueur rouge

            if DonneeChallengedExist is None : # si les données existent pas pour le joueur rouge
                
                sql = ("INSERT INTO shifumi(user_id, VictoryCountSFM, LoseCountSFM) VALUES(?,?,?)")
                val = (other_player.id, zerovictoire, zerodefaite)
                cursor.execute(sql, val)
                db.commit()
                pass
            
            ### Suite du code ###

            EmbedJeu = discord.Embed(description = f"Alright !! Let's go !\nCheck your DM's\nYou have got 2mins to react your choose",
                                    colour = discord.Colour.blurple())

            EmbedChaqueJoueur = discord.Embed(description = "React to choose your move !",
                                    colour = discord.Colour.orange())

            await rep.edit(embed = EmbedJeu, components=[])

            ChallengerMessage = await ChallengerUser.send(embed = EmbedChaqueJoueur, components=[PlayRaw1])
            ChallengedMessage = await other_player.send(embed = EmbedChaqueJoueur, components=[PlayRaw2])

            await asyncio.sleep(0.1)

            ChallengeUsers = [f"{ChallengerUser.id}", f"{other_player.id}"]
            #ChallengeMessages = [f"{ChallengerMessage.id}", f"{ChallengedMessage.id}"]
            #ChallengeMessages = [ChallengerMessage, ChallengedMessage]
            #emojilist = ['✋','✊','🖖']
            ResultatPartie = []

            #def checkchallenge1(payload):
            #    return (str(payload.user_id) in ChallengeUsers) and (str(payload.emoji) in emojilist) and (str(payload.message_id) in ChallengeMessages)


            async def ChellengerTask():

                def checkchallenge(ctx: ComponentContext):
                    return ctx.author_id == ChallengerUser.id and (ctx.custom_id == "feuille" or ctx.custom_id == "pierre" or ctx.custom_id == "ciseaux")
                
                try:            
                    ChoixJoueur : ComponentContext = await manage_components.wait_for_component(self.client, messages=ChallengerMessage, components=PlayRaw1, timeout=120.0, check=checkchallenge)
                except asyncio.TimeoutError:
                    EmbedErrorTimeout = discord.Embed(description = "A user did not choose a reation", 
                                            colour = discord.Colour.dark_blue())
                    await rep.edit(embed = EmbedErrorTimeout, components=[])
                    await ChallengerMessage.edit(embed = EmbedErrorTimeout, components=[])
                    await ChallengedMessage.edit(embed = EmbedErrorTimeout, components=[])
                    return

                for x in range(len(PlayRaw1)+1):
                    PlayRaw1['components'][x]["disabled"] = True

                if ChoixJoueur.custom_id == "feuille":
                    Choix = "Paper"
                    PlayRaw1['components'][0]["style"] = ButtonStyle.green

                elif ChoixJoueur.custom_id == "pierre":
                    Choix = "Rock"
                    PlayRaw1['components'][1]["style"] = ButtonStyle.green

                elif ChoixJoueur.custom_id == "ciseaux" :
                    Choix = "Scissors"
                    PlayRaw1['components'][2]["style"] = ButtonStyle.green
                
                EmbedChoixJoueur = discord.Embed(description = f"You've chosen **{Choix}**\nWaiting your opponent",
                                                colour=discord.Colour.purple()
                                                )

                await ChoixJoueur.edit_origin(embed = EmbedChoixJoueur, components=[PlayRaw1])
                ResultatPartie.append([ChoixJoueur.component['emoji']['name'], ChoixJoueur.author_id])


            async def ChellengedTask():

                def checkchallenge(ctx: ComponentContext):
                    return ctx.author_id == other_player.id and (ctx.custom_id == "feuille" or ctx.custom_id == "pierre" or ctx.custom_id == "ciseaux")
                
                try:            
                    ChoixJoueur : ComponentContext = await manage_components.wait_for_component(self.client, messages=ChallengedMessage, components=PlayRaw2, timeout=120.0, check=checkchallenge)
                except asyncio.TimeoutError:
                    EmbedErrorTimeout = discord.Embed(description = "A user did not choose a reation", 
                                            colour = discord.Colour.dark_blue())
                    await rep.edit(embed = EmbedErrorTimeout, components=[])
                    await ChallengerMessage.edit(embed = EmbedErrorTimeout, components=[])
                    await ChallengedMessage.edit(embed = EmbedErrorTimeout, components=[])
                    return

                for x in range(len(PlayRaw1)+1):
                    PlayRaw2['components'][x]["disabled"] = True

                if ChoixJoueur.custom_id == "feuille":
                    Choix = "Paper"
                    PlayRaw2['components'][0]["style"] = ButtonStyle.green

                elif ChoixJoueur.custom_id == "pierre":
                    Choix = "Rock"
                    PlayRaw2['components'][1]["style"] = ButtonStyle.green

                elif ChoixJoueur.custom_id == "ciseaux" :
                    Choix = "Scissors"
                    PlayRaw2['components'][2]["style"] = ButtonStyle.green
                
                EmbedChoixJoueur = discord.Embed(description = f"You've chosen **{Choix}**\nWaiting your opponent",
                                                colour=discord.Colour.purple()
                                                )

                await ChoixJoueur.edit_origin(embed = EmbedChoixJoueur, components=[PlayRaw2])
                ResultatPartie.append([ChoixJoueur.component['emoji']['name'], ChoixJoueur.author_id])
            
            await asyncio.gather(ChellengerTask(), ChellengedTask())


            ResultatPartie[0] = [0 if i=='✊' else 1 if i=='✋' else 2 if i=='🖖' else i for i in ResultatPartie[0]]
            ResultatPartie[1] = [0 if i=='✊' else 1 if i=='✋' else 2 if i=='🖖' else i for i in ResultatPartie[1]]

            Joueur1 = ChallengerUser
            Joueur2 = other_player
            

            if ResultatPartie[0][0] == ResultatPartie[1][0]:

                ### Fin de game par une égalité ###

                if ResultatPartie[0][0] == 0:
                    PublicWinnerPicked = "``(Picked Rock)``"
                    PrivateWinnerPicked = "Rock"
                elif ResultatPartie[0][0] == 1:
                    PublicWinnerPicked = "``(Picked Paper)``"
                    PrivateWinnerPicked = "Paper"
                else:
                    PublicWinnerPicked = "``(Picked Scissors)``"
                    PrivateWinnerPicked = "Scissors"

                EmbedChannelEgalite = discord.Embed(description = f"IT'S A TIE !! {PublicWinnerPicked}\n\nGG WP to <@{ResultatPartie[0][1]}> and <@{ResultatPartie[1][1]}>",
                                                    colour = discord.Colour.green())
                await rep.edit(embed = EmbedChannelEgalite)
                
                EmbedTieDMGauche = discord.Embed(title = "Tie !",
                                                description = f"{Joueur2} has chosen {PrivateWinnerPicked}",
                                                colour = 0xFF0000)
                await ChallengerMessage.edit(embed = EmbedTieDMGauche)

                EmbedTieDMGauche = discord.Embed(title = "Tie !",
                                                description = f"{Joueur1} has chosen {PrivateWinnerPicked}",
                                                colour = 0xFF0000)
                await ChallengedMessage.edit(embed = EmbedTieDMGauche)
                return
            
            elif (ResultatPartie[0][0] > ResultatPartie[1][0] and ResultatPartie[1][0] + 1 == ResultatPartie[0][0]) or (ResultatPartie[0][0] < ResultatPartie[1][0] and ResultatPartie[0][0] + ResultatPartie[1][0]==2):

                ### Fin de game par une victoire du joueur lanceur de la game ###

                if ResultatPartie[0][0] == 0:
                    PublicWinnerPicked = "``(Picked Rock)``"
                    PublicLoserPicked = "``(Picked Scissors)``"
                    PrivateWinnerPicked = "Rock"
                    PrivateLoserPicked = "Scissors"
                elif ResultatPartie[0][0] == 1:
                    PublicWinnerPicked = "``(Picked Paper)``"
                    PublicLoserPicked = "``(Picked Rock)``"
                    PrivateWinnerPicked = "Paper"
                    PrivateLoserPicked = "Rock"
                else:
                    PublicWinnerPicked = "``(Picked Scissors)``"
                    PublicLoserPicked = "``(Picked Paper)``"
                    PrivateWinnerPicked = "Scissors"
                    PrivateLoserPicked = "Paper"

                EmbedChannelGaucheWinner = discord.Embed(description = f"<@{ResultatPartie[0][1]}> won the match ! {PublicWinnerPicked}\n<@{ResultatPartie[1][1]}> lost the match ! {PublicLoserPicked}\n\nGG WP to <@{ResultatPartie[0][1]}> and <@{ResultatPartie[1][1]}>",
                                                        colour = discord.Colour.green())
                await rep.edit(embed = EmbedChannelGaucheWinner)

                EmbedWinDM = discord.Embed(title = "You won !",
                                        description = f"{Joueur2} picked {PrivateLoserPicked}",
                                        colour = discord.Colour.green())
                await ChallengerMessage.edit(embed = EmbedWinDM)

                EmbedLoseDM = discord.Embed(title = "You lost !",
                                        description = f"{Joueur1} picked {PrivateWinnerPicked}",
                                        colour = discord.Colour.red())
                await ChallengedMessage.edit(embed = EmbedLoseDM)
                
                ### Incrémentation dans la base de donnée ###

                cursor.execute(f"SELECT VictoryCountSFM, LoseCountSFM FROM shifumi WHERE user_id = {ChallengerUser.id}")
                add1victorchallenger = cursor.fetchall()
                ajouter1victoirechallenger = int(add1victorchallenger[0][0])+1
                sql = ("UPDATE shifumi SET VictoryCountSFM = ? WHERE user_id = ?")
                val = (ajouter1victoirechallenger, ChallengerUser.id)
                cursor.execute(sql, val)
                db.commit()

                cursor.execute(f"SELECT VictoryCountSFM, LoseCountSFM FROM shifumi WHERE user_id = {other_player.id}")
                add1defeatchallenged = cursor.fetchall()
                ajouter1défaitechallenged = int(add1defeatchallenged[0][1])+1
                sql = ("UPDATE shifumi SET LoseCountSFM = ? WHERE user_id = ?")
                val = (ajouter1défaitechallenged, other_player.id)
                cursor.execute(sql, val)
                db.commit()

                return
            
            else:

                ### Fin de la game par victoire du joueur qui s'est fait invité ###

                if ResultatPartie[1][0] == 0:
                    PublicWinnerPicked = "``(Picked Rock)``"
                    PublicLoserPicked = "``(Picked Scissors)``"
                    PrivateWinnerPicked = "Rock"
                    PrivateLoserPicked = "Scissors"
                elif ResultatPartie[1][0] == 1:
                    PublicWinnerPicked = "``(Picked Paper)``"
                    PublicLoserPicked = "``(Picked Rock)``"
                    PrivateWinnerPicked = "Paper"
                    PrivateLoserPicked = "Rock"
                elif ResultatPartie[1][0] == 2:
                    PublicWinnerPicked = "``(Picked Scissors)``"
                    PublicLoserPicked = "``(Picked Paper)``"
                    PrivateWinnerPicked = "Scissors"
                    PrivateLoserPicked = "Paper"
                
                EmbedChannelDroitWinner = discord.Embed(description = f"<@{ResultatPartie[1][1]}> won the match ! {PublicWinnerPicked}\n<@{ResultatPartie[0][1]}> lost the match ! {PublicLoserPicked}\n\nGG WP to <@{ResultatPartie[1][1]}> and <@{ResultatPartie[0][1]}>",
                                                        colour = discord.Colour.green())
                await rep.edit(embed = EmbedChannelDroitWinner)
                
                EmbedWinDM = discord.Embed(title = "You won !",
                                        description = f"{Joueur1} picked {PrivateLoserPicked}",
                                        colour = discord.Colour.green())
                await ChallengedMessage.edit(embed = EmbedWinDM)
                
                EmbedLoseDM = discord.Embed(title = "You lost !",
                                        description = f"{Joueur2} picked {PrivateWinnerPicked}",
                                        colour = discord.Colour.red())
                await ChallengerMessage.edit(embed = EmbedLoseDM)

                ### Incrémentation dans la base de donnée ###

                cursor.execute(f"SELECT VictoryCountSFM, LoseCountSFM FROM shifumi WHERE user_id = {other_player.id}")
                add1victorchallenged = cursor.fetchall()
                ajouter1victoirechallenged = int(add1victorchallenged[0][0])+1
                sql = ("UPDATE shifumi SET VictoryCountSFM = ? WHERE user_id = ?")
                val = (ajouter1victoirechallenged, other_player.id)
                cursor.execute(sql, val)
                db.commit()

                cursor.execute(f"SELECT VictoryCountSFM, LoseCountSFM FROM shifumi WHERE user_id = {ChallengerUser.id}")
                add1defeatchallenger = cursor.fetchall()
                ajouter1défaitechallenger = int(add1defeatchallenger[0][1])+1
                sql = ("UPDATE shifumi SET LoseCountSFM = ? WHERE user_id = ?")
                val = (ajouter1défaitechallenger, ChallengerUser.id)
                cursor.execute(sql, val)
                db.commit()

                return
                




def setup(client):
    client.add_cog(ShiFuMiCommand(client))
    print("Shi-Fu-Mi command cog ready !")