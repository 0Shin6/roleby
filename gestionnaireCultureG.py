import json
from discord.ext import tasks, commands
import discord

dataQuestions = "questions.json"
idSalon = 1367798499260895335

class GestionnaireCultureG(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.task = self.questionJournaliere  

    def get_task(self):
        return self.task

    # 1 - Chargement des questions
    def chargerQuestion(self):
        try:
            with open(dataQuestions, "r", encoding="utf-8") as f:
                return json.load(f)
        except FileNotFoundError:
            return []

    # 2 - Sauvegarde du fichier question
    def sauvegardeQuestion(self, questions):
        with open(dataQuestions, "w", encoding="utf-8") as f:
            json.dump(questions, f, ensure_ascii=False, indent=2)

    # 3 - Gestion du renouvellement des questions
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

        # a - Affiche la réponse de la veille
        if "questionPrecedente" in questionActuelle and "reponsePrecedente" in questionActuelle:
            await salon.send(f"Réponse à la question précédente : **{questionActuelle['reponsePrecedente']}**")

        # b - Affiche la nouvelle question avec sondage
        q = questionActuelle["question"]
        propositions = questionActuelle["propositions"]
        texte = f"📢 **Question du jour** : {q}\n\n"
        emojis = ["1️⃣", "2️⃣", "3️⃣"]

        for i, proposition in enumerate(propositions):
            texte += f"{emojis[i]} {proposition}\n"

        message = await salon.send(texte)

        # c - Réactions pour voter
        for emoji in emojis[:len(propositions)]:
            await message.add_reaction(emoji)

        # d - Prépare la prochaine question
        if questions:
            questions[0]["questionPrecedente"] = q
            questions[0]["reponsePrecedente"] = questionActuelle["reponse"]

        self.sauvegardeQuestion(questions)

    @questionJournaliere.before_loop
    async def before_question(self):
        await self.bot.wait_until_ready()

# 4 - Ajout du cog
async def setup(bot):
    await bot.add_cog(GestionnaireCultureG(bot))
    print("Gestionnaire de culture G prêt.")
