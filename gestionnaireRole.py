import discord
from discord.ext import commands
import os
from dictionnaireEmojies import *

class GestionnaireRole(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.id_message_role = self.charger_id_message()
        self.guild_id = self.charger_guild_id()

    # 1 - Chargement de l'ID du message
    def charger_id_message(self):
        if os.path.exists("identifiantMessage.txt"):
            with open("identifiantMessage.txt", "r") as f:
                contenu = f.read().strip()
                if contenu.isdigit():
                    return int(contenu)
        return None

    # 1b - Chargement de l'ID du serveur
    def charger_guild_id(self):
        if os.path.exists("guild_id.txt"):
            with open("guild_id.txt", "r") as f:
                contenu = f.read().strip()
                if contenu.isdigit():
                    return int(contenu)
        return None

    # 2 - Sauvegarde de l'ID du message et du serveur
    def sauvegarder_info(self, idMessage, idServeur):
        with open("identifiantMessage.txt", "w") as f:
            f.write(str(idMessage))
        with open("guild_id.txt", "w") as f:
            f.write(str(idServeur))
        self.id_message_role = idMessage
        self.guild_id = idServeur

    # 3 - Ajout du rôle "Non vérifié" aux nouveaux membres
    @commands.Cog.listener()
    async def on_member_join(self, member):
        try:
            role = discord.utils.get(member.guild.roles, name="Non vérifié")
            if role:
                await member.add_roles(role)
                print("Rôle 'Non vérifié' ajouté à", member.display_name)
        except Exception as e:
            print("Erreur ajout rôle 'Non vérifié' :", e)

    # 4 - Gestion des réactions
    async def gestionRoleReaction(self, payload, ajouter=True):
        if payload.message_id != self.id_message_role:
            return

        try:
            serveur = self.bot.get_guild(payload.guild_id)
            if not serveur:
                return

            emoji = payload.emoji.name
            nomRole = dictionnaireEmojies().get(emoji)
            if not nomRole:
                return

            role = discord.utils.get(serveur.roles, name=nomRole)
            if not role:
                print("Rôle", nomRole, "introuvable")
                return

            membre = serveur.get_member(payload.user_id)
            if membre:
                if ajouter:
                    await membre.add_roles(role)
                    print("Rôle", role.name, "ajouté à", membre.display_name)
                else:
                    await membre.remove_roles(role)
                    print("Rôle", role.name, "retiré à", membre.display_name)

        except Exception as e:
            print("Erreur gestion des rôles :", e)

    # 5 - Réactions : ajout / retrait
    @commands.Cog.listener()
    async def on_raw_reaction_add(self, payload):
        await self.gestionRoleReaction(payload, ajouter=True)

    @commands.Cog.listener()
    async def on_raw_reaction_remove(self, payload):
        await self.gestionRoleReaction(payload, ajouter=False)

    # 6 - Connexion du bot : envoie ou récupère le message
    @commands.Cog.listener()
    async def on_ready(self):
        print("GestionnaireRole prêt. Connecté en tant que :",self.bot.user)

        if not self.bot.guilds:
            print("Le bot n'est dans aucun serveur.")
            return None

        guild = self.bot.guilds[0]

        salon = discord.utils.get(guild.text_channels, id=1358417427716640878)
        if not salon:
            print("Salon introuvable")
            return None

        # Cas : serveur a changé (donc message invalide)
        if self.guild_id != guild.id:
            print("Nouveau serveur détecté : création d'un nouveau message de rôle")
            await self.creationMessageRole(salon, guild)
            return

        # Cas : essayer de récupérer le message si même serveur
        if self.id_message_role:
            try:
                await salon.fetch_message(self.id_message_role)
                print("Message de rôle existant trouvé")
                return
            except discord.NotFound:
                print("Ancien message introuvable")
            except Exception as e:
                print("Erreur récupération message :", e)

        # Sinon, créer un nouveau message
        await self.creationMessageRole(salon, guild)

    # 7 - Création du message de rôle
    async def creationMessageRole(self, salon, guild):
        try:
            message = await salon.send(
                "**__Réagis pour obtenir un rôle :__**\n\n"
                "💪 = Muscu\n"
                "📖 = Lecture\n"
                "👔 = Fashion"
            )
            for emoji in dictionnaireEmojies().keys():
                await message.add_reaction(emoji)

            self.sauvegarder_info(message.id, guild.id)
            print("Nouveau message créé et sauvegardé")
        except Exception as e:
            print("Erreur lors de l'envoi du message de rôle :", e)

    # 8 - Ajout du rôle booster si l'utilisateur booste le serveur
    @commands.Cog.listener()
    async def on_member_update(self, before, after):
        try:
            # Si le membre a commencé à booster
            if not before.premium_since and after.premium_since:
                booster_role = discord.utils.get(after.guild.roles, name="Booster")
                if booster_role:
                    await after.add_roles(booster_role)
                    print(f"{after.display_name} a boosté le serveur. Rôle attribué.")
            
            # Si le membre a arrêté de booster
            elif before.premium_since and not after.premium_since:
                booster_role = discord.utils.get(after.guild.roles, name="Server Booster")
                if booster_role and booster_role in after.roles:
                    await after.remove_roles(booster_role)
                    print(f"{after.display_name} a arrêté de booster. Rôle retiré.")
        
        except Exception as e:
            print("Erreur lors de l'ajout ou retrait du rôle booster :", e)
