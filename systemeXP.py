import discord
from discord.ext import commands, tasks
import asyncio
from collections import defaultdict
import aiosqlite

class SystemeXP(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.doneeXP = defaultdict(lambda: {'xp': 0, 'niveau': 0})
        self.etatVocale = {}
        self.idSalonNiveau = None
        self.bot.loop.create_task(self.load_settings())
        self.gestionVocal.start()

    async def load_settings(self):
        default_channel_id = 1367621879090778286
        async with aiosqlite.connect("bot.db") as db:
            await db.execute("""
                CREATE TABLE IF NOT EXISTS bot_settings (
                    key TEXT PRIMARY KEY,
                    value TEXT
                )
            """)
            await db.execute(
                "INSERT OR IGNORE INTO bot_settings (key, value) VALUES (?, ?)",
                ("xp_level_channel_id", str(default_channel_id))
            )
            await db.commit()

            cursor = await db.execute(
                "SELECT value FROM bot_settings WHERE key = ?",
                ("xp_level_channel_id",)
            )
            row = await cursor.fetchone()

        if row and row[0]:
            self.idSalonNiveau = int(row[0])

    # 1 - Ajout de 2 XP à chaque message
    @commands.Cog.listener()
    async def on_message(self, message):
        if message.author.bot:
            return

        membre = message.author
        identifiant = str(membre.id)
        self.ajouterXP(identifiant, 2)

        await self.MAJniveau(membre)

    # 2a - Détection d'entrée/sortie en salon vocal
    @commands.Cog.listener()
    async def on_voice_state_update(self, membre, avant, apres):
        if apres.channel and not avant.channel:
            self.etatVocale[membre.id] = asyncio.get_event_loop().time()
        elif avant.channel and not apres.channel:
            self.etatVocale.pop(membre.id, None)

    # 2b - Attribution automatique de 1 XP par minute passée en vocal
    @tasks.loop(minutes=1)
    async def gestionVocal(self):
        for serveur in self.bot.guilds:
            for salon_vocal in serveur.voice_channels:
                for membre in salon_vocal.members:
                    if not membre.bot:
                        identifiant = str(membre.id)
                        self.ajouterXP(identifiant, 1)
                        await self.MAJniveau(membre)

    # 3 - Ajout d'XP à un utilisateur
    def ajouterXP(self, identifiant, quantite):
        self.doneeXP[identifiant]['xp'] += quantite

    # 4 - Calcul du niveau à partir de l’XP totale
    def calculerNiveau(self, totalXP):
        niveaux = 0
        XPrequis = 0

        for niveau in range(1, 101):
            if niveau < 5:
                palier = 50
            elif niveau < 10:
                palier = 75
            elif niveau < 20:
                palier = 50
            elif niveau < 30:
                palier = 90
            elif niveau < 40:
                palier = 100
            elif niveau < 50:
                palier = 120
            else:
                palier = 150

            XPrequis += palier
            if totalXP >= XPrequis:
                niveaux += 1
            else:
                break

        return niveaux

    # Vérifie si un membre a atteint un nouveau niveau
    async def MAJniveau(self, membre: discord.Member):
        identifiant = str(membre.id)
        xp_total = self.doneeXP[identifiant]['xp']
        nouveauNiveau = self.calculerNiveau(xp_total)

        if self.doneeXP[identifiant]['niveau'] != nouveauNiveau:
            self.doneeXP[identifiant]['niveau'] = nouveauNiveau
            await self.MAJrole(membre, nouveauNiveau)

    # 5 - Attribution du rôle + annonce dans le salon dédié
    async def MAJrole(self, membre: discord.Member, niveau: int):
        serveur = membre.guild

        # Liste des paliers avec le niveau minimum requis
        rolePalier = [
            (100, "Godlike Viewer"),
            (80, "Mythic Viewer"),
            (60, "Legend Viewer"),
            (40, "Ace Viewer"),
            (20, "Good Viewer"),
            (10, "Active Viewer"),
            (5, "Middle Viewer"),
            (1, "Viewer"),
        ]

        # Trouve le bon rôle à attribuer
        nouveauRole = None
        for niveauMin, nomRole in rolePalier:
            if niveau >= niveauMin:
                nouveauRole = discord.utils.get(serveur.roles, name=nomRole)

        # Si un rôle est trouvé, il est appliqué
        if nouveauRole:
            nomRole = [nom for _, nom in rolePalier]
            ancienRole = [r for r in membre.roles if r.name in nomRole and r != nouveauRole]

            await membre.remove_roles(*ancienRole)
            if nouveauRole not in membre.roles:
                await membre.add_roles(nouveauRole)

async def setup(bot):
    await bot.add_cog(SystemeXP(bot))
    print("Gestionnaire de commande prêt.")
 