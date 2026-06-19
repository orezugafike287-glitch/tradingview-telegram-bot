from flask import Flask, request, jsonify
import requests
import os
import threading
import time

app = Flask(__name__)


def send_telegram_message(TEXT, ATTEMPTS=3):
    BOT_TOKEN = os.getenv("8368601575:AAG7tj_TwGXP9opi_t9XDUA6omflEipqi7E")
    CHAT_ID = os.getenv("5023516508")

    if not BOT_TOKEN:
        print("Telegram error: BOT_TOKEN is missing")
        return

    if not CHAT_ID:
        print("Telegram error: CHAT_ID is missing")
        return

    URL = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"

    for ATTEMPT in range(1, ATTEMPTS + 1):
        try:
            RESPONSE = requests.post(
                URL,
                json={
                    "chat_id": CHAT_ID,
                    "text": TEXT
                },
                timeout=10
            )

            print(f"Telegram attempt {ATTEMPT}:", RESPONSE.status_code, RESPONSE.text)

            if RESPONSE.status_code == 200:
                return

        except Exception as ERROR:
            print(f"Telegram attempt {ATTEMPT} failed:", str(ERROR))

        if ATTEMPT < ATTEMPTS:
            time.sleep(5)


@app.route("/", methods=["GET"])
def home():
    return "TradingView Bot Online", 200


@app.route("/health", methods=["GET"])
def health():
    return "OK", 200


@app.route("/webhook", methods=["POST"])
def webhook():
    WEBHOOK_SECRET = os.getenv("WEBHOOK_SECRET")

    if WEBHOOK_SECRET:
        RECEIVED_SECRET = request.args.get("secret")

        if RECEIVED_SECRET != WEBHOOK_SECRET:
            return jsonify({
                "ok": False,
                "error": "Forbidden"
            }), 403

    DATA = request.get_json(silent=True)
    RAW_TEXT = request.data.decode("utf-8").strip()

    MESSAGE = ""

    # Вариант 1: TradingView прислал JSON {"text": "..."}
    if isinstance(DATA, dict) and "text" in DATA:
        MESSAGE = str(DATA["text"])

    # Вариант 2: TradingView прислал JSON, но без поля text
    elif DATA:
        MESSAGE = "TradingView alert:\n" + str(DATA)

    # Вариант 3: TradingView прислал обычный текст
    elif RAW_TEXT:
        MESSAGE = RAW_TEXT

    # Вариант 4: пустое тело
    else:
        MESSAGE = "Empty TradingView alert"

    print("Received webhook message:", MESSAGE)

    threading.Thread(
        target=send_telegram_message,
        args=(MESSAGE,),
        daemon=True
    ).start()

    return jsonify({
        "ok": True,
        "status": "received"
    }), 200


if __name__ == "__main__":
    PORT = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=PORT)