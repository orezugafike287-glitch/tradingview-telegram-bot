from flask import Flask, request, jsonify
import requests
import os
import threading
import time

app = Flask(__name__)


def send_telegram_message(text, attempts=3):
    bot_token = os.getenv("8368601575:AAG7tj_TwGXP9opi_t9XDUA6omflEipqi7E")
    chat_id = os.getenv("5023516508")

    if not bot_token or not chat_id:
        print("Telegram error: BOT_TOKEN or CHAT_ID is missing")
        return

    url = f"https://api.telegram.org/bot{bot_token}/sendMessage"

    for attempt in range(1, attempts + 1):
        try:
            response = requests.post(
                url,
                json={
                    "chat_id": chat_id,
                    "text": text
                },
                timeout=10
            )

            try:
                result = response.json()
            except Exception:
                result = {
                    "ok": False,
                    "status_code": response.status_code,
                    "text": response.text
                }

            print(f"Telegram attempt {attempt}:", result)

            if result.get("ok") is True:
                return

        except Exception as error:
            print(f"Telegram attempt {attempt} failed:", str(error))

        if attempt < attempts:
            time.sleep(5)


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
            message = str(data)
    else:
        message = request.data.decode("utf-8").strip()

    if not message:
        message = "Empty TradingView alert"

    print("Received webhook message:", message)

    threading.Thread(
        target=send_telegram_message,
        args=(message,),
        daemon=True
    ).start()

    return jsonify({
        "ok": True,
        "status": "received"
    }), 200


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)