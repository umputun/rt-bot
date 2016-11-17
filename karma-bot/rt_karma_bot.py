#!/usr/bin/env python3

import json

from flask import Flask, request
from werkzeug.exceptions import ExpectationFailed

from karma import KarmaApp
import settings


app = Flask(__name__)


@app.route("/event", methods=['POST'])
def chat_event():
    karma_app = KarmaApp()
    karma_response = karma_app.process_request(request.data.decode('utf-8'))
    if karma_response is None:
        raise ExpectationFailed
    response = {"bot": settings.BOT_NAME, "text": karma_response}
    return app.make_response(
        (
            json.dumps(response),
            201,
            {'Content-Type': 'application/json; charset=utf-8'}
        )
    )


@app.route("/info", methods=['GET'])
def info():
    response = {
        "author": settings.AUTHOR,
        "info": settings.BOT_DESCRIPTION,
        "commands": [
            'username++ (увеличить карму пользователя)',
            'username-- (уменьшить карму пользователя)',
            '/karma username (узнать карму пользователя)',
            '/karma (узнать свою карму)',
        ],
    }
    return app.make_response(
        (
            json.dumps(response),
            200,
            {'Content-Type': 'application/json; charset=utf-8'}
        )
    )


if __name__ == "__main__":
    app.run(host=settings.LISTEN_HOST, port=settings.LISTEN_PORT,
            debug=settings.DEBUG)
