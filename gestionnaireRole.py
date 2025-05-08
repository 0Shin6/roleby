import discord
from discord.ext import commands
import os
from dictionnaireEmojies import *
import json

idJson = "identifiants.json"

#1a - Chargement du fichier JSON
def charger_config():
    if os.path.exists(idJson):
        with open(idJson, "r") as f:
            return json.load(f)
    return {}

#1b - Sauvegarde du fichier JSON
def sauvegarder_config(data):
    with open(idJson, "w") as f:
        json.dump(data, f, indent=4)

class GestionnaireRole(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.configs = charger_config()
    
    #2a - prend l'ID des différents serveur où le bot se trouve
    def get_config(self, guild_id):
        return self.configs.get(str(guild_id), {})

    #2b - mets à jour la configuration des serveurs
    def set_config(self, guild_id, key, value):
        guild = str(guild_id)
        if guild not in self.configs:
            self.configs[guild] = {}
        self.configs[guild][key] = value
        sauvegarder_config(self.configs)

    #3a - ajout du rôle "non vérifié" aux nouveaux membres
    @commands.Cog.listener()
    async def on_member_join(self, member):
        try:
            role = discord.utils.get(member.guild.roles, name="Non vérifié")
            if role:
                await member.add_roles(role)
                print("Rôle 'Non vérifié' donné à", member.display_name)
        except Exception as e:
            print("Erreur lors de l’arrivée d’un membre :", e)

    #3b - mise en place du gestionnaire de réaction
    async def gestionRoleReaction(self, payload, ajouter=True):
        config = self.get_config(payload.guild_id)
        if payload.message_id != config.get("idMessageRole"):
            return None
        try:
            serveur = self.bot.get_guild(payload.guild_id)
            emoji = payload.emoji.name
            nomRole = dictionnaireEmojies().get(emoji)
            if not nomRole or not serveur:
                return None

            role = discord.utils.get(serveur.roles, name=nomRole)
            membre = serveur.get_member(payload.user_id)
            if membre and role:
                if ajouter:
                    await membre.add_roles(role)
                    print("Rôle", role.name, "ajouté à", membre.display_name)
                else:
                    await membre.remove_roles(role)
                    print("Rôle", role.name, "retiré à", membre.display_name)
        except Exception as e:
            print("Erreur gestion des rôles :", e)

     #3c - ajout du rôle "Vérifié" lorsque l'utilisateur coche la réaction. Retrait du rôle "non vérifié" en simultanée
    async def gestionVerification(self, payload):
        config = self.get_config(payload.guild_id)
        if payload.message_id != config.get("idVerification") or str(payload.emoji.name) != "✅":
            return None
        try:
            serveur = self.bot.get_guild(payload.guild_id)
            membre = serveur.get_member(payload.user_id)

            verifie = discord.utils.get(serveur.roles, name="Vérifié")
            nonVerifie = discord.utils.get(serveur.roles, name="Non vérifié")

            if membre:
                if verifie:
                    await membre.add_roles(verifie)
                if nonVerifie:
                    await membre.remove_roles(nonVerifie)
                print(f"{membre.display_name} est maintenant vérifié.")
        except Exception as e:
            print("Erreur gestion vérification :", e)

    #4 - mise en place des écouteurs
    @commands.Cog.listener()
    async def on_raw_reaction_add(self, payload):
        await self.gestionRoleReaction(payload, ajouter=True)
        await self.gestionVerification(payload)

    @commands.Cog.listener()
    async def on_raw_reaction_remove(self, payload):
        await self.gestionRoleReaction(payload, ajouter=False)

    #5 - connexion du bot 
    @commands.Cog.listener()
    async def on_ready(self):
        print("GestionnaireRole prêt. Connecté en tant que :", self.bot.user)

        for guild in self.bot.guilds:
            config = self.get_config(guild.id)

            salonRole = discord.utils.get(guild.text_channels, id=config.get("idSalonRole"))
            salonVerif = discord.utils.get(guild.text_channels, id=config.get("idSalonVerification"))

            if not config.get("idMessageRole"):
                if salonRole:
                    await self.creationMessageRole(salonRole, guild.id)
                else:
                    print(f"Salon de rôles introuvable pour le serveur {guild.name}")

            else:
                try:
                    await salonRole.fetch_message(config.get("idMessageRole"))
                    print("Message de rôles existant récupéré.")
                except Exception as e:
                    print("Message de rôles non trouvé, recréation...", e)
                    await self.creationMessageRole(salonRole, guild.id)

            if not config.get("idVerification"):
                if salonVerif:
                    await self.creationMessageVerification(salonVerif, guild.id)
                else:
                    print(f"Salon de vérification introuvable pour le serveur {guild.name}")

            else:
                try:
                    await salonVerif.fetch_message(config.get("idVerification"))
                    print("Message de vérification existant récupéré.")
                except Exception as e:
                    print("Message de vérification non trouvé, recréation...", e)
                    await self.creationMessageVerification(salonVerif, guild.id)

    #6b - création des messages rôle
    async def creationMessageRole(self, salon, guild_id):
        if salon is None:
            print("Salon de rôle est None.")
            return
        try:
            message = await salon.send(
                "**__Réagis pour obtenir un rôle :__**\n\n"
                "🦧 : 14\n"
                "👦 : 15\n"
                "🗿 : 16\n"
                "💪 : 17\n"
                "👨‍🦰 : 18+\n"
            )
            for emoji in dictionnaireEmojies().keys():
                await message.add_reaction(emoji)

            self.set_config(guild_id, "idMessageRole", message.id)
            print("Message de rôle envoyé.")
        except Exception as e:
            print("Erreur création message rôle :", e)

    #7 - Création message vérification
    async def creationMessageVerification(self, salon, guild_id):
        if salon is None:
            print("Salon de vérification est None.")
            return
        try:
            message = await salon.send(
                "Bienvenue ! Réagis avec ✅ pour être vérifié et accéder au serveur."
            )
            await message.add_reaction("✅")
            self.set_config(guild_id, "idVerification", message.id)
            print("Message de vérification envoyé.")
        except Exception as e:
            print("Erreur création message vérification :", e)

    # 8 - Gestion du boost
    @commands.Cog.listener()
    async def on_member_update(self, before, after):
        try:
            if not before.premium_since and after.premium_since:
                booster_role = discord.utils.get(after.guild.roles, name="Booster")
                if booster_role:
                    await after.add_roles(booster_role)
                    print(f"{after.display_name} a boosté. Rôle donné.")

            elif before.premium_since and not after.premium_since:
                booster_role = discord.utils.get(after.guild.roles, name="Booster")
                if booster_role and booster_role in after.roles:
                    await after.remove_roles(booster_role)
                    print(f"{after.display_name} a arrêté de booster. Rôle retiré.")
        except Exception as e:
            print("Erreur gestion boost :", e)
