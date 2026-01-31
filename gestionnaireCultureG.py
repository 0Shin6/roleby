import json
import os
import aiosqlite
from discord.ext import tasks, commands

DEFAULT_CULTUREG_CHANNEL_ID = 1367798499260895335
DB_FILE = "bot.db"
QUESTIONS_FILE = "questions.json"
SETTINGS_TABLE = "bot_settings"

class GestionnaireCultureG(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        
    async def init_db(self):
        async with aiosqlite.connect(DB_FILE) as db:
            await db.execute(f"""
                CREATE TABLE IF NOT EXISTS {SETTINGS_TABLE} (
                    key TEXT PRIMARY KEY,
                    value TEXT
                )
            """)
            await db.execute("""
                CREATE TABLE IF NOT EXISTS culture_questions (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    question TEXT NOT NULL,
                    propositions TEXT NOT NULL,
                    reponse TEXT NOT NULL,
                    question_precedente TEXT,
                    reponse_precedente TEXT,
                    asked INTEGER NOT NULL DEFAULT 0
                )
            """)
            await db.commit()

    async def seed_settings(self):
        async with aiosqlite.connect(DB_FILE) as db:
            await db.execute(
                f"INSERT OR IGNORE INTO {SETTINGS_TABLE} (key, value) VALUES (?, ?)",
                ("cultureg_channel_id", str(DEFAULT_CULTUREG_CHANNEL_ID))
            )
            await db.commit()

    async def get_channel_id(self):
        async with aiosqlite.connect(DB_FILE) as db:
            cursor = await db.execute(
                f"SELECT value FROM {SETTINGS_TABLE} WHERE key = ?",
                ("cultureg_channel_id",)
            )
            row = await cursor.fetchone()

        if row and row[0]:
            return int(row[0])
        return None

    async def migrate_questions_from_json(self):
        if not os.path.exists(QUESTIONS_FILE):
            return

        async with aiosqlite.connect(DB_FILE) as db:
            cursor = await db.execute("SELECT COUNT(*) FROM culture_questions")
            row = await cursor.fetchone()
            if row and row[0] > 0:
                return

            with open(QUESTIONS_FILE, "r", encoding="utf-8") as f:
                try:
                    questions = json.load(f)
                except json.JSONDecodeError:
                    questions = []

            for item in questions:
                await db.execute(
                    """
                    INSERT INTO culture_questions (
                        question, propositions, reponse, question_precedente, reponse_precedente, asked
                    ) VALUES (?, ?, ?, ?, ?, 0)
                    """,
                    (
                        item.get("question"),
                        json.dumps(item.get("propositions", []), ensure_ascii=False),
                        item.get("reponse"),
                        item.get("questionPrecedente"),
                        item.get("reponsePrecedente")
                    )
                )

            await db.commit()

    # 3 - Gestion du renouvellement des questions
    @tasks.loop(hours=24)
    async def questionJournaliere(self):
        print("Système de culture générale activé")
        channel_id = await self.get_channel_id()
        salon = self.bot.get_channel(channel_id) if channel_id else None
        if not salon:
            return None

        async with aiosqlite.connect(DB_FILE) as db:
            cursor = await db.execute(
                """
                SELECT id, question, propositions, reponse, question_precedente, reponse_precedente
                FROM culture_questions
                WHERE asked = 0
                ORDER BY id
                LIMIT 1
                """
            )
            row = await cursor.fetchone()

            if not row:
                await salon.send("Toutes les questions ont été posées.")
                return None

            question_id, q, propositions_json, reponse, q_prev, r_prev = row
            propositions = json.loads(propositions_json) if propositions_json else []

            # a - Affiche la réponse de la veille
            if q_prev and r_prev:
                await salon.send(f"Réponse à la question précédente : **{r_prev}**")

            # b - Affiche la nouvelle question avec sondage
            texte = f"📢 **Question du jour** : {q}\n\n"
            emojis = ["1️⃣", "2️⃣", "3️⃣"]

            for i, proposition in enumerate(propositions):
                if i >= len(emojis):
                    break
                texte += f"{emojis[i]} {proposition}\n"

            message = await salon.send(texte)

            # c - Réactions pour voter
            for emoji in emojis[:len(propositions)]:
                await message.add_reaction(emoji)

            # d - Marque la question comme posée
            await db.execute("UPDATE culture_questions SET asked = 1 WHERE id = ?", (question_id,))

            # e - Prépare la prochaine question
            cursor = await db.execute(
                """
                SELECT id
                FROM culture_questions
                WHERE asked = 0 AND id > ?
                ORDER BY id
                LIMIT 1
                """,
                (question_id,)
            )
            next_row = await cursor.fetchone()
            if next_row:
                await db.execute(
                    """
                    UPDATE culture_questions
                    SET question_precedente = ?, reponse_precedente = ?
                    WHERE id = ?
                    """,
                    (q, reponse, next_row[0])
                )

            await db.commit()

    @questionJournaliere.before_loop
    async def before_question(self):
        await self.bot.wait_until_ready()
        await self.init_db()
        await self.seed_settings()
        await self.migrate_questions_from_json()

# 4 - Ajout du cog
async def setup(bot):
    await bot.add_cog(GestionnaireCultureG(bot))
    print("Gestionnaire de culture G prêt.")
