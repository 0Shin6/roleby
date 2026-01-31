import discord
from discord.ext import commands
import aiosqlite
import json
import os
from dictionnaireEmojies import *

# 0 - Constantes
DB_FILE = "bot.db" 
IDENTIFIANTS_FILE = "identifiants.json"
verifier = "Robynetos"
nonVerifier = "Non vérifié"
booster = "Booster"
emojieValider = "✅"

class GestionnaireRole(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    async def init_db(self):
        async with aiosqlite.connect(DB_FILE) as db:
            await db.execute("""
                CREATE TABLE IF NOT EXISTS guild_config (
                    guild_id TEXT PRIMARY KEY,
                    id_message_role TEXT,
                    id_verification TEXT,
                    id_salon_role TEXT,
                    id_salon_verification TEXT
                )
            """)
            await db.commit()

    async def migrate_identifiants_from_json(self):
        if not os.path.exists(IDENTIFIANTS_FILE):
            return

        with open(IDENTIFIANTS_FILE, "r", encoding="utf-8") as f:
            try:
                data = json.load(f)
            except json.JSONDecodeError:
                return

        if not isinstance(data, dict):
            return

        async with aiosqlite.connect(DB_FILE) as db:
            for guild_id, config in data.items():
                if not isinstance(config, dict):
                    continue

                raw_msg_roles = config.get("idMessageRole")
                if raw_msg_roles is None:
                    raw_msg_roles = config.get("idMessagesRole")

                if isinstance(raw_msg_roles, list):
                    msg_roles = json.dumps(raw_msg_roles, ensure_ascii=False)
                elif raw_msg_roles is None:
                    msg_roles = None
                else:
                    msg_roles = str(raw_msg_roles)

                await db.execute(
                    """
                    INSERT OR IGNORE INTO guild_config (
                        guild_id, id_message_role, id_verification, id_salon_role, id_salon_verification
                    ) VALUES (?, ?, ?, ?, ?)
                    """,
                    (
                        str(guild_id),
                        msg_roles,
                        str(config.get("idVerification")) if config.get("idVerification") else None,
                        str(config.get("idSalonRole")) if config.get("idSalonRole") else None,
                        str(config.get("idSalonVerification")) if config.get("idSalonVerification") else None,
                    )
                )

            await db.commit()

    # 2a - Récupération de la config depuis la DB (Nouvelle version)
    async def get_config_db(self, guild_id):
        async with aiosqlite.connect(DB_FILE) as db:
            cursor = await db.execute("SELECT * FROM guild_config WHERE guild_id = ?", (str(guild_id),))
            row = await cursor.fetchone()
            
            if row:
                try:
                    msg_roles = json.loads(row[1]) if row[1] else [] # id_messages_role
                except:
                    msg_roles = [int(row[1])] if row[1] and row[1].isdigit() else []

                return {
                    "idMessageRole": msg_roles,
                    "idVerification": int(row[2]) if row[2] else None,
                    "idSalonRole": int(row[3]) if row[3] else None,
                    "idSalonVerification": int(row[4]) if row[4] else None
                }
            return {}

    # 2b - Mise à jour de la config 
    async def set_verification_id(self, guild_id, message_id):
        async with aiosqlite.connect(DB_FILE) as db:
            await db.execute("""
                INSERT INTO guild_config (guild_id, id_verification) VALUES (?, ?)
                ON CONFLICT(guild_id) DO UPDATE SET id_verification = excluded.id_verification
            """, (str(guild_id), str(message_id)))
            await db.commit()

    # 3a - Ajout du rôle "Non vérifié"
    @commands.Cog.listener()
    async def on_member_join(self, member):
        try:
            role = discord.utils.get(member.guild.roles, name=nonVerifier)
            if role:
                await member.add_roles(role)
                print("Rôle 'Non vérifié' donné à", member.display_name)
        except Exception as e:
            print("Erreur lors de l’arrivée d’un membre :", e)

    # 3b - Gestion des réactions pour les rôles
    async def gestionRoleReaction(self, payload, ajouter=True):
        # SQL : On récupère la config
        config = await self.get_config_db(payload.guild_id)
        
        idMessageRoles = config.get("idMessageRole", [])
        # S'assurer que c'est une liste (au cas où)
        if isinstance(idMessageRoles, int): idMessageRoles = [idMessageRoles]

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

    # 3c - Vérification
    async def gestionVerification(self, payload):
        # SQL : On récupère la config
        config = await self.get_config_db(payload.guild_id)
        
        target_id = config.get("idVerification")
        
        if payload.message_id != target_id or str(payload.emoji.name) != emojieValider:
            return None

        try:
            serveur = self.bot.get_guild(payload.guild_id)
            membre = serveur.get_member(payload.user_id)

            verifie = discord.utils.get(serveur.roles, name=verifier)
            nonVerifie = discord.utils.get(serveur.roles, name=nonVerifier)

            if membre:
                if verifie:
                    await membre.add_roles(verifie)
                if nonVerifie:
                    await membre.remove_roles(nonVerifie)
                print(f"{membre.display_name} est maintenant vérifié.")
        except Exception as e:
            print("Erreur gestion vérification :", e)

    # 4a - Réaction ajoutée
    @commands.Cog.listener()
    async def on_raw_reaction_add(self, payload):
        await self.gestionRoleReaction(payload, ajouter=True)
        await self.gestionVerification(payload)

    # 4b - Réaction retirée
    @commands.Cog.listener()
    async def on_raw_reaction_remove(self, payload):
        await self.gestionRoleReaction(payload, ajouter=False)

    # 5 - Bot prêt
    @commands.Cog.listener()
    async def on_ready(self):
        print("GestionnaireRole prêt. Connecté en tant que :", self.bot.user)

        await self.init_db()
        await self.migrate_identifiants_from_json()

        for guild in self.bot.guilds:
            config = await self.get_config_db(guild.id)

            salon_role_id = config.get("idSalonRole")
            salon_verif_id = config.get("idSalonVerification")
            
            salonRole = discord.utils.get(guild.text_channels, id=salon_role_id) if salon_role_id else None
            salonVerif = discord.utils.get(guild.text_channels, id=salon_verif_id) if salon_verif_id else None

            idMessages = config.get("idMessageRole", [])
            if isinstance(idMessages, int): idMessages = [idMessages]

            if salonRole:
                for msg_id in idMessages:
                    try:
                        await salonRole.fetch_message(msg_id)
                        print(f"Message de rôles existant récupéré (ID: {msg_id}).")
                    except Exception as e:
                        print(f"Message de rôles non trouvé (ID: {msg_id})", e)

            id_verif = config.get("idVerification")
            if not id_verif:
                if salonVerif:
                    await self.creationMessageVerification(salonVerif, guild.id)
                else:
                    print(f"Salon de vérification introuvable pour le serveur {guild.name}")
            else:
                try:
                    if salonVerif:
                        await salonVerif.fetch_message(id_verif)
                        print("Message de vérification existant récupéré.")
                except Exception as e:
                    print("Message de vérification non trouvé, recréation...", e)
                    if salonVerif:
                        await self.creationMessageVerification(salonVerif, guild.id)

    # 6 - Création du message de vérification
    async def creationMessageVerification(self, salon, guild_id):
        if salon is None:
            print("Salon de vérification est inexistant.")
            return None

        try:
            embed = discord.Embed(
                title="**__Réglement du serveur :__**",
                description=("**Lisez attentivement ces règles. En réagissant, vous attestez les accepter et vous engagez à les respecter pour accéder au serveur.**"),
                color=discord.Color.green()
            )

            embed.set_footer(text="Bot réalisé par @.Shin60 :-)")

            sections = [
                """
                **__CHARTE DU SERVEUR DISCORD__**\n
                **Lisez attentivement ces règles. En réagissant, vous attestez les accepter et vous engagez à les respecter pour accéder au serveur.**\n\n

                **__I. Respect et Courtoisie__**\n
                **Soyez respectueux envers tous les membres.**\n\n

                ・Aucun harcèlement, discrimination, propos haineux ou attaques personnelles ne sera toléré.\n
                ・Les débats doivent rester constructifs et polis.\n\n


                **__II. Interdiction du Spam__**\n

                ・Pas de messages répétitifs, flood ou envoi massif d'emojis.\n
                ・Les publicités non autorisées (liens externes, serveurs Discord, etc.) sont interdites.\n\n


                **__III. Contenus Appropriés__**\n
                ・Tout contenu NSFW, violent, illégal ou contraire aux règles de Discord est interdit.\n
                ・Respectez les droits d'auteur : pas de partage de contenus piratés.\n\n


                **__IV. Bon Usage des Canaux__**\n
                ・Utilisez les salons prévus à cet effet (ex : discussions jeux dans #jeux-vidéo, questions techniques dans #aide).\n
                ・Vérifiez les descriptions des canaux avant de poster.\n\n


                **__V. Langue Principale\n__**
                ・Le français est la langue de communication par défaut.\n
                ・Si un salon est dédié à une autre langue, respectez cette exception.\n\n


                **__VI. Sujets Sensibles__**\n
                ・Les discussions politiques ou religieuses trop inflammatoires sont à éviter pour préserver la sérénité du serveur.\n\n


                **__VII. Protection de la Vie Privée\n__**
                ・Ne partagez pas vos informations personnelles (nom complet, adresse, etc.).\n
                ・Ne divulguez pas celles des autres membres sans leur accord explicite.\n\n


                **__VIII. Âge Minimum\n__**
                ・Conformément aux conditions de Discord, vous devez avoir au moins 13 ans pour participer.\n\n


                **__IX. Modération et Sanction__**\n
                ・Les modérateurs interviennent à leur discrétion et leurs décisions sont sans appel.\n
                ・En cas de problème, contactez un modérateur en message privé (pas d'appel public à la modération).\n
                ・Toute tentative de contourner un avertissement, mute ou bannissement (comme un retour avec un autre compte) entraînera une exclusion définitive.\n\n


                En réagissant, vous acceptez ces règles sans réserve.
                """
            ]

            for name, value in sections:
                embed.add_field(name=name, value=value, inline=False)

            message = await salon.send(embed=embed)
            await message.add_reaction(emojieValider)

            await self.set_verification_id(guild_id, message.id)
            print("Message de vérification envoyé.")
        except Exception as e:
            print("Erreur création message vérification :", e)

    # 7 - Gestion du boost
    @commands.Cog.listener()
    async def on_member_update(self, before, after):
        try:
            if not before.premium_since and after.premium_since:
                booster_role = discord.utils.get(after.guild.roles, name=booster)
                if booster_role:
                    await after.add_roles(booster_role)
                    print(f"{after.display_name} a boosté. Rôle donné.")

            elif before.premium_since and not after.premium_since:
                booster_role = discord.utils.get(after.guild.roles, name=booster)
                if booster_role and booster_role in after.roles:
                    await after.remove_roles(booster_role)
                    print(f"{after.display_name} a arrêté de booster. Rôle retiré.")
        except Exception as e:
            print("Erreur gestion boost :", e)
