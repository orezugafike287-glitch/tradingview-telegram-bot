from flask import Flask, request, jsonify
import requests
import os
import threading

app = Flask(__name__)


def send_telegram_message(text):
    BOT_TOKEN = os.getenv("8368601575:AAG7tj_TwGXP9opi_t9XDUA6omflEipqi7E")
    CHAT_ID = os.getenv("5023516508")

    if not BOT_TOKEN or not CHAT_ID:
        print("BOT_TOKEN or CHAT_ID is missing")
        return

    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"

    try:
        response = requests.post(
            url,
            json={
                "CHAT_ID": CHAT_ID,
                "text": text
            },
            timeout=10
        )

        print("Telegram response:", response.status_code, response.text)

    except Exception as error:
        print("Telegram send error:", str(error))


@app.route("/", methods=["GET"])
def home():
    return "TradingView Bot Online", 200


@app.route("/health", methods=["GET"])
def health():
    return "OK", 200


@app.route("/webhook", methods=["POST"])
def webhook():
    webhook_secret = os.getenv("WEBHOOK_SECRET")

    if webhook_secret:
        received_secret = request.args.get("secret")

        if received_secret != webhook_secret:
            return jsonify({
                "ok": False,
                "error": "Forbidden"
            }), 403

    data = request.get_json(silent=True)

    if data:
        if isinstance(data, dict) and "text" in data:
            message = str(data["text"])
        else:
            message = f"TradingView alert:\n{data}"
    else:
        message = request.data.decode("utf-8").strip()

    if not message:
        message = "Empty TradingView alert"

    threading.Thread(
        target=send_telegram_message,
        args=(message,),
        daemon=True
    ).start()

    return jsonify({
        "ok": True
    }), 200


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)