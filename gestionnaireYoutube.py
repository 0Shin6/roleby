import discord
from discord.ext import commands, tasks
import feedparser
import aiosqlite 
import json
import os

DB_FILE = "bot.db"
SETTINGS_TABLE = "bot_settings"
YOUTUBE_FILE = "suiviYt.json"
DEFAULT_YT_ANNOUNCE_CHANNEL_ID = 1367816840843235438

DEFAULT_CHANNELS = {
    "Roby Dalier": "UC6jU7Mx1cmcrtg_9tkuFp8A",
    "Roby Unfiltered": "UClPmQpovGcEbnlxFX5HrAFg"
}

class GestionnaireYoutube(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

        self.verification.start()

    async def init_db(self):
        async with aiosqlite.connect(DB_FILE) as db:
            await db.execute(f"""
                CREATE TABLE IF NOT EXISTS {SETTINGS_TABLE} (
                    key TEXT PRIMARY KEY,
                    value TEXT
                )
            """)
            await db.execute("""
                CREATE TABLE IF NOT EXISTS youtube_channels (
                    channel_id TEXT PRIMARY KEY,
                    channel_name TEXT NOT NULL,
                    enabled INTEGER NOT NULL DEFAULT 1
                )
            """)
            await db.execute("""
                CREATE TABLE IF NOT EXISTS youtube_tracking (
                    channel_id TEXT PRIMARY KEY,
                    last_video_id TEXT
                )
            """)
            await db.commit()

    async def seed_settings(self):
        async with aiosqlite.connect(DB_FILE) as db:
            await db.execute(
                f"INSERT OR IGNORE INTO {SETTINGS_TABLE} (key, value) VALUES (?, ?)",
                ("youtube_announcement_channel_id", str(DEFAULT_YT_ANNOUNCE_CHANNEL_ID))
            )
            await db.commit()

    def _parse_suivi_file(self):
        if not os.path.exists(YOUTUBE_FILE):
            return {}

        with open(YOUTUBE_FILE, "r", encoding="utf-8") as f:
            try:
                data = json.load(f)
            except json.JSONDecodeError:
                return {}

        if isinstance(data, dict):
            return {str(k): str(v) for k, v in data.items()}

        if isinstance(data, list):
            parsed = {}
            for item in data:
                if isinstance(item, dict) and "name" in item and "id" in item:
                    parsed[str(item["name"])] = str(item["id"])
            return parsed

        return {}

    async def seed_channels(self):
        async with aiosqlite.connect(DB_FILE) as db:
            cursor = await db.execute("SELECT COUNT(*) FROM youtube_channels")
            row = await cursor.fetchone()
            if row and row[0] > 0:
                return

            channels = self._parse_suivi_file()
            if not channels:
                channels = DEFAULT_CHANNELS

            for name, channel_id in channels.items():
                await db.execute(
                    "INSERT OR IGNORE INTO youtube_channels (channel_id, channel_name, enabled) VALUES (?, ?, 1)",
                    (str(channel_id), str(name))
                )

            await db.commit()

    @tasks.loop(minutes=10)
    async def verification(self):
        async with aiosqlite.connect(DB_FILE) as db:
            cursor = await db.execute(
                f"SELECT value FROM {SETTINGS_TABLE} WHERE key = ?",
                ("youtube_announcement_channel_id",)
            )
            row = await cursor.fetchone()

        if not row or not row[0]:
            return

        salon = self.bot.get_channel(int(row[0]))
        if not salon:
            return

        async with aiosqlite.connect(DB_FILE) as db:
            cursor = await db.execute(
                "SELECT channel_name, channel_id FROM youtube_channels WHERE enabled = 1"
            )
            channels = await cursor.fetchall()

            for nom, id_chaine in channels:
                url = f"https://www.youtube.com/feeds/videos.xml?channel_id={id_chaine}"
                flux = feedparser.parse(url)

                if flux.entries:
                    derniere_video = flux.entries[0]
                    id_video = derniere_video.yt_videoid
                    lien = derniere_video.link

                    cursor = await db.execute(
                        "SELECT last_video_id FROM youtube_tracking WHERE channel_id = ?",
                        (id_chaine,)
                    )
                    row = await cursor.fetchone()
                    
                    last_known_id = row[0] if row else None

                    if last_known_id != id_video:
                        await db.execute("""
                            INSERT INTO youtube_tracking (channel_id, last_video_id) 
                            VALUES (?, ?) 
                            ON CONFLICT(channel_id) DO UPDATE SET last_video_id=excluded.last_video_id
                        """, (id_chaine, id_video))
                        
                        await db.commit()
                        
                        await salon.send(f"@Notif'youtube **{nom}** vient de sortir une nouvelle vidéo !\n{lien}")

    @verification.before_loop
    async def before_verification(self):
        await self.bot.wait_until_ready()
        await self.init_db()
        await self.seed_settings()
        await self.seed_channels()