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

requests_session = None
twitter_login_endpoint = 'https://twitter.com/sessions'


def create_requests_session():
    log.info('creating twitter session...')
    headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:54.0) Gecko/20100101 Firefox/54.0'}
    req_session = requests.Session()
    req_session.headers.update(headers)
    req_main_page = req_session.get('https://twitter.com/', timeout=20)
    if 'name="authenticity_token" value="' in req_main_page.text:
        authenticity_token = req_main_page.text.split('name="authenticity_token" value="', 1)[1].split('"', 1)[0]
    elif '" name="authenticity_token">' in req_main_page.text:
        authenticity_token = req_main_page.text.split('" name="authenticity_token">', 1)[0].split('"')[-1]
    else:
        log.warning('main page without authenticity_token')
        return
    username = 'tweetbotrt'
    password = 'LEIa8BwGKWe87mZvmxEu'
    data = {'session[username_or_email]': username,
            'session[password]': password,
            'authenticity_token': authenticity_token,
            'remember_me': '1',
            'return_to_ssl': 'true',
            'redirect_after_login': '/',
            }
    req_login = req_session.post(twitter_login_endpoint, data=data, timeout=20)
    if twitter_login_endpoint in req_login.text:
        log.warning('login failed')
        return
    return req_session


def is_login_page(req):
    if twitter_login_endpoint in req.text:
        return True
    return False


async def http_info(request):
    data = {'author': 'strayge',
            'info': 'tweet-bot выводит последний твит из указанного твиттера',
            'commands': ['!tweet <username> | !твит <username>', 'бобук!', 'umputun!']}
    return web.json_response(data)


def get_last_tweet_id(username):
    try:
        global requests_session
        if not requests_session:
            log.info('session not founded')
            requests_session = create_requests_session()
        url = 'https://twitter.com/%s/with_replies' % username
        headers = {'Referer': url}
        cookies = {'app_shell_visited': '1'}
        r = requests_session.get(url, timeout=20, cookies=cookies, headers=headers)
        if is_login_page(r):
            log.warning('login page returned')
            requests_session = None
            return
        if r.status_code != 200 or 'data-tweet-id=' not in r.text:
            log.warning('no tweets founded')
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
