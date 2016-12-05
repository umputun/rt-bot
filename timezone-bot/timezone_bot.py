import datetime
import os
import re

import googlemaps
from flask import Flask, json, request
from pytz import timezone
from werkzeug.exceptions import ExpectationFailed

app = Flask(__name__)

app.config.from_envvar('APP_CONFIG')

google_key = os.environ.get('GOOGLE_KEY')

if not google_key:
    raise ValueError('GOOGLE_KEY environment variable is not set')

gmaps_api = googlemaps.Client(google_key, timeout=5)


@app.route('/event', methods=['POST'])
def event():
    """Main event of app"""
    try:
        message = json.loads(request.data).get('text', None)

        if not message:
            return ExpectationFailed()

        # Check if message matches with pattern
        result = re.findall(r'время (в|во) (.*)', message)

        if not result:
            return ExpectationFailed()

        city = result[0][1]

        # Get places by city name (``query`` arg for ``places`` method)
        places = gmaps_api.places(city)

        if places['status'] == 'OK':
            # Get timezone by location
            tz = gmaps_api.timezone(
                places['results'][0]['geometry']['location']
            )
            if tz['status'] == 'OK':
                # Load timezone
                location = timezone(tz['timeZoneId'])
                localized_time = datetime.datetime.now(location)
                return json.dumps({
                    'text': 'Местное время в {city} сейчас {time}'.format(
                        city=places['results'][0]['formatted_address'],
                        time=localized_time.strftime(app.config['TIME_FORMAT'])
                    ),
                    'bot': app.config['BOT_NAME']
                }, ensure_ascii=False), 201, {
                           'Content-Type': 'application/json; charset=utf-8'
                       }
            else:
                return json.dumps({
                    'text': 'Не могу получить данные о часовом поясе',
                    'bot': app.config['BOT_NAME']
                }, ensure_ascii=False), 201, {
                           'Content-Type': 'application/json; charset=utf-8'
                       }
        else:
            return json.dumps({
                'text': 'Не могу найти город по запросу "{city}"'.format(
                    city=city
                ),
                'bot': app.config['BOT_NAME']
            }, ensure_ascii=False), 201, {
                       'Content-Type': 'application/json; charset=utf-8'
                   }

    # JSONDecodeError or have no connection with Google API services
    except Exception:
        return ExpectationFailed()


@app.route('/info')
def info():
    """Get info about bot"""
    return json.dumps({
        'author': 'Anton Prokhorov',
        'info': 'Bot which shows time in location which is passed by a query, '
                'example: on request "время в красноярске" bot have to '
                'respond: "Местное время в Krasnoyarsk, Krasnoyarsk Krai, '
                'Russia сейчас 30.11.2016 23:29:24',
        'commands': ['погода в <city>']
    }, ensure_ascii=False)
