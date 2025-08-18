from collections import defaultdict
import random
import discord
from discord.ext import commands
#from systemeXP import calculerNiveau


import asyncio

class GestionnaireCommande(commands.Cog):
    def __init__(self, bot):
        self.bot = bot



    ########################
    #--- Commande !role ---#
    ########################
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



    ############################
    #--- commande !giveaway ---#
    ############################
    @commands.command(name="giveaway")
    @commands.has_permissions(administrator=True)
    async def giveaway(self, ctx) :
        def filtre(msg):
            return msg.author == ctx.author and isinstance(msg.channel, discord.DMChannel)

        try:
            try:
                await ctx.author.send("Création du giveaway. Répondez aux questions ci-dessous.")
            except discord.Forbidden:
                await ctx.send("Je ne peux pas vous envoyer de message privé. Activez vos DMs et réessayez.")
                return

            # Prix
            await ctx.author.send("Quel est le **prix** du giveaway ?")
            messagePrix = await self.bot.wait_for('message', check=filtre, timeout=60)
            prix = messagePrix.content

            # Durée
            await ctx.author.send("Quelle est la **durée** du giveaway (en **secondes**) ?")
            messageDuree = await self.bot.wait_for('message', check=filtre, timeout=60)
            duree = int(messageDuree.content)

            # Nombre de gagnants
            await ctx.author.send("Combien de **gagnants** ?")
            messageGagnant = await self.bot.wait_for('message', check=filtre, timeout=60)
            nbGagnant = int(messageGagnant.content)

            # Emoji
            await ctx.author.send("Quel emoji souhaitez-vous utiliser pour la participation ?")
            messageEmojie = await self.bot.wait_for('message', check=filtre, timeout=60)
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

            participants = [user async for user in reaction.users()]
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

    

    #################################
    #--- Commandes !cg & !cgetat ---#
    #################################
    @commands.command("cg")
    @commands.has_permissions(administrator=True)
    async def cg(self, ctx):
        cog = self.bot.get_cog("GestionnaireCultureG")
        if not cog:
            await ctx.send("Le système de culture générale n'est pas chargé.")
            return None

        if not cog.questionJournaliere.is_running():
            cog.questionJournaliere.start()
            await ctx.send("Questions de culture générale **activées** (toutes les 24h).")
        else:
            cog.questionJournaliere.cancel()
            await ctx.send("Questions de culture générale **désactivées**.")

    @commands.command(name="cgetat")
    async def etatCultureG(self, ctx):
        cog_cg = self.bot.get_cog("GestionnaireCultureG")
        if cog_cg is None:
            await ctx.send("Le système de culture générale n'est pas chargé.")
            return None

        etat = "actif" if cog_cg.questionJournaliere.is_running() else "inactif"
        await ctx.send(f"Le système de culture générale est **{etat}**.")



    ###########################
    #--- Commande !ajoutcg ---#
    ###########################
    @commands.command(name="ajoutcg")
    @commands.has_permissions(administrator=True)
    async def ajoutcg(self, ctx):
            cg = self.bot.get_cog("GestionnaireCultureG")
            if not cg:
                await ctx.send("Le système de culture générale n'est pas chargé.")
                return None
            
            def filtre(message):
                return message.author == ctx.author and message.channel == ctx.channel

            await ctx.author.send("Entrez l'intitulé de la question :")
            messageQuestion = await self.bot.wait_for('message', check=filtre, timeout=60)
            question = messageQuestion.content

            propositions = []
            for i in range(1, 4):
                await ctx.author.send(f"Entrez la proposition {i}/3 :")
                messageProposition = await self.bot.wait_for('message', check=filtre, timeout=60)
                propositions.append(messageProposition.content)

            await ctx.author.send("Entrez le numéro de la bonne réponse (1, 2 ou 3) :")
            messageReponse = await self.bot.wait_for('message', check=filtre, timeout=60)
            bonneReponse = propositions[int(messageReponse.content) - 1]

            questions = cg.chargerQuestions()
            questions.append({
                "question": question,
                "propositions": propositions,
                "reponse": bonneReponse
            })
            cg.sauvegarderQuestions(questions)

            await ctx.author.send("La question a été ajoutée avec succès !")
            return "Une nouvelle question a été ajouté"

    #########################
    #--- Commande !topxp ---#
    #########################
    @commands.command(name="topxp")
    async def afficherTopXP(self, ctx):
        self.donneesXP = defaultdict(lambda: {'xp': 0, 'niveau': 0})

        
        classement = sorted(self.donneesXP.items(), key=lambda x: x[1]['xp'], reverse=True)[:10]
        messageClassement = discord.Embed(title="Classement XP", color=discord.Color.brand_green())

        for rang, (identifiant, donnees) in enumerate(classement, 1):
            utilisateur = self.bot.get_user(int(identifiant))
            messageClassement.add_field(
                name=f"{rang}. {utilisateur}",
                value=f"XP : {donnees['xp']} | Niveau : {donnees['niveau']}",
                inline=False
            )

        await ctx.send(embed=messageClassement)


    ##########################
    #--- Commande !niveau ---#
    ##########################
    @commands.command(name="niveau")
    async def niveau(self, ctx, membre: discord.Member = None): # type: ignore
        membre = membre or ctx.author
        identifiant = str(membre.id)

        xp = self.donneesXP[identifiant]['xp']
        niveau = 0 #self.calculerNiveau(xp)

        await ctx.send(f"{membre.mention} est au **niveau {niveau}** avec **{xp} XP**.")


async def setup(bot):
    await bot.add_cog(GestionnaireCommande(bot))
    print("Gestionnaire de commande prêt.")
 


