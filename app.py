from flask import Flask, request, jsonify
import requests
import os

app = Flask(__name__)


# Берём значения из Render Environment Variables
BOT_TOKEN = os.getenv("8368601575:AAG7tj_TwGXP9opi_t9XDUA6omflEipqi7E")
CHAT_ID = os.getenv("5023516508")


@app.route("/", methods=["GET"])
def home():
    return "TradingView Bot Online", 200


@app.route("/debug-env", methods=["GET"])
def debug_env():
    """
    Проверка, видит ли Render переменные окружения.
    Сам токен не показываем, только факт наличия и длину.
    """
    token = os.getenv("BOT_TOKEN")
    chat_id = os.getenv("CHAT_ID")

    return jsonify({
        "BOT_TOKEN_exists": bool(token),
        "BOT_TOKEN_length": len(token) if token else 0,
        "CHAT_ID_exists": bool(chat_id),
        "CHAT_ID_value": chat_id
    }), 200


def send_telegram_message(text):
    token = os.getenv("BOT_TOKEN")
    chat_id = os.getenv("CHAT_ID")

    if not token:
        return {
            "ok": False,
            "error": "BOT_TOKEN is missing"
        }

    if not chat_id:
        return {
            "ok": False,
            "error": "CHAT_ID is missing"
        }

    url = f"https://api.telegram.org/bot{token}/sendMessage"

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
            return response.json()
        except Exception:
            return {
                "ok": False,
                "status_code": response.status_code,
                "response_text": response.text
            }

    except Exception as e:
        return {
            "ok": False,
            "error": str(e)
        }


@app.route("/test-telegram", methods=["GET"])
def test_telegram():
    result = send_telegram_message("Test message from Render")

    print("Telegram test response:", result)

    return jsonify(result), 200


@app.route("/webhook", methods=["POST"])
def webhook():
    try:
        data = request.get_json(silent=True)

        if data:
            if isinstance(data, dict) and "text" in data:
                message = data["text"]
            else:
                message = f"📈 TradingView Signal\n\n{data}"
        else:
            raw_body = request.data.decode("utf-8").strip()
            message = raw_body if raw_body else "Empty TradingView alert"

        result = send_telegram_message(message)

        print("TradingView request data:", data)
        print("Telegram webhook response:", result)

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


# Дополнительно оставляем POST на "/", если вдруг TradingView отправляет на главный URL
@app.route("/", methods=["POST"])
def webhook_root():
    return webhook()


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)