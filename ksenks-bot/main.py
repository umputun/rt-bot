import asyncio
import hashlib
import json.decoder
import logging
from datetime import datetime
from time import time

import aiohttp
import audio
import pytz
from aiohttp import web
from log_handler import ArrayHandler

SECS_BEFORE_SILENT = 1 * 60
SECS_BEFORE_SLEEP = 5 * 60
DEFAULT_URL = 'http://stream.radio-t.com/'
STREAM_URL = DEFAULT_URL

DEBUG_COMMANDS = True
DEBUG_IGNORE_TIME_UNTIL = 0
DEBUG_RESET_FLAG = False

DEFAULT_PROBABILITY = 0.95
PROBABILITY = DEFAULT_PROBABILITY

last_detects = []
last_ksenks_timestamp = 0
svm_model = None

last_logs = ArrayHandler(max_count=200)
logging.basicConfig(format='%(asctime)-15s %(levelname)-8s %(message)s', level=logging.INFO,
                    datefmt="%Y-%m-%d %H:%M:%S", handlers=[logging.StreamHandler(), last_logs])
log = logging.getLogger()

# disable info logging for http connects
aiohttp_logger = logging.getLogger('aiohttp')
aiohttp_logger.setLevel(logging.WARNING)


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


async def http_info(request):
    data = {'author': 'strayge',
            'info': 'Ksenks-bot выводит время с момента последней реплики Ксюши',
            'commands': ['Ксюша!', 'ksenks!']}
    return web.json_response(data)


async def http_event(request):
    try:
        input_json = await request.json()
    except json.decoder.JSONDecodeError:
        return web.Response(status=417)
    input_text = input_json.get('text')
    # input_username = input_json.get('username')
    # input_displayname = input_json.get('display_name')

    valid_key = False
    if DEBUG_COMMANDS:
        input_key = input_json.get('key')
        if input_key:
            calced_hash = hashlib.new('sha256', str(input_key).encode('utf-8', errors='ignore')).hexdigest()
            predefined_hash = 'a49f6ea4bc8fd77cfa1f02ef1c2e0f6a37970ff964104982b3823e8fc825e971'
            if calced_hash == predefined_hash:
                valid_key = True

    if DEBUG_COMMANDS and valid_key:
        global STREAM_URL, DEBUG_IGNORE_TIME_UNTIL, DEBUG_RESET_FLAG
        global PROBABILITY, last_ksenks_timestamp

        set_away_secs = input_json.get('set_away')
        set_url = input_json.get('set_url')
        get_status = input_json.get('status')
        set_reset = input_json.get('reset')
        set_probability = input_json.get('probability')
        set_ignoretime = input_json.get('ignoretime')
        get_log = input_json.get('showlog')

        if set_away_secs:
            secs_away = int(set_away_secs)
            log.info('Someone changed last_ksenks_timestamp to %i in past' % secs_away)
            if secs_away == 0:
                last_ksenks_timestamp = 0
            else:
                last_ksenks_timestamp = time() - secs_away
            return web.json_response({'text': 'Ок!'})

        if set_url:
            log.info('Someone changed stream_url (and 1 hour of ignoring stream time) to %s' % str(set_url))
            STREAM_URL = str(set_url)
            DEBUG_IGNORE_TIME_UNTIL = time() + 3600
            return web.json_response({'text': 'Ок!'})

        if set_ignoretime:
            log.info('Someone setted to ignoring stream time for 1 hour')
            DEBUG_IGNORE_TIME_UNTIL = time() + 3600
            return web.json_response({'text': 'Ок!'})

        if get_status is not None:
            return web.json_response({'url': STREAM_URL,
                                      'last_timestamp': last_ksenks_timestamp,
                                      'ignore_time_until': DEBUG_IGNORE_TIME_UNTIL,
                                      'reset_flag': DEBUG_RESET_FLAG,
                                      'last_detects': last_detects,
                                      'probability': PROBABILITY})

        if set_reset is not None:
            log.info('Someone resetted settings')
            STREAM_URL = DEFAULT_URL
            DEBUG_IGNORE_TIME_UNTIL = 0
            DEBUG_RESET_FLAG = True
            PROBABILITY = DEFAULT_PROBABILITY
            return web.json_response({'text': 'Ок!'})

        if set_probability:
            if 0.5 < float(set_probability) < 1:
                PROBABILITY = float(set_probability)
                log.info('Someone changed probability %f' % PROBABILITY)
                return web.json_response({'text': 'Ок!'})
            else:
                return web.json_response({'text': 'Fail!'})

        if get_log:
            return web.json_response({'log': last_logs.logs()})

    if not input_text:
        return web.Response(status=417)
    if input_text.strip().lower() not in ['ксюша!', 'ksenks!', '!ксюша', '!ksenks']:
        return web.Response(status=417)

    now = time()
    if not last_ksenks_timestamp or (now - last_ksenks_timestamp) > 24 * 3600:
        text = 'Здесь такая не появлялась :disappointed:'
    else:
        if now - last_ksenks_timestamp < SECS_BEFORE_SILENT:
            text = 'Ксюша с нами! :smile:'
        elif now - last_ksenks_timestamp < SECS_BEFORE_SLEEP:
            minutes = (now - last_ksenks_timestamp) // 60
            text = 'Ксюша молчит уже %i %s...' % (minutes, minutes_word(minutes))
        else:
            minutes = (now - last_ksenks_timestamp) // 60
            if minutes < 60:
                text = 'Ксюша заснула %i %s назад :sleeping:' % (minutes, minutes_word(minutes))
            else:
                hours = minutes // 60
                text = 'Ксюша заснула %i %s назад :sleeping:' % (hours, hours_word(hours))

    output = {'text': text, 'bot': 'ksenks-bot'}
    return web.json_response(data=output, status=201)


