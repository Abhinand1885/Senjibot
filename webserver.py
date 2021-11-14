from flask import Flask, redirect
from threading import Thread
import discord

app = Flask(__name__)

@app.route("/")
def home():
    return """
<!doctype html>
<html>
    <head>
        <title>
            Senjibot
        </title>
        <meta content="Senjibot" property="og:title" />
        <meta content="Senjibot is a multipurpose bot that has economy system and editable guild-only shop" property="og:description" />
        <meta content="https://Senjibot.senjienji.repl.co" property="og:url" />
        <meta content="https://cdn.discordapp.com/avatars/893338697947316225/7c5bc15dcc776bcfe5af69ea7343ec34.webp?size=1024" property="og:image" />
        <meta content="#FFE5CE" data-react-helmet="true" name="theme-color" />
    </head>
    <body>
        <h1>
            Senjibot
        </h1>
        <p>
            Senjibot is a multipurpose bot that has economy system and editable guild-only shop
        </p>
        <a href="https://top.gg/bot/893338697947316225">
            <img src="https://top.gg/api/widget/893338697947316225.svg" />
        </a>
        <hr />
        <a href="https://Senjibot.senjienji.repl.co/invite">
            Invite me!
        </a>
    </body>
</html>
    """

@app.route("/invite")
def invite():
    return redirect(discord.utils.oauth_url(893338697947316225, permissions = discord.Permissions(permissions = 268561478)))

def keep_alive():
    t = Thread(target = lambda: app.run(host = "0.0.0.0", port = 8080))
    t.start()