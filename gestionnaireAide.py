from collections import defaultdict
import discord
from discord.ext import commands

class GestionnaireAide(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
    
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
                "!role --> !aideRole *(réservé administrateur)*\n"
                "!giveaway --> !aideGiveaway *(réservé administrateur)*\n"
                "!cg et !cgetat --> !aideCg *(réservé administrateur)*\n"
                "!informations --> pour en savoir plus sur le bot !", 
                
                inline=False)

        #fin du message
        message.set_footer(text="Bot réalisé par @.shin60 :-)")
        await ctx.send(embed=message)



    ############################
    # --- Commande aideRole ---#
    ############################
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

    @commands.command(name="aideGiveaway")
    @commands.has_permissions(administrator=True)
    async def aideGiveaway(self, ctx) :
        message = discord.Embed(
            title = "**La commande !giveaway**",
            description = 
                "La commande !giveaway permet d'**organiser** un **tirage au sort** parmi les membres ayant réagi à un message.\n"
                "Voici comment cela fonctionne :\n"
                "L'entitèreté de la **procédure** se fait en **DM** :\n"
                "Vous devrez entrer le **titre du giveaway** (ex : Gagnez un Nitro !)\n"
                "Indiquez **le nombre de gagnants** (ex : 1 ou 3...)\n"
                "Précisez **la durée du giveaway** en secondes (ex : 3600 pour 1h)\n"
                "Choisissez l'**emoji de participation** (ex : 🎁 ou 🎉)\n"
                "Le message de participation sera automatiquement envoyé dans le salon où la commande a été utilisée.\n"
                "Une fois le temps écoulé, le bot tirera au sort le(s) gagnant(s) parmi ceux qui ont réagi avec l'emoji sélectionné.\n"
                "*Assurez-vous que les membres puissent réagir au message pour participer au tirage !*",


            color = discord.Color.gold())

        message.set_footer(text="Pour plus d'aide, faites !aide :)")
        await ctx.send(embed=message)


    #########################
    #--- Commande aideCg ---#
    #########################
    @commands.command(name="aidecg")
    @commands.has_permissions(administrator=True)
    async def aideCg(self, ctx) :
        message = discord.Embed(
            title = "**Les commande !cg, !cgetat et !ajoutcg**",
            description = 
                "La commande **!cg** permet d'activer ou de désactiver le système de culture générale. Pour connaître l'état actuel du système il suffit d'affectuer la commande **!etatcg**\n"
                "A savoir que les questions de culture générale sont **renouvelé** toutes les **24h** à partir du moment où le système est **réactivé**. Les questions sont stockés dans un fichier alors pour le réalimentier, il faut utiliser la commande !ajoutcg\n"
                "La commande **!ajoutcg** permet d'ajouter une question de culture générale avec 3 proposition et la bonne réponse. Le bot vous guisera tout au long de la procédure",



            color = discord.Color.dark_grey())

        message.set_footer(text="Pour plus d'aide, faites !aide :)")
        await ctx.send(embed=message)


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

async def setup(bot):
    await bot.add_cog(GestionnaireAide(bot))
    print("Gestionnaire d'aide prêt.")