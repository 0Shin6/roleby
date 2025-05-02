import discord
from discord.ext import commands
import asyncio

class GestionnaireCommande(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name="sondage")
    #commande !sondage
    async def sondage(self, ctx):
        def check(msg):
            return msg.author == ctx.author and msg.channel == ctx.channel
        
        try:
            #écriture du titre du sondage
            await ctx.send("Quel est le titre du sondage ?")
            sujetMessage =await self.bot.wait_for('message', check=check, timeout=80)
            sujet = sujetMessage.content

            #écriture des options du sondage
            await ctx.send("Entrez les options du sondage (séparées par des virgules `,`).")
            optionMessage = await self.bot.wait_for('message', check=check, timeout=80)
            options = [opt.strip() for opt in optionMessage.content.split(',') if opt.strip()]

            if len(options) < 2:
                await ctx.send("il doit y avoir au minimum 2 options et au maximum 10.")
                return None

            #écriture des émojies associés aux options
            await ctx.send("Donnez les emojies à utiliser pour les sondages (séparés par des espaces).")
            emojiMessage = await self.bot.wait_for('message', check=check, timeout=60)
            emojis = emojiMessage.content.split()

            if len(emojis) != len(options):
                await ctx.send("Le nombre d'emojis ne correspond pas au nombre d'options.")
                return None
        #écriture de la durée du sondage (en seconde)
        await ctx.send("Quelle est la durée du sondage ? *en seconde*")
        dureeMessage = await self.bot.wait_for('message', check=check, timeout=45)
        duree = int(dureeMessage)


#Commandes : !sondage