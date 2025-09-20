import discord
from discord.ext import commands
import time
from collections import defaultdict

class GestionnaireAntiSpam(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.message = defaultdict(list)  

        # paramètres
        self.intervalle = 10    
        self.messagesMax = 5    

    @commands.Cog.listener()
    async def on_message(self, message: discord.Message):
        if message.author.bot or not message.guild:
            return

        idmembre = message.author.id
        maintenant = time.time()

        # ajouter timestamp
        self.message[idmembre].append(maintenant)

        # garder seulement les messages récents
        self.message[idmembre] = [
            t for t in self.message[idmembre] if maintenant - t < self.intervalle
        ]

        # vérifier le spam
        if len(self.message[idmembre]) > self.messagesMax:
            membre = message.author

            # si le membre a rejoint il y a moins de 14 jours
            if (discord.utils.utcnow() - membre.joined_at).days < 14:
                try:
                    await message.delete()
                    await membre.ban(reason="Spam détecté")
                    await message.channel.send(f" {membre.mention} a été **banni** pour spam (moins de 2 semaines sur le serveur).")
                except discord.Forbidden:
                    await message.channel.send("Je n’ai pas la permission de bannir ce membre ou de supprimer son message.")
            else:
                try:
                    await message.delete()
                    await message.channel.send(f"{membre.mention}, ton message a été supprimé pour spam.")
                except discord.Forbidden:
                    await message.channel.send("Je n’ai pas la permission de supprimer des messages.")

            # reset pour éviter punition infinie
            self.message[idmembre] = []