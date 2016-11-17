import os
import json.decoder
import asyncio
import aiohttp.web
import re

BOT_NAME = "grabpage-bot"
PAGELR_API_KEY = "okT2EKgWY0eE0KHkW2n4Ag"
PAGELR_API_ENDPOINT = "https://api.pagelr.com/capture/javascript"
PAGELR_URL_TMPL = "https://api.pagelr.com/capture/javascript?uri={url}&b_width=1280&width=240&height=168&maxage=86400&key={key}"

loop = asyncio.get_event_loop()
web_app = aiohttp.web.Application(loop=loop)
client_session = aiohttp.ClientSession(loop=loop)

def make_response(text):

    return aiohttp.web.json_response(
        data={
            "bot": "grabpage-bot",
            "text": text
        },
        status=201
    )


def find_urls(text):
    urls = re.findall('http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\(\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+', text)
    return urls


def make_pagelr_url(url):
    return PAGELR_URL_TMPL.format(url=url, key=PAGELR_API_KEY)


async def event_handle(request: aiohttp.web.Request):

    try:
        request_data = await request.json()
    except json.decoder.JSONDecodeError:
        return aiohttp.web.Response(status=400)

    request_text = request_data.get("text", None)

    if request_text is None:
        return aiohttp.web.Response(status=400)

    urls = find_urls(request_text)

    if len(urls) == 0:
        return aiohttp.web.Response(status=417)

    grabbed_page_url = make_pagelr_url(urls[-1])

    return make_response('\n![{url}]({grabbed_page})'.format(url=urls[-1], grabbed_page=grabbed_page_url))

async def info_handle(request: aiohttp.web.Request):

    return make_response("Ahoy! Grab url and return page snapshot!")


web_app.router.add_post("/event", event_handle)
web_app.router.add_get("/info", info_handle)
aiohttp.web.run_app(web_app, host="0.0.0.0", port=8080)
