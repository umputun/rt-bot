import asyncio
import hashlib
import json.decoder
import logging
from datetime import datetime, timedelta
from time import time

import pytz
import requests
from aiohttp import web
from disqusapi import DisqusAPI
from log_handler import ArrayHandler

DEBUG_COMMANDS = True
DISQUS_PUBLIC_KEY = 'HW9WFn7kT9Tz0ou9h0wwNElRDNgybM8BONcpHkFDMtBxXFs2cjtOn5pK45xqSEK7'

last_update_timestamp = 0
last_themes_num = 0
last_podcast_num = 0

user_themes_posts = None
user_themes_timestamp = 0

last_logs = ArrayHandler(max_count=200)
logging.basicConfig(format='%(asctime)-15s %(levelname)-8s %(message)s', level=logging.INFO,
                    datefmt="%Y-%m-%d %H:%M:%S", handlers=[logging.StreamHandler(), last_logs])
log = logging.getLogger()

disqus = DisqusAPI(public_key=DISQUS_PUBLIC_KEY)
disqus_thread_id = 0


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


async def http_info(request):
    data = {'author': 'strayge',
            'info': 'Rtnumber-bot выводит номер выпуска, время до эфира, темы слушателей',
            'commands': ['Номер! | Выпуск!', 'Время!', 'Темы слушателей! [:число результатов]']}
    return web.json_response(data)


async def http_event(request):
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
        output = {'text': text, 'bot': 'rtnumber-bot'}
        return web.json_response(data=output, status=201)

    if input_text.strip().lower() in ['номер!', 'выпуск!', '!номер', '!выпуск']:
        if not last_podcast_num:
            return web.Response(status=417)
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
                likes = post['likes']
                msg = post['raw_message'].replace('\n', ' ')
                new_line = '* **[%+i]** %s\\n' % (likes, msg)
                if len(text_out) + len(new_line) >= max_allowed_len:
                    break
                text_out += new_line
            return text_out

        max_len = 0
        if ':' in input_text:
            part1, part2 = input_text.strip().lower().split(':', 1)
            if part1.strip() == command and part2.strip().isdigit():
                max_len = int(part2)

        if not disqus_thread_id:
            return web.Response(status=417)

        global user_themes_posts, user_themes_timestamp

        if user_themes_posts and time() < user_themes_timestamp + 5 * 60:
            output = {'text': gen_user_themes_text(user_themes_posts, max_len), 'bot': 'rtnumber-bot'}
            return web.json_response(data=output, status=201)

        posts = disqus.get('threads.listPosts', forum='radiot', limit=100, thread=disqus_thread_id, method='GET')
        sorted_posts = posts[:]
        sorted_posts.sort(key=lambda x: x['likes'], reverse=True)
        user_themes_posts = sorted_posts
        user_themes_timestamp = time()

        output = {'text': gen_user_themes_text(user_themes_posts, max_len), 'bot': 'rtnumber-bot'}
        return web.json_response(data=output, status=201)

    return web.Response(status=417)


async def main_loop(web_app):
    try:
        while True:
            global last_update_timestamp

            if time() > last_update_timestamp + 24 * 3600:
                global last_podcast_num, last_themes_num
                try:
                    r = requests.get('https://radio-t.com/', timeout=20)
                except:
                    log.warn('Response error')
                    await asyncio.sleep(5 * 60)
                    continue
                r.encoding = 'utf-8'
                try:
                    h1 = r.text.split('"entry-title">')[1:]
                    for i in range(len(h1)):
                        h1[i] = h1[i].split('">', 1)[1].split('</a', 1)[0]
                except:
                    log.warn('Parsing error')
                    await asyncio.sleep(5 * 60)
                    continue

                podcast_num_found = False
                themes_num_found = False
                for title in h1:
                    if not podcast_num_found and 'Радио-Т ' in title:
                        num = title.replace('Радио-Т ', '').strip()
                        if num.isdigit():
                            last_podcast_num = int(num)
                            podcast_num_found = True
                        else:
                            log.warn('Invalid podcast num: "%s"' % num)
                    if not themes_num_found and 'Темы для ' in title:
                        num = title.replace('Темы для ', '').strip()
                        if num.isdigit():
                            last_themes_num = int(num)
                            themes_num_found = True
                        else:
                            log.warn('Invalid themes num: "%s"' % num)

                if podcast_num_found:
                    log.info('Retrieved podcast number, %i' % last_podcast_num)

                if themes_num_found:
                    threads = disqus.get('forums.listThreads', forum='radiot', method='GET')
                    thread_id = None
                    for thread in threads:
                        if 'Темы для %i' % last_themes_num in thread['title']:
                            thread_id = thread['id']
                            break
                    if thread_id:
                        global disqus_thread_id
                        disqus_thread_id = thread_id
                    else:
                        log.warn('Disqus thread for themes not found')

                if podcast_num_found and themes_num_found:
                    last_update_timestamp = time()
            await asyncio.sleep(10)
    except asyncio.CancelledError:
        pass


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
