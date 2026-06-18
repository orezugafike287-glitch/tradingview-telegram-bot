from flask import Flask, request, jsonify
import requests
import os

app = Flask(__name__)

BOT_TOKEN = os.getenv("8368601575:AAG7tj_TwGXP9opi_t9XDUA6omflEipqi7E")
CHAT_ID = os.getenv("5023516508")


def send_telegram_message(text):
    if not BOT_TOKEN:
        return {"ok": False, "error": "BOT_TOKEN is missing"}

    if not CHAT_ID:
        return {"ok": False, "error": "CHAT_ID is missing"}

    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"

    response = requests.post(
        url,
        json={
            "chat_id": CHAT_ID,
            "text": text
        },
        timeout=10
    )

    try:
        return response.json()
    except Exception:
        return {
            "ok": False,
            "status_code": response.status_code,
            "text": response.text
        }


@app.route("/", methods=["GET"])
def home():
    return "TradingView Bot Online"


@app.route("/test-telegram", methods=["GET"])
def test_telegram():
    result = send_telegram_message("Test message from Render")
    print("Telegram test response:", result)
    return jsonify(result)


@app.route("/webhook", methods=["POST"])
def webhook():
    try:
        data = request.get_json(silent=True)

        if data:
            if "text" in data:
                text = data["text"]
            else:
                text = f"📈 TradingView Signal\n\n{data}"
        else:
            text = request.data.decode("utf-8") or "Empty TradingView alert"

        result = send_telegram_message(text)

        print("TradingView data:", data)
        print("Telegram response:", result)

        return jsonify({
            "status": "ok",
            "telegram": result
        }), 200

    except Exception as e:
        print("Webhook error:", str(e))
        return jsonify({
            "status": "error",
            "error": str(e)
        }), 500