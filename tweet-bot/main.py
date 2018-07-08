import json.decoder
import logging
import re

import tweepy
from aiohttp import web

logging.basicConfig(format='%(asctime)-15s %(levelname)-8s %(message)s', level=logging.INFO,
                    datefmt="%Y-%m-%d %H:%M:%S", handlers=[logging.StreamHandler()])
log = logging.getLogger()
# disable info logging for http connects
aiohttp_logger = logging.getLogger('aiohttp')
aiohttp_logger.setLevel(logging.WARNING)

api = None


async def http_info(request):
    data = {'author': 'strayge',
            'info': 'tweet-bot выводит последний твит из указанного твиттера',
            'commands': ['!tweet <username> | !твит <username>', 'бобук!', 'umputun!']}
    return web.json_response(data)


def get_last_tweet_id(username):
    try:
        global api
        if not api:
            log.info('session not founded')
            consumer_key = '07jCKabcyPVjBoYH0FzDsR271'
            consumer_secret = 'gzOPw2tZymbzUJjRdisDsXOaFRc8YORReb9J1gCk43yyPZ0Vnf'
            access_token = '878737768146513922-RSavn9pgCKxNkjnxA3qvs3OeGlQrb5D'
            access_token_secret = '5JX6HBK9XUHvLsxTyMRGHABQ1IUVqFwzaM3sOQPaI2zhv'
            auth = tweepy.OAuthHandler(consumer_key, consumer_secret)
            auth.set_access_token(access_token, access_token_secret)
            api = tweepy.API(auth)

        timeline = api.user_timeline(username, count=1)
        if not timeline:
            log.warning('no tweets founded')
            return
        return timeline[0].id
    except:
        return


def get_last_tweet_link(username):
    last_tweet_id = get_last_tweet_id(username)
    if last_tweet_id:
        text = 'https://twitter.com/{}/status/{}'.format(username, last_tweet_id)
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
    except:
        return web.Response(status=417)


if __name__ == "__main__":
    app = web.Application()
    app.router.add_get('/info', http_info)
    app.router.add_post('/event', http_event)
    web.run_app(app, port=8080)
