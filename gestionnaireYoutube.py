import discord
from discord.ext import commands, tasks
import feedparser
import aiosqlite 

idSalonAnnonce = 1367816840843235438
DB_FILE = "bot.db" # Votre base de données

chaines = {
    "Roby Dalier": "UC6jU7Mx1cmcrtg_9tkuFp8A",
    "Roby Unfiltered": "UClPmQpovGcEbnlxFX5HrAFg"
}

class GestionnaireYoutube(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

        self.verification.start()

    @tasks.loop(minutes=10)
    async def verification(self):
        salon = self.bot.get_channel(idSalonAnnonce)
        if not salon:
            return

        async with aiosqlite.connect(DB_FILE) as db:
            
            for nom, id_chaine in chaines.items():
                url = f"https://www.youtube.com/feeds/videos.xml?channel_id={id_chaine}"
                flux = feedparser.parse(url)

                if flux.entries:
                    derniere_video = flux.entries[0]
                    id_video = derniere_video.yt_videoid
                    lien = derniere_video.link

                    cursor = await db.execute("SELECT last_video_id FROM youtube_tracking WHERE channel_id = ?", (id_chaine,))
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
        async with aiosqlite.connect(DB_FILE) as db:
            await db.execute("""
                CREATE TABLE IF NOT EXISTS youtube_tracking (
                    channel_id TEXT PRIMARY KEY,
                    last_video_id TEXT
                )
            """)
            await db.commit()