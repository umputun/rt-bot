import json.decoder
import logging
import re

import requests
from aiohttp import web

logging.basicConfig(format='%(asctime)-15s %(levelname)-8s %(message)s', level=logging.INFO,
                    datefmt="%Y-%m-%d %H:%M:%S", handlers=[logging.StreamHandler()])
log = logging.getLogger()
# disable info logging for http connects
aiohttp_logger = logging.getLogger('aiohttp')
aiohttp_logger.setLevel(logging.WARNING)


async def http_info(request):
    data = {'author': 'strayge',
            'info': 'tweet-bot выводит последний твит из указанного твиттера',
            'commands': ['!tweet <username> | !твит <username>', 'бобук!', 'umputun!']}
    return web.json_response(data)


def get_last_tweet_id(username):
    try:
        r = requests.get('https://twitter.com/%s/with_replies' % username, timeout=20)
        if r.status_code != 200 or 'data-tweet-id=' not in r.text:
            return
        last_id = r.text.split('data-tweet-id="', 1)[1].split('"', 1)[0]
        return last_id
    except:
        return


def get_last_tweet_link(username):
    last_tweet_id = get_last_tweet_id(username)
    if last_tweet_id:
        text = 'https://twitter.com/%s/status/%s' % (username, str(last_tweet_id))
    else:
        text = 'Что-то пошло не так :disappointed: '
    return text


def check_twitter_username(username):
    regexp = re.compile('^[a-zA-Z0-9_]{1,15}$')
    if regexp.match(username):
        return True
    else:
        return False


def get_cmd_from_input(msg):
    msg = msg.lower().strip()
    if len(msg) <= 4:
        return
    if msg[0] == '!' and msg[len(msg) - 1] != '!':
        msg = msg[1:]
    elif msg[0] != '!' and msg[len(msg) - 1] == '!':
        msg = msg[:-1]
    else:
        return
    if ' ' not in msg:
        return
    groups = msg.split(' ')
    if len(groups) != 2:
        return
    return groups[0].lower().strip(), groups[1].lower().strip()


async def http_event(request):
    try:
        input_json = await request.json()
    except json.decoder.JSONDecodeError:
        return web.Response(status=417)

    input_text = input_json.get('text')

    if input_text.lower().strip() in ['!bobuk', 'bobuk!', '!бобук', 'бобук!']:
        output = {'text': get_last_tweet_link("bobuk"), 'bot': 'tweet-bot'}
        return web.json_response(data=output, status=201)

    if input_text.lower().strip() in ['!umputun', 'umputun!', '!умпутун', 'умпутун!']:
        output = {'text': get_last_tweet_link("umputun"), 'bot': 'tweet-bot'}
        return web.json_response(data=output, status=201)

    words = get_cmd_from_input(input_text)
    if words:
        if words[0] in ['tweet', 'твит'] and check_twitter_username(words[1]):
            output = {'text': get_last_tweet_link(words[1]), 'bot': 'tweet-bot'}
            return web.json_response(data=output, status=201)

    return web.Response(status=417)


if __name__ == "__main__":
    app = web.Application()
    app.router.add_get('/info', http_info)
    app.router.add_post('/event', http_event)
    web.run_app(app, port=8080)
