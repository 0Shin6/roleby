import discord
from discord.ext import commands
import os
from dictionnaireEmojies import *
import json

idJson = "serveur_config.json"

#1a - chargement du fichier json
def charger_config():
    if os.path.exists(idJson):
        with open(idJson, "r") as f:
            return json.load(f)
    return {}

#1b - sauvegarde du fichier json
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

    # 3a - ajout du rôle "non vérifié" aux nouveaux membres
    @commands.Cog.listener()
    async def on_member_join(self, member):
        try:
            role = discord.utils.get(member.guild.roles, name="Non vérifié")
            if role:
                await member.add_roles(role)
                print("Rôle 'Non vérifié' donné à", member.display_name)
        except Exception as e:
            print("Erreur lors de l’arrivée d’un membre :", e)

    # 3b - mise en place du gestionnaire de réaction
    async def gestionRoleReaction(self, payload, ajouter=True):
        config = self.get_config(payload.guild_id)
        if payload.message_id != config.get("message_role"):
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

    # 3c - ajout du rôle "Vérifié" lorsque l'utilisateur coche la réaction. Retrait du rôle "non vérifié" en simultanée
    async def gestionVerification(self, payload):
        config = self.get_config(payload.guild_id)
        if payload.message_id != config.get("message_verification") or str(payload.emoji.name) != "✅":
            return None
        try:
            serveur = self.bot.get_guild(payload.guild_id)
            membre = serveur.get_member(payload.user_id)

            role_verifie = discord.utils.get(serveur.roles, name="Vérifié")
            role_nonverif = discord.utils.get(serveur.roles, name="Non vérifié")

            if membre:
                if role_verifie:
                    await membre.add_roles(role_verifie)
                if role_nonverif:
                    await membre.remove_roles(role_nonverif)
                print(f"{membre.display_name} est maintenant vérifié.")
        except Exception as e:
            print("Erreur gestion vérification :", e)

    # 4 - mise en place des écouteurs
    @commands.Cog.listener()
    async def on_raw_reaction_add(self, payload):
        await self.gestionRoleReaction(payload, ajouter=True)
        await self.gestionVerification(payload)

    @commands.Cog.listener()
    async def on_raw_reaction_remove(self, payload):
        await self.gestionRoleReaction(payload, ajouter=False)

    # 5 - connexion du bot 
    @commands.Cog.listener()
    async def on_ready(self):
        print("GestionnaireRole prêt. Connecté en tant que :", self.bot.user)
        if not self.bot.guilds:
            print("Aucun serveur détecté.")
            return

        for guild in self.bot.guilds:
            salonRoles = discord.utils.get(guild.text_channels, id=1358417427716640878)
            salonVerification = discord.utils.get(guild.text_channels, id=1364602013509357568)

            config = self.get_config(guild.id)

            idMessageRole = config.get("idMessageRole")
            idVerification = config.get("idVerification")

            if not idMessageRole:
                await self.creationMessageRole(salonRoles, guild)
            else:
                try:
                    await salonRoles.fetch_message(idMessageRole)
                    print("Message de rôles récupéré.")
                except discord.NotFound:
                    await self.creationMessageRole(salonRoles, guild)

            if not idVerification:
                await self.creationMessageVerification(salonVerification, guild)

    # 6b - création des messages rôle
    async def creationMessageRole(self, salon, guild):
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

            self.set_config(guild.id, "message_role", message.id)
            print("Message de rôle envoyé.")
        except Exception as e:
            print("Erreur création message rôle :", e)

    # 7 - Création message vérification
    async def creationMessageVerification(self, salon, guild):
        try:
            message = await salon.send(
                "Bienvenue ! Réagis avec ✅ pour être vérifié et accéder au serveur."
            )
            await message.add_reaction("✅")
            self.set_config(guild.id, "message_verification", message.id)
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