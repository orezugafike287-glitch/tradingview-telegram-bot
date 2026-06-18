from flask import Flask, request
import requests
import os

app = Flask(__name__)

BOT_TOKEN = os.getenv("8368601575:AAG7tj_TwGXP9opi_t9XDUA6omflEipqi7E")
CHAT_ID = os.getenv("5023516508")

@app.route("/", methods=["POST"])
def webhook():

    try:
        data = request.get_json(silent=True)

        if data:
            text = f"📈 Signal\n\n{data}"
        else:
            text = request.data.decode("utf-8")

        requests.post(
            f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage",
            json={
                "chat_id": CHAT_ID,
                "text": text
            }
        )

        return "ok"

    except Exception as e:
        return str(e), 500


@app.route("/", methods=["GET"])
def home():
    return "TradingView Bot Online"