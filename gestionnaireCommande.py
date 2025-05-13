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
    
    ########################
    #--- Commandes aide ---#
    ########################
    @commands.command(name="aide")
    async def aide(self, ctx):
        #tête de message
        message = discord.Embed(
            title = " __**Mode d'emploi du bot**__",
            description = "Voici les commandes disponibles :",
            color = discord.Color.red())

        #corps du message
        message.add_field(
            name="Pour quelle commande avez-vous besoin d'aide ?",
            value = 
                "!sondage --> !aideSonsage *(réserver administrateur)*\n"
                "!role --> !aideRole *(réserver administrateur)*\n"
                "!informations --> pour en savoir plus sur le bot !", inline=False)

        #fin du message
        message.set_footer(text="Bot réalisé par @.shin60 :-)")
        await ctx.send(embed=message)

    @commands.command(name="aideSondage")
    @commands.has_permissions(administrator=True)
    async def aideSondage(self, ctx):
        message = discord.Embed(
            title = "**La commande !sondage**",
            description = 
                "La commande !sondage permet de créer un sondage depuis vos DM !\n"
                "En DM il vous sera demandé le titre, puis les options, par la suite les émojies et la durée du sondage *en seconde*.\n"
                "Le bot envoie le sondage dans le salon où __!sondage__ a été écrit. Dès que le timer est écoulé, le bot compte les résultats et désigne l'option gagnante.",
            color = discord.Color.orange())
        
        message.set_footer(text="Pour plus d'information contacter @.shin60 :) ")
        await ctx.send(embed=message)
    
    @commands.command(name="aideRole")
    @commands.has_permissions(administrator=True)
    async def aideRole(self, ctx) :
        message = discord.Embed(
            title = "**La commande !role",
            description = 
                "La commande !role permet de créer un message de rôle réaction\n"
                " il faut donner l'association emoji - rôle sous ce format :\n"
                "`emoji : rôle\n"
                "Par exemple :\n"
                "🦧 : 14\n"
                "👦 : 15\n"
                "Le message de rôle réaction sera envoyé dans me salon où la commande a été effectué\n"
                "*Attention a bien écrire le nom du rôle. Dans le cas contraire le rôle réaction ne marchera pas !*",
            color = discord.Color.dark_purple())

        message.set_footer(text="Pour plus d'information contacter @.shin60 :) ")
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
            await ctx.author.send("Donne le **titre** du message de rôle :")
            titre = await self.bot.wait_for("message", check=check, timeout=60)

            await ctx.author.send("🧾 Donne la **description** (ou tape `skip` pour rien) :")
            descriptionMessage = await self.bot.wait_for("message", check=check, timeout=60)
            description = None if descriptionMessage.content.lower() == "skip" else descriptionMessage.content

            await ctx.author.send(
                "Donner les rôles avec leurs émojis, un par ligne"
            )

            #...

        except Exception as e:
            await ctx.author.send(" Une erreur est survenue. Vérifie bien ta saisie.")
            print("Erreur dans la commande !role :", e)

async def setup(bot):
    await bot.add_cog(GestionnaireCommande(bot))
    print("Gestionnaire de commande prêt.")


##############################
#--- commande information ---#
##############################



#commandes à faire: !role, !information, !message