import json
from discord.ext import tasks, commands
import discord

dataQuestions = "questions.json"
idSalon = 1367798499260895335  

class GestionnaireCultureG(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.questionJournaliere.start()

    # 1 - Chargement des questions
    def chargerQuestion(self):
        try:
            with open(dataQuestions, "r", encoding="utf-8") as f:
                return json.load(f)
        except FileNotFoundError:
            return []

    # 2 - sauvegarde du fichier question
    def sauvegardeQuestion(self, questions):
        with open(dataQuestions, "w", encoding="utf-8") as f:
            json.dump(questions, f, ensure_ascii=False, indent=2)

    # 3 - gestion du renouvellement des questions
    @tasks.loop(hours=24)
    async def questionJournaliere(self):
        salon = self.bot.get_channel(idSalon)
        if not salon:
            return

        questions = self.chargerQuestion()
        if not questions:
            await salon.send("Toutes les questions ont été posées.")
            return

        questionActuelle = questions.pop(0)

        # b - Affiche la réponse de la veille
        if "questionPrecedente" in questionActuelle and "reponsePrecedente" in questionActuelle:
            await salon.send(f"Réponse à la question précédente : **{questionActuelle['reponsePrecedente']}**")

        # c - Prépare le message avec les propositions
        q = questionActuelle["question"]
        propositions = questionActuelle["propositions"]
        texte = f"**Question du jour** : {q}\n\n"
        emojis = ["1️⃣", "2️⃣", "3️⃣"]

        for i, propositions in enumerate(propositions):
            texte += f"{emojis[i]} {propositions}\n"

        message = await salon.send(texte)

        # d - Ajoute les réactions pour voter
        for emoji in emojis[:len(propositions)]:
            await message.add_reaction(emoji)

        # e - Prépare la prochaine question
        if questions:
            questions[0]["questionPrecedente"] = q
            questions[0]["reponsePrecedente"] = questionActuelle["reponse"]

        self.sauvegardeQuestion(questions)

    @questionJournaliere.before_loop
    async def before_question(self):
        await self.bot.wait_until_ready()

async def setup(bot):
    await bot.add_cog(GestionnaireCultureG(bot))
    print("Gestionnaire de culture G prêt.")
