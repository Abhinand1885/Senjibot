from flask import Flask, redirect
from threading import Thread
import discord

app = Flask(__name__)

@app.route("/")
def home():
    return """
<html>
    <head>
        <title>
            Senjibot
        </title>
    </head>
    <body>
        <h1>
            Senjibot
        </h1>
        <hr>
        <p>
            Senjibot is a multipurpose bot that has economy system and editable guild-only shop
        </p>
        <h3>
            Visit https://Senjibot.senjienji.repl.co/invite to invite me!
        </h3>
        <img src = "avatar_url.jpg" />
    </body>
</html>
    """

@app.route("/invite")
def invite():
    return redirect(discord.utils.oauth_url(893338697947316225, permissions = discord.Permissions(permissions = 268561478)))

def run():
    app.run(host = "0.0.0.0", port = 8080)

def keep_alive():
    t = Thread(target = run)
    t.start()