async def process_stream(resp):
    tail = b''
    not_processed_frames = []
    log.info('staring processing stream')

    while True:
        if DEBUG_COMMANDS:
            global DEBUG_RESET_FLAG
            if DEBUG_RESET_FLAG:
                log.info('Stream closed by reset command')
                DEBUG_RESET_FLAG = False
                resp.close()
                break

        stream_chunk = await resp.content.read(65536)
        if not stream_chunk:
            log.warn("Can't read audio stream")
            break

        frames, tail = audio.get_frames_from_mp3(stream_chunk, tail)
        if not len(frames):
            log.warn("Can't extract mp3 frames from mp3")
        not_processed_frames += frames

        if len(not_processed_frames) > 100:
            pcm = audio.get_pcm_from_frames(not_processed_frames)
            not_processed_frames = []
            if not pcm:
                log.warn('Decoding error')
                continue

            global svm_model
            probability, svm_model = audio.probe_ksenks_on_pcm(pcm, svm_model)
            if not probability:
                log.error("Can't load SVM model.")
                exit()

            if probability >= PROBABILITY:
                if DEBUG_COMMANDS:
                    global last_detects
                    last_detects.append({'time': round(time()), 'probability': probability})
                    if len(last_detects) > 10:
                        del (last_detects[0])

                log.info('Ksenks detected, prob = %5.2f %%' % (probability * 100))
                global last_ksenks_timestamp
                last_ksenks_timestamp = time()

    log.info('waiting...')
    await asyncio.sleep(30)


async def main_loop(web_app):
    try:
        async with aiohttp.ClientSession() as session:
            while True:
                try:
                    current_date = datetime.now(tz=pytz.timezone('Europe/Moscow'))
                    if (current_date.weekday() == 5 and current_date.hour >= 22) or \
                            (current_date.weekday() == 6 and current_date.hour <= 4) or \
                            (DEBUG_COMMANDS and DEBUG_IGNORE_TIME_UNTIL and time() < DEBUG_IGNORE_TIME_UNTIL):
                        async with session.get(STREAM_URL) as resp:
                            await process_stream(resp)
                    else:
                        log.info('now is not a stream time, waiting...')
                        await asyncio.sleep(30)
                except aiohttp.ClientResponseError:
                    log.warn('Response error, maybe wrong stream url')
    except asyncio.CancelledError:
        pass


async def start_background_tasks(web_app):
    web_app['audio_processor'] = web_app.loop.create_task(main_loop(web_app))


async def cleanup_background_tasks(web_app):
    web_app['audio_processor'].cancel()
    await web_app['audio_processor']


if __name__ == "__main__":
    app = web.Application()
    app.on_startup.append(start_background_tasks)
    app.on_cleanup.append(cleanup_background_tasks)
    app.router.add_get('/info', http_info)
    app.router.add_post('/event', http_event)
    web.run_app(app, port=8080)
