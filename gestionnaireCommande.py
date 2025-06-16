import random
import discord
from discord.ext import commands
import asyncio
from gestionnaireRole import sauvegarder_config 

class GestionnaireCommande(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    ##########################
    #--- Commande sondage ---#
    ##########################
    @commands.has_permissions(administrator=True)
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
            title = "**La commande !role**",
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
    @commands.has_permissions(administrator=True) #seul les membres ayant la permission administrateur peuvent executer cette commande
    async def creationMessageRole(self, ctx):
        def check(m):
            return m.author == ctx.author and isinstance(m.channel, discord.DMChannel)

        try:
            #Envoie de la procédure de création du message en DM de l'auteur
            await ctx.author.send("Donne le **titre** du message de rôle :")
            titre = await self.bot.wait_for("message", check=check, timeout=60)

            await ctx.author.send("Donne la **description** (ou tape 'skip' pour rien) :")
            descriptionMessage = await self.bot.wait_for("message", check=check, timeout=60)
            if descriptionMessage.content.lower() == "skip":
                description = None
            else :
                description = descriptionMessage.content

            await ctx.author.send("Donner les rôles avec leurs émojis, un par ligne :")

            lignes = await self.bot.wait_for("message", check=check, timeout=200)
            lignes = lignes.content.strip().split("\n")

            contenu = ""
            emojiRole = {}

            for ligne in lignes:
                if ":" in ligne:
                    emoji, nomRole = ligne.split(":", 1)
                    emoji = emoji.strip()
                    contenu += f"{emoji} : {nomRole}\n"
                    emojiRole[emoji] = nomRole

            #Création du message de rôle
            embed = discord.Embed(
                title=f"__**{titre.content}**__",
                description=description or "Réagis avec l'émoji correspondant pour obtenir un rôle.",
                color=discord.Color.orange()
            )
            embed.add_field(name="Rôles disponibles :", value=contenu, inline=False)
            embed.set_footer(text="Bot réalisé par @.Shin60 :-)")

            message = await ctx.channel.send(embed=embed)

            for emoji in emojiRole.keys():
                await message.add_reaction(emoji)

            gestionnaire = self.bot.get_cog("GestionnaireRole")
            if gestionnaire:
                
                #On récupère les id message déjà enregistré
                config = gestionnaire.get_config(ctx.guild.id)
                idEnregistrees = config.get("idMessageRole", [])
                if not isinstance(idEnregistrees, list):
                    idEnregistrees = [idEnregistrees]

                #On ajoute le nouveau message
                idEnregistrees.append(message.id)
                gestionnaire.set_config(ctx.guild.id, "idMessageRole", message.id, append=True)

            await ctx.author.send("Le message de rôle a bien été envoyé.")

        except Exception as e:
            await ctx.author.send(" Une erreur est survenue. Vérifie bien la saisie.")
            print("Erreur dans la commande !role :", e)

    ##############################
    #--- commande information ---#
    ##############################
    @commands.command(name="info")
    async def information(self, ctx) :
        message = discord.Embed(
            title = "**Informations sur le bot**",
            description = 
                "Salut, je suis le bot du serveur Robynet créer par un youtubeur qui développe une communauté autour du développement personnel.\n"
                "Mon but est globalement de gérer les rôles via notamment les rôles réactions.\n"
                "De plus, le bot pourra à l'avenir gérer les niveaux, la boutique et également pouvoir organiser des concours.\n"
                "Je suis entièrement développé par @.shin60. Si vous voulez plus d'informations relatives au bot ou alors le contacter pour en créer un n'hésitez pas !",

            color = discord.Color.blue())

        message.set_footer(text="Pour plus d'aide, faites !aide :)")
        await ctx.send(embed=message)

    ###########################
    #--- commande giveaway ---#
    ###########################
    @commands.command(name="giveaway")
    @commands.has_permissions(administrator=True)
    async def giveaway(self, ctx) :
        def check(msg):
            return msg.author == ctx.author and isinstance(msg.channel, discord.DMChannel)

        try:
            try:
                await ctx.author.send("Création du giveaway. Répondez aux questions ci-dessous.")
            except discord.Forbidden:
                await ctx.send("Je ne peux pas vous envoyer de message privé. Activez vos DMs et réessayez.")
                return

            # Prix
            await ctx.author.send("Quel est le **prix** du giveaway ?")
            messagePrix = await self.bot.wait_for('message', check=check, timeout=60)
            prix = messagePrix.content

            # Durée
            await ctx.author.send("Quelle est la **durée** du giveaway (en **secondes**) ?")
            messageDuree = await self.bot.wait_for('message', check=check, timeout=60)
            duree = int(messageDuree.content)

            # Nombre de gagnants
            await ctx.author.send("Combien de **gagnants** ?")
            messageGagnant = await self.bot.wait_for('message', check=check, timeout=60)
            nbGagnant = int(messageGagnant.content)

            # Emoji
            await ctx.author.send("Quel emoji souhaitez-vous utiliser pour la participation ?")
            messageEmojie = await self.bot.wait_for('message', check=check, timeout=60)
            emoji = messageEmojie.content.strip()

            # Création de l’embed
            embed = discord.Embed(
                title="🎉 GIVEAWAY 🎉",
                description=f"récompense : **{prix}**\nRéagissez avec {emoji} pour participer !\nDurée : {duree} secondes",
                color=discord.Color.gold()
            )
            embed.set_footer(text=f"Lancé par {ctx.author.display_name}")

            # Envoi du message
            messageGiveaway = await ctx.send(embed=embed)
            await messageGiveaway.add_reaction(emoji)

            await ctx.author.send("Giveaway lancé avec succès.")

            # Attente de fin
            await asyncio.sleep(duree)

            # Analyse des participations
            message = await ctx.channel.fetch_message(messageGiveaway.id)
            reaction = discord.utils.get(message.reactions, emoji=emoji)

            if not reaction:
                await ctx.send("Aucun participant.")
                return None

            participants = await reaction.users().flatten()
            participants = [u for u in participants if not u.bot]

            if not participants:
                await ctx.send("Aucun participant valide.")
                return

            if nbGagnant > len(participants):
                nbGagnant = len(participants)

            gagnants = random.sample(participants, nbGagnant)
            mentions = ", ".join(user.mention for user in gagnants)

            await ctx.send(f"Félicitations {mentions} ! Vous remportez **{prix}** !")

        except asyncio.TimeoutError:
            await ctx.author.send("Temps écoulé. Giveaway annulé.")
        except Exception as e:
            await ctx.author.send(f"Une erreur est survenue : {e}")


async def setup(bot):
    await bot.add_cog(GestionnaireCommande(bot))
    print("Gestionnaire de commande prêt.")
