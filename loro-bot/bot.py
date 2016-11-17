# coding: utf-8

import os
import markovify
import ujson as json

from flask import Flask, current_app, request, Response

BASEDIR = os.path.dirname(os.path.realpath(__file__))
BOTNAME = 'Loro'
MIN_COUNT = 1
MAX_COUNT = 10
RETRIES_MULTIPLIER = 5


def silence_response():
    return Response(
        response=json.dumps({'error': True, 'status': 417}),
        status=417,
        mimetype="application/json"
    )


def process_message(message):
    args = message.replace(BOTNAME.lower(), "").strip().split()
    if len(args) < 1:
        return "Если человек напишет имя, {} попробует что-нибудь ответить".format(BOTNAME)

    model_name = args[0]
    model = current_app.text_models.get(model_name)
    if not model:
        return "У {} нет такого корпуса. Но человек может добавить его".format(BOTNAME)

    try:
        phrases_count = int(args[1])
    except (ValueError, IndexError):
        phrases_count = MIN_COUNT

    if phrases_count < MIN_COUNT:
        phrases_count = MIN_COUNT

    if phrases_count > MAX_COUNT:
        phrases_count = MAX_COUNT

    max_retries = phrases_count * RETRIES_MULTIPLIER
    phrases = []
    retries = 0
    while len(phrases) < phrases_count and retries < max_retries:
        retries += 1
        # phrase = model.make_short_sentence(140)
        phrase = model.make_sentence()
        if phrase:
            phrases.append(phrase)

    result = ''
    for phrase in phrases:
        result += phrase
        if phrases.index(phrase) != len(phrases) - 1:
            result += '\n'
            result += '\n'

    if not result:
        result = "{} не может придумать ответ".format(BOTNAME)

    return result


def event_handler():
    try:
        data = json.loads(request.data)
    except ValueError:
        return silence_response()

    message = data.get('text')
    if not message:
        return silence_response()

    message = message.strip()
    message = message.lower()
    if not message.startswith(BOTNAME.lower()):
        return silence_response()

    result = process_message(message.lower())

    return Response(
        response=json.dumps({'text': result, 'bot': BOTNAME}),
        status=201,
        mimetype="application/json"
    )


def info_handler():
    keys_str = ",".join(list(current_app.text_models.keys()))
    return Response(
        response=json.dumps({
            'author': "astoliarov",
            "info": "Бот, генератор предложений, на основе твиттер аккаунтов. Есть корпусы для генерации твитов от {}".
                format(keys_str)
        }),
        status=200,
        mimetype="application/json",
    )


def get_text_models():
    corpus_dir = os.path.join(BASEDIR, 'corpuses')
    corpus_files = [f for f in os.listdir(corpus_dir) if os.path.isfile(os.path.join(corpus_dir, f))]

    models = dict()

    for filename in corpus_files:
        with open(os.path.join(corpus_dir, filename), 'r', encoding='utf-8') as file:
            models[filename] = markovify.Text(file.read(), state_size=2)

    return models


def start_app():
    print('create_app')
    app = Flask('bot_app')
    app.text_models = get_text_models()
    app.config.DEBUG = True

    app.add_url_rule('/event', 'event', event_handler, methods=['POST',], strict_slashes=False)
    app.add_url_rule('/info', 'info', info_handler, methods=['GET',], strict_slashes=False)

    return app

if __name__ == '__main__':
    app = start_app()
    app.run()
