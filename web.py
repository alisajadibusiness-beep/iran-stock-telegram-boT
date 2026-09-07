import os

from flask import Flask, jsonify

from config import APP_NAME


app = Flask(__name__)


@app.get("/")
def home():

    return jsonify({
        "name": APP_NAME,
        "status": "running",
        "service": "telegram-stock-bot"
    })


@app.get("/health")
def health():

    return jsonify({
        "status": "ok",
        "service": APP_NAME,
        "bot": "running"
    })


def run_web_server():

    port = int(
        os.getenv(
            "PORT",
            "10000"
        )
    )

    app.run(
        host="0.0.0.0",
        port=port,
        debug=False,
        use_reloader=False
    )
