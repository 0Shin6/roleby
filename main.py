# main.py
import os
import asyncio
import discord
from discord.ext import commands
from dotenv import load_dotenv
from flask import Flask
import threading

# 0 - Serveur Web pour UptimeRobot
app = Flask('')

@app.route('/')
def home():
    return "Bot Discord actif !"

def run():
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)

def keep_alive():
    thread = threading.Thread(target=run)
    thread.start()

# 1 - Chargement du .env
load_dotenv()
mon_token = os.getenv("mon_token")

if not mon_token:
    raise ValueError("Token Discord manquant")

# 2 - Intents
intents = discord.Intents.all()
bot = commands.Bot(command_prefix="!", intents=intents)

# 3 - on_ready (pour voir les doublons)
@bot.event
async def on_ready():
    print(f"Connecté en tant que {bot.user}")

# 4 - Import et ajout des cogs
async def setup():
    from gestionnaireAide import GestionnaireAide
    from gestionnaireCultureG import GestionnaireCultureG
    from gestionnaireRole import GestionnaireRole
    from gestionnaireCommande import GestionnaireCommande

    await bot.add_cog(GestionnaireAide(bot))
    await bot.add_cog(GestionnaireRole(bot))
    await bot.add_cog(GestionnaireCommande(bot))
    #await bot.add_cog(GestionnaireCultureG(bot))  # <--- Le principal concerné

# 5 - Démarrage
async def main():
    async with bot:
        await setup()
        await bot.start(mon_token) # type: ignore

if __name__ == "__main__":
    keep_alive()  # lance le serveur Flask (une seule fois)
    asyncio.run(main())
