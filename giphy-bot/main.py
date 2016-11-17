import os
import json.decoder

import asyncio
import aiohttp
import aiohttp.web
import async_timeout

GIPHY_API_KEY = os.environ.get('GIPHY_API_KEY', 'dc6zaTOxFJmzC')
GIPHY_API_ENDPOINT = os.environ.get('GIPHY_API_ENDPOINT', 'http://api.giphy.com/v1/gifs/translate')
GIPHY_API_TIMEOUT = int(os.environ.get('GIPHY_API_TIMEOUT', '3'))

MY_NAME = os.environ.get('MY_NAME', 'Giphy')

loop = asyncio.get_event_loop()
web_app = aiohttp.web.Application(loop=loop)
client_session = aiohttp.ClientSession(loop=loop)


def wrap_response(text):
    return aiohttp.web.json_response(
        data={
            'bot': MY_NAME,
            'text': text,
        },
        status=201,
    )


def giphy_timeout_response():
    return wrap_response('**Giphy** did not responded in {} seconds :('.format(GIPHY_API_TIMEOUT))


def giphy_error_response(giphy_response: aiohttp.ClientResponse):
    return wrap_response('Something went wrong. **Giphy** said: *{} {}*'.format(
        giphy_response.status,
        giphy_response.reason,
    ))


async def giphy_image_response(giphy_response: aiohttp.ClientResponse):
    try:
        giphy_data = await giphy_response.json()
    except json.decoder.JSONDecodeError:
        return wrap_response('Something bad happened :(')

    giphy_data_data = giphy_data.get('data', None)
    # it can be a dict or an empty LIST o_O

    if not giphy_data_data:
        return wrap_response('**Giphy** has not found anything :(')

    giphy_image_url = giphy_data_data. \
        get('images', {}). \
        get('fixed_height_small', {}). \
        get('webp', None)

    if giphy_image_url is None:
        return wrap_response('I cannot understand **Giphy** response :(')

    return wrap_response('![gif]({})'.format(giphy_image_url))


async def call_gyphy(search_string):
    async with client_session.get(GIPHY_API_ENDPOINT, params={
        's': search_string,
        'api_key': GIPHY_API_KEY,
    }) as client_response:
        if client_response.status != 200:
            return giphy_error_response(client_response)
        return await giphy_image_response(client_response)


async def handle(request: aiohttp.web.Request):
    try:
        request_data = await request.json()
    except json.decoder.JSONDecodeError:
        return aiohttp.web.Response(status=400)

    if request_data.get('text', None) is None:
        return aiohttp.web.Response(status=400)

    request_text = request_data.get('text')
    username = request_data.get('username', None)

    if not request_text.lower().startswith('giphy') or username == 'rt-bot':
        return aiohttp.web.Response(status=417)

    search_string = request_text[5:].strip()

    if not search_string:
        return wrap_response('Hey, @{}, your search query is empty!'.format(
            request_data.get('username', '')
        ))

    try:
        with async_timeout.timeout(GIPHY_API_TIMEOUT):
            return await call_gyphy(search_string)
    except asyncio.TimeoutError:
        return giphy_timeout_response()


web_app.router.add_post('/event', handle)

aiohttp.web.run_app(web_app, host='0.0.0.0', port=8080)
