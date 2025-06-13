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
    def set_config(self, guild_id, key, value, append=False):
        guild = str(guild_id)
        if guild not in self.configs:
            self.configs[guild] = {}

        if append and key in self.configs[guild]:
            if isinstance(self.configs[guild][key], list):
                self.configs[guild][key].append(value)
            else:
                self.configs[guild][key] = [self.configs[guild][key], value]
        else:
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
        idMessageRoles = config.get("idMessageRole", [])
        if isinstance(idMessageRoles, int):
            idMessageRoles = [idMessageRoles]

        idMessageRoles = config.get("idMessageRole", [])
        if isinstance(idMessageRoles, int):
            idMessageRoles = [idMessageRoles]

        if payload.message_id not in idMessageRoles:
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

            verifie = discord.utils.get(serveur.roles, name="Robynetos")
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

            idMessages = config.get("idMessageRole", [])
            if isinstance(idMessages, int):
                idMessages = [idMessages]

            
            for msg_id in idMessages:
                try:
                    await salonRole.fetch_message(msg_id)
                    print(f"Message de rôles existant récupéré (ID: {msg_id}).")
                except Exception as e:
                    print(f"Message de rôles non trouvé (ID: {msg_id})", e)
                       

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

    #7 - Création message vérification
    async def creationMessageVerification(self, salon, guild_id):
        if salon is None:
            print("Salon de vérification est inexistant.")
            return None
        try:
            messageVerif = discord.Embed(
                title="**__Réglement du serveur :__**",
                description=(
                    "**Lisez attentivement ces règles. En réagissant, vous attestez les accepter et vous engagez à les respecter pour accéder au serveur.**"
                ),
                color=discord.Color.green()
            )

            messageVerif.set_footer(text="Bot réalisé par @.Shin60 :-)")

            # Ajout des sections en tant que champs
            messageVerif.add_field(
                name="**__I. Respect et Courtoisie__**",
                value=(
                    "**Soyez respectueux envers tous les membres.**\n"
                    "・Aucun harcèlement, discrimination, propos haineux ou attaques personnelles ne sera toléré.\n"
                    "・Les débats doivent rester constructifs et polis.\n"
                ),
                inline=False
            )
            messageVerif.add_field(
                name="**__II. Interdiction du Spam__**",
                value=(
                    "・Pas de messages répétitifs, flood ou envoi massif d'emojis.\n"
                    "・Les publicités non autorisées (liens externes, serveurs Discord, etc.) sont interdites.\n"
                ),
                inline=False
            )
            messageVerif.add_field(
                name="**__III. Contenus Appropriés__**",
                value=(
                    "・Tout contenu NSFW, violent, illégal ou contraire aux règles de Discord est interdit.\n"
                    "・Respectez les droits d'auteur : pas de partage de contenus piratés.\n"
                ),
                inline=False
            )
            messageVerif.add_field(
                name="**__IV. Bon Usage des Canaux__**",
                value=(
                    "・Utilisez les salons prévus à cet effet (ex : discussions jeux dans #jeux-vidéo, questions techniques dans #aide).\n"
                    "・Vérifiez les descriptions des canaux avant de poster.\n"
                ),
                inline=False
            )
            messageVerif.add_field(
                name="**__V. Langue Principale__**",
                value=(
                    "・Le français est la langue de communication par défaut.\n"
                    "・Si un salon est dédié à une autre langue, respectez cette exception.\n"
                ),
                inline=False
            )
            messageVerif.add_field(
                name="**__VI. Sujets Sensibles__**",
                value=(
                    "・Les discussions politiques ou religieuses trop inflammatoires sont à éviter pour préserver la sérénité du serveur.\n"
                ),
                inline=False
            )
            messageVerif.add_field(
                name="**__VII. Protection de la Vie Privée__**",
                value=(
                    "・Ne partagez pas vos informations personnelles (nom complet, adresse, etc.).\n"
                    "・Ne divulguez pas celles des autres membres sans leur accord explicite.\n"
                ),
                inline=False
            )
            messageVerif.add_field(
                name="**__VIII. Âge Minimum__**",
                value="・Conformément aux conditions de Discord, vous devez avoir au moins 13 ans pour participer.\n",
                inline=False
            )
            messageVerif.add_field(
                name="**__IX. Modération et Sanction__**",
                value=(
                    "・Les modérateurs interviennent à leur discrétion et leurs décisions sont sans appel.\n"
                    "・En cas de problème, contactez un modérateur en message privé (pas d'appel public à la modération).\n"
                    "・Toute tentative de contourner un avertissement, mute ou bannissement (comme un retour avec un autre compte) entraînera une exclusion définitive.\n"
                ),
                inline=False
            )

            # Ajout du message final d'acceptation
            messageVerif.add_field(
                name="__**Acceptation**__",
                value="En réagissant avec ✅, vous acceptez ces règles sans réserve.",
                inline=False
            )


            message = await salon.send(embed=messageVerif)
            await message.add_reaction("✅")

            # Sauvegarde de l'ID du message
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


#adapter les rôles pour les serveurs, améliorer la présentation des messages, Ajouter la fonctionnalité de niveau