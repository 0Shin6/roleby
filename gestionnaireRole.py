import discord
from discord.ext import commands
import os
from dictionnaireEmojies import *

class GestionnaireRole(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.id_message_role = self.chargement_id_messages()
        self.guild_id = self.chargement_id_guild()
        self.id_verification = self.chargement_id_verification()

    # 1 - chargements des différents id
    def chargement_id_messages(self):
        if os.path.exists("identifiantMessage.txt"):
            with open("identifiantMessage.txt", "r") as f:
                contenu = f.read().strip()
                if contenu.isdigit():
                    return int(contenu)
        return None

    def chargement_id_guild(self):
        if os.path.exists("guild_id.txt"):
            with open("guild_id.txt", "r") as f:
                contenu = f.read().strip()
                if contenu.isdigit():
                    return int(contenu)
        return None

    def chargement_id_verification(self):
        if os.path.exists("identifiantVerification.txt"):
            with open("identifiantVerification.txt", "r") as f:
                contenu = f.read().strip()
                if contenu.isdigit():
                    return int(contenu)
        return None

    # 2 - sauvegarde des différents id
    def sauvegarde_info(self, idMessage, idServeur):
        with open("identifiantMessage.txt", "w") as f:
            f.write(str(idMessage))
        with open("guild_id.txt", "w") as f:
            f.write(str(idServeur))
        self.id_message_role = idMessage
        self.guild_id = idServeur

    def sauvegarde_verification(self, idMessage):
        with open("identifiantVerification.txt", "w") as f:
            f.write(str(idMessage))
        self.id_verification = idMessage

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
        if payload.message_id != self.id_message_role:
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
        if payload.message_id != self.id_verification or str(payload.emoji.name) != "✅":
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

        guild = self.bot.guilds[0]

        salon_roles = discord.utils.get(guild.text_channels, id=1358417427716640878)
        salon_verification = discord.utils.get(guild.text_channels, id=1364602013509357568)

        # 6a - récupération du message rôle
        if self.guild_id != guild.id or not self.id_message_role:
            await self.creationMessageRole(salon_roles, guild)
        else:
            try:
                await salon_roles.fetch_message(self.id_message_role)
                print("Message de rôles récupéré.")
            except discord.NotFound:
                await self.creationMessageRole(salon_roles, guild)

        if not self.id_verification:
            await self.creationMessageVerification(salon_verification)

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

            self.sauvegarde_info(message.id, guild.id)
            print("Message de rôle envoyé.")
        except Exception as e:
            print("Erreur création message rôle :", e)

    # 7 - Création message vérification
    async def creationMessageVerification(self, salon):
        try:
            message = await salon.send(
                "Bienvenue ! Réagis avec ✅ pour être vérifié et accéder au serveur."
            )
            await message.add_reaction("✅")
            self.sauvegarde_verification(message.id)
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
