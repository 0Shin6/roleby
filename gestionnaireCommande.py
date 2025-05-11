import discord
from discord.ext import commands
import asyncio

class GestionnaireCommande(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    ##########################
    #--- Commande sondage ---#
    ##########################
    @commands.command(name="sondage")
    async def sondage(self, ctx):
        def check(msg):
            return msg.author == ctx.author and isinstance(msg.channel, discord.DMChannel)
    
        try:
            #Procédure de création du sondage fait en DM
            try:
                await ctx.author.send("Bien reçu ! Creéation du sondage.")
            except discord.Forbidden:
                await ctx.send("Je ne peux pas vous envoyer de message privé. Activez vos DMs et réessayer.")
                return None
            #écriture du titre du sondage
            await ctx.author.send("Quel est le titre du sondage ?")
            sujetMessage =await self.bot.wait_for('message', check=check, timeout=80)
            sujet = sujetMessage.content

            #écriture des options du sondage
            await ctx.author.send("Entrez les options du sondage (séparées par des virgules `,`).")
            optionMessage = await self.bot.wait_for('message', check=check, timeout=80)
            options = [opt.strip() for opt in optionMessage.content.split(',') if opt.strip()]

            if len(options) < 2:
                await ctx.author.send("il doit y avoir au minimum 2 options et au maximum 10.")
                return None

            #écriture des émojies associés aux options
            await ctx.author.send("Donnez les emojies à utiliser pour les sondages (séparés par des espaces).")
            emojiMessage = await self.bot.wait_for('message', check=check, timeout=60)
            emojis = emojiMessage.content.split()

            if len(emojis) != len(options):
                await ctx.author.send("Le nombre d'emojis ne correspond pas au nombre d'options.")
                return None
            #écriture de la durée du sondage (en seconde)
            await ctx.author.send("Quelle est la durée du sondage ? *en seconde*")
            saisieDuree = await self.bot.wait_for('message', check=check, timeout=45)
            duree = int(saisieDuree.content)

            #préparation du message de sondage
                #mise en place de la description (= options de réponse)
            description = "\n".join(f"{emojis[i]} : {options[i]}" for i in range(len(options)))
                #structuration du message (= sujet, option et auteur)
            message = discord.Embed(title=sujet, description=description, color=discord.Color.blue())
            message.set_footer(text=f"sondage lancé par {ctx.author.display_name}")

            #envoie du message
            messageSondage = await ctx.send(embed=message)

            #ajout des réaction sous le sondage
            for emoji in emojis:
                await messageSondage.add_reaction(emoji)

            #ajout du timer 
            await asyncio.sleep(duree)

            message = await ctx.channel.fetch_message(messageSondage.id)
            resultat = {}

            #comptage des résultats
            for reaction in message.reactions:
                emoji = reaction.emoji
                if emoji in emojis:
                    resultat[emoji] = reaction.count - 1
            
            #déduction du gagnant
            if resultat:
                gagnant = max(resultat.items(), key=lambda item: item[0])

                if gagnant[1] != 0:
                    await ctx.send(f"Fin du sondage : \n Le choix {gagnant[0]} l’emporte avec {gagnant[1]} votes.")
                else:
                    await ctx.send("Sondage annulé : aucun vote réalisé")

        except Exception as e:
            await ctx.author.send("Une erreur est survenue", e)                
    
    #######################
    #--- Commande help ---#
    #######################
    @commands.command(name="aide")
    async def aide(self, ctx):
        #tête de message
        message = discord.Embed(
            title = " __**Mode d'emploi du bot**__",
            description = "Voici les commandes disponibles :",
            color = discord.Color.dark_purple())

        #corps du message
        # 1ere rubrique
        message.add_field(
            name="__*!sondage*__",
            value = 
                "Lance la création d'un sondage __en DM__.\n"
                "Le sondage est ensuite affiché dans le salon d'où la commande a été lancée.", inline=False)

        #2e rubrique
        message.add_field(
            name = "Fonctionnement du sondage",
            value = 
                "**1** - Le bot vous pose ces questions en DM : \n"
                "---a - le titre du sondage\n"
                "---b - les options de réponses\n"
                "---c - les émojies correspondant\n"
                "---d - la durée du sondage __en secondes__\n"
                "**2** - Une fois tout validé, le sondage s’affiche dans le salon.\n"
                "**3** - Le bot ajoute les réactions.\n"
                "**4** - À la fin du temps, le résultat est automatiquement annoncé.", inline=False)

        #fin du message
        message.set_footer(text="Bot réalisé par @.shin60 :-)")
        await ctx.send(embed=message)


    #######################
    #--- Commande role ---#
    #######################
    @commands.command(name="role")
    @commands.has_permissions(administrator=True)
    async def creationMessageRole(self, ctx):
        def check(m):
            return m.author == ctx.author and isinstance(m.channel, discord.DMChannel)

        try:
            await ctx.author.send("📝 Donne le **titre** du message de rôle :")
            titre = await self.bot.wait_for("message", check=check, timeout=60)

            await ctx.author.send("🧾 Donne la **description** (ou tape `skip` pour rien) :")
            descriptionMessage = await self.bot.wait_for("message", check=check, timeout=60)
            description = None if descriptionMessage.content.lower() == "skip" else descriptionMessage.content

            await ctx.author.send(
                "Donne les rôles avec leurs émojis, un par ligne sous ce format :\n"
                "`emoji : NomDuRôle`\n"
                "Exemple :\n"
                "🦧 : 14\n👦 : 15"
            )

            #...

        except Exception as e:
            await ctx.author.send("❌ Une erreur est survenue. Vérifie bien ta saisie.")
            print("Erreur dans la commande !role :", e)

async def setup(bot):
    await bot.add_cog(GestionnaireCommande(bot))
    print("Gestionnaire de commande prêt.")
