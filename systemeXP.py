import discord
from discord.ext import commands, tasks
import asyncio
from collections import defaultdict

class SystemeXP(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.doneeXP = defaultdict(lambda: {'xp': 0, 'niveau': 0})
        self.etatVocale = {}
        self.idSalonNiveau = 1367621879090778286
        self.gestionVocal.start()

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
    def calculerNiveau(self, xp_total):
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
            if xp_total >= XPrequis:
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
            (100, "Unreal Viewer"),
            (80, "Legend Viewer"),
            (60, "Mythic Viewer"),
            (40, "Ace Viewer"),
            (20, "Epic Viewer"),
            (10, "Active Viewer"),
            (5, "Common Viewer"),
            (1, "Average Viewer"),
        ]

        # Trouve le bon rôle à attribuer
        nouveauRole = None
        for niveauMin, nomRole in rolePalier:
            if niveau >= niveauMin:
                nouveauRole = discord.utils.get(serveur.roles, name=nomRole)
