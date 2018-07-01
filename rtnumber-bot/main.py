import asyncio
import hashlib
import json.decoder
import logging
import re
import traceback
from datetime import datetime, timedelta
from time import time

import pytz
import requests
from aiohttp import web
from log_handler import ArrayHandler

DEBUG_COMMANDS = True

last_update_timestamp = 0

podcast_urls = dict()
themes_urls = dict()

last_response = None

user_themes_comments = None
user_themes_timestamp = 0

last_logs = ArrayHandler(max_count=200)
logging.basicConfig(format='%(asctime)-15s %(levelname)-8s %(message)s', level=logging.INFO,
                    datefmt="%Y-%m-%d %H:%M:%S", handlers=[logging.StreamHandler(), last_logs])
log = logging.getLogger()


def minutes_word(minutes):
    word = 'минут'
    if 11 <= minutes <= 14:
        pass
    elif minutes % 10 == 1:
        word += 'у'
    elif minutes % 10 in [2, 3, 4]:
        word += 'ы'
    return word


def hours_word(hours):
    word = 'часов'
    if 11 <= hours <= 14:
        pass
    elif hours % 10 == 1:
        word = 'час'
    elif hours % 10 in [2, 3, 4]:
        word = 'часа'
    return word


def hours_minutes_text(minutes, hours=0):
    if hours == 0:
        if minutes >= 60:
            hours = minutes // 60
            minutes -= (minutes // 60) * 60
    h_word = hours_word(hours)
    m_word = minutes_word(minutes)
    return '%i %s %i %s' % (hours, h_word, minutes, m_word)


async def http_info(_):
    data = {'author': 'strayge',
            'info': 'Rtnumber-bot выводит номер выпуска, время до эфира, темы слушателей',
            'commands': ['Номер! | Выпуск!', 'Время!', 'Темы слушателей! [:число результатов]']}
    return web.json_response(data)


async def http_event(request):
    global last_response
    try:
        input_json = await request.json()
    except json.decoder.JSONDecodeError:
        return web.Response(status=417)

    input_text = input_json.get('text')

    valid_key = False
    if DEBUG_COMMANDS:
        input_key = input_json.get('key')
        if input_key:
            calced_hash = hashlib.new('sha256', str(input_key).encode('utf-8', errors='ignore')).hexdigest()
            predefined_hash = '3914b7f17b84ed68dc579b8308e2970950e29c257520975faee2f701f13311c7'
            if calced_hash == predefined_hash:
                valid_key = True

    delta_hours = None
    if DEBUG_COMMANDS and valid_key:
        delta_hours = input_json.get('delta')
        get_log = input_json.get('showlog')
        if get_log:
            return web.json_response({'log': last_logs.logs()})

    if not input_text:
        return web.Response(status=417)

    dt = datetime.now(tz=pytz.timezone('Europe/Moscow'))
    if delta_hours:
        dt = dt + timedelta(hours=int(delta_hours))

    if input_text.strip().lower() in ['время!', '!время']:
        weekday = dt.weekday()
        if last_response is None or (datetime.now() - last_response).seconds > 45:
            if weekday == 5:
                if dt.hour < 23:
                    min_until_rt = 23 * 60 - (dt.hour * 60 + dt.minute)
                    text = 'Трансляция должна начаться через %s' % hours_minutes_text(min_until_rt)
                else:
                    min_after_rt = (dt.hour - 23) * 60 + dt.minute
                    text = 'Трансляция должна идти уже %s' % hours_minutes_text(min_after_rt)
            elif weekday == 6:
                if dt.hour <= 2:
                    min_after_rt = (dt.hour + 1) * 60 + dt.minute
                    text = 'Трансляция должна идти уже %s' % hours_minutes_text(min_after_rt)
                else:
                    text = 'Трансляция должна была уже закончиться'
            else:
                text = 'Сегодня никакого Радио-Т'
        else:
            text = 'Чуть меньше, чем когда спрашивали в прошлый раз.'
        output = {'text': text, 'bot': 'rtnumber-bot'}
        last_response = datetime.now()
        return web.json_response(data=output, status=201)

    if input_text.strip().lower() in ['номер!', 'выпуск!', '!номер', '!выпуск']:
        if not podcast_urls:
            return web.Response(status=417)
        last_podcast_num = int(max(podcast_urls.keys()))
        weekday = dt.weekday()
        if weekday == 5:
            delta_days_num = 0
        elif weekday == 6:
            delta_days_num = -1
        else:
            delta_days_num = 5 - weekday
        day_num = (dt + timedelta(days=delta_days_num)).day
        if day_num <= 7:
            text = 'Выпуск # %i, гиковский' % (last_podcast_num + 1)
        else:
            text = 'Выпуск # %i, не гиковский' % (last_podcast_num + 1)
        output = {'text': text, 'bot': 'rtnumber-bot'}
        return web.json_response(data=output, status=201)

    def is_one_of_cmds_in_input(cmds, input):
        for cmd in cmds:
            if cmd in input.strip().lower():
                return cmd

    command = is_one_of_cmds_in_input(['темы слушателей!', '!темы слушателей',
                                       'темы пользователей!', '!темы пользователей'], input_text)
    if command:
        def gen_user_themes_text(posts_list, max_posts=0):
            max_allowed_len = 4000
            text_out = '**Темы слушателей:**\\n\\n'
            if max_posts <= 0:
                max_posts = len(posts_list)
            for post in posts_list[:max_posts]:
                likes = post['comment']['score']
                msg = post['comment']['orig'].replace('\n', ' ')
                while '  ' in msg:
                    msg = msg.replace('  ', ' ')
                new_line = '* **[%+i]** %s\\n' % (likes, msg)
                if len(text_out) + len(new_line) >= max_allowed_len:
                    break
                text_out += new_line
            return text_out

        max_len = 5
        if ':' in input_text:
            part1, part2 = input_text.strip().lower().split(':', 1)
            if part1.strip() == command and part2.strip().isdigit():
                max_len = int(part2)

        if not themes_urls:
            return web.Response(status=417)

        global user_themes_comments, user_themes_timestamp

        if user_themes_comments and time() < user_themes_timestamp + 5 * 60:
            output = {'text': gen_user_themes_text(user_themes_comments, max_len), 'bot': 'rtnumber-bot'}
            return web.json_response(data=output, status=201)

        last_themes_num = max(themes_urls.keys())
        url = 'https://remark42.radio-t.com/api/v1/find?site=radiot&url={}&sort=-score&format=tree'.format(
            themes_urls[last_themes_num])
        try:
            r = requests.get(url, timeout=20)
            user_themes_comments = r.json()['comments']
            user_themes_timestamp = time()
        except:
            log.warning('Parsing error in fetching comments')
            return web.Response(status=417)

        output = {'text': gen_user_themes_text(user_themes_comments, max_len), 'bot': 'rtnumber-bot'}
        return web.json_response(data=output, status=201)

    return web.Response(status=417)


async def main_loop(_):
    while True:
        try:
            global last_update_timestamp

            if time() > last_update_timestamp + 24 * 3600:
                global podcast_urls, themes_urls
                try:
                    r = requests.get('https://remark42.radio-t.com/api/v1/list?site=radiot&limit=10&skip=0', timeout=20)
                except:
                    log.warning('Response error')
                    await asyncio.sleep(5 * 60)
                    continue
                r.encoding = 'utf-8'
                try:
                    podcast_urls = dict()
                    themes_urls = dict()
                    for x in r.json():
                        topic_url = x['url']
                        num = re.findall('podcast-(\d+)', topic_url)
                        if num:
                            podcast_urls[num[0]] = topic_url
                            continue
                        num = re.findall('prep-(\d+)', topic_url)
                        if num:
                            themes_urls[num[0]] = topic_url
                    log.info('Retrieved podcast numbers, {}'.format(podcast_urls))
                    log.info('Retrieved themes numbers, {}'.format(themes_urls))
                except:
                    log.warning('Parsing error in list of topics')
                    await asyncio.sleep(5 * 60)
                    continue

                if podcast_urls and themes_urls:
                    last_update_timestamp = time()

            await asyncio.sleep(10)
        except asyncio.CancelledError:
            pass
        except:
            log.warning('Unhandled exception in main_loop')
            print(traceback.format_exc())
            await asyncio.sleep(1)


async def start_background_tasks(web_app):
    web_app['loop'] = web_app.loop.create_task(main_loop(web_app))


async def cleanup_background_tasks(web_app):
    web_app['loop'].cancel()
    await web_app['loop']


if __name__ == "__main__":
    app = web.Application()
    app.on_startup.append(start_background_tasks)
    app.on_cleanup.append(cleanup_background_tasks)
    app.router.add_get('/info', http_info)
    app.router.add_post('/event', http_event)
    web.run_app(app, port=8080)
