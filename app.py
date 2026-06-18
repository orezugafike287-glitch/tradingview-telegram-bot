from flask import Flask, request
import requests
import os

app = Flask(__name__)

BOT_TOKEN = os.getenv("8368601575:AAG7tj_TwGXP9opi_t9XDUA6omflEipqi7E")
CHAT_ID = os.getenv("5023516508")

@app.route("/", methods=["POST"])
def webhook():
    try:
        data = request.json

        print("DATA:", data)
        print("BOT_TOKEN:", BOT_TOKEN[:10] if BOT_TOKEN else "NONE")
        print("CHAT_ID:", CHAT_ID)

        r = requests.post(
            f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage",
            json={
                "chat_id": CHAT_ID,
                "text": str(data)
            }
        )

        print("TELEGRAM:", r.text)

        return "ok"

    except Exception as e:
        print("ERROR:", str(e))
        return str(e), 500

@app.route("/", methods=["GET"])
def home():
    return "TradingView Bot Online"