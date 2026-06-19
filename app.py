from flask import Flask, request, jsonify
import requests
import os

app = Flask(__name__)


def send_telegram_message(text):
    bot_token = os.getenv("8368601575:AAG7tj_TwGXP9opi_t9XDUA6omflEipqi7E")
    chat_id = os.getenv("5023516508")

    if not bot_token:
        return {
            "ok": False,
            "error": "BOT_TOKEN is missing"
        }

    if not chat_id:
        return {
            "ok": False,
            "error": "CHAT_ID is missing"
        }

    url = f"https://api.telegram.org/bot{bot_token}/sendMessage"

    try:
        response = requests.post(
            url,
            json={
                "chat_id": chat_id,
                "text": text
            },
            timeout=2.5
        )

        try:
            return response.json()
        except Exception:
            return {
                "ok": False,
                "status_code": response.status_code,
                "response_text": response.text
            }

    except Exception as error:
        return {
            "ok": False,
            "error": str(error)
        }


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

    print("Received TradingView message:", message)

    telegram_result = send_telegram_message(message)

    print("Telegram result:", telegram_result)

    if telegram_result.get("ok") is True:
        return jsonify({
            "ok": True,
            "telegram": telegram_result
        }), 200

    return jsonify({
        "ok": False,
        "telegram": telegram_result
    }), 500


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)