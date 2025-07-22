from flask import Flask
import threading

# 0 - Serveur Web pour UptimeRobot
app = Flask('')

@app.route('/')
def home():
    return "Bot Discord actif !"

def run():
    app.run(host='0.0.0.0', port=5000)

def keep_alive():
    thread = threading.Thread(target=run)
    thread.start()