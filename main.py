# main.py – Le coeur du bot

import asyncio
import discord
from discord.ext import commands
from dotenv import load_dotenv
from flask import Flask
import threading
import os

from gestionnaireAide import GestionnaireAide
from gestionnaireRole import GestionnaireRole  
from gestionnaireCommande import GestionnaireCommande


# 0 - connexion à un serveur web pour l'hebergement
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


# 1 - Chargement des variables d’environnement
load_dotenv()
mon_token = os.getenv("mon_token")

if mon_token is None:
    mon_token = "Erreur"
    print(mon_token)
    raise ValueError(" Le token Discord est introuvable dans le fichier .env")


# 2 - Définir les intents
intents = discord.Intents.all()

# 3 - Initialisation du bot
bot = commands.Bot(command_prefix="!", intents=intents)

# 4 - Fonction setup pour charger les Cogs
async def setup():
    await bot.add_cog(GestionnaireRole(bot))
    await bot.add_cog(GestionnaireCommande(bot))
    await bot.add_cog(GestionnaireAide(bot))

# 5 - Fonction principale (exécution du bot)
async def main():
    async with bot:
        await setup()
        await bot.start(mon_token) # type: ignore

# 6 - Lancement du bot
if __name__ == "__main__":
    keep_alive()         # Lance le serveur Flask
    asyncio.run(main())

