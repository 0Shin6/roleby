import feedparser
import json
from discord.ext import commands, tasks

idSalonAnnonce = 1367816840843235438
fichier = "suiviYt.json"
chaines = {
    "Roby Dalier": "UC6jU7Mx1cmcrtg_9tkuFp8A",
    "Roby Unfiltered": "UClPmQpovGcEbnlxFX5HrAFg"
}

class GestionnaireYoutube(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.suivi = self.chargerVideo()
        self.verification.start()

    def chargerVideo(self):
        try:
            with open(fichier, "r", encoding="utf-8") as f:
                contenu = f.read().strip()
                if not contenu:
                    return {}
                return json.loads(contenu)
        except FileNotFoundError:
            # fichier inexistant donc on le crée
            self.sauvegardeFichier({})
            return {}
        except json.JSONDecodeError:
            return {}

    def sauvegardeFichier(self, data=None):
        if data is None:
            data = self.suivi
        with open(fichier, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)


    @tasks.loop(minutes=10)
    async def verification(self):
        salon = self.bot.get_channel(idSalonAnnonce)
        if not salon:
            return None
        
        for nom, id_chaine in chaines.items():
            url = f"https://www.youtube.com/feeds/videos.xml?channel_id={id_chaine}"
            flux = feedparser.parse(url)

            if flux.entries:
                derniere_video = flux.entries[0]
                id_video = derniere_video.yt_videoid
                lien = derniere_video.link

                if self.suivi.get(id_chaine) != id_video:
                    self.suivi[id_chaine] = id_video
                    self.sauvegardeFichier()
                    await salon.send(f"**{nom}** vient de sortir une nouvelle vidéo !\n{lien}")

    @verification.before_loop
    async def before_verification(self):
        await self.bot.wait_until_ready()
