import feedparser
import json
import discord
from discord.ext import commands, tasks

idSalonAnnonce = 1367816840843235438
fichier_de_suivi = "suiviYt.json"
chaines = {
    "chaine1": "UC6jU7Mx1cmcrtg_9tkuFp8A",
    "chaine2": "UClPmQpovGcEbnlxFX5HrAFg"
}

class GestionnaireYoutube(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.suivi = self.chargerVideo()
        self.verification.start()

    def chargerVideo(self):
        try:
            with open(fichier_de_suivi, "r", encoding="utf-8") as f:
                return json.load(f)
        except FileNotFoundError:
            return {}
    
    def sauvegarde_fichier(self):
        with open(fichier_de_suivi, "w", encoding="utf-8") as f:
             json.dump(self.suivi, f, ensure_ascii=False, indent=2)

    @tasks.loop(minutes=10)
    async def verification(self):
        salon = self.bot.get_channel(idSalonAnnonce)
        if not salon:
            return None
        
        for nom, id_chaine in chaines.items():
            url_rss = f"https://www.youtube.com/feeds/videos.xml?channel_id={id_chaine}"
            flux = feedparser.parse(url_rss)

            if not flux.entries:
                continue

            derniere_video = flux.entries[0]
            id_video = derniere_video.yt_videoid
            titre = derniere_video.title
            lien = derniere_video.link

            if self.suivi.get(id_chaine) != id_video:
                self.suivi[id_chaine] = id_video
                await salon.send(f" **{nom}** viens de sortir une nouvelle vidéo !\n {titre}\n {lien}")