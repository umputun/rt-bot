#!/usr/bin/env python3

import os
import sys
import argparse
import logging

import requests
from requests.packages.urllib3.exceptions import InsecureRequestWarning

from bot_configparser import BotConfig, BotConfigNotFound, BotConfigError


BASE_URL = os.environ.get('BOT_BASE_URL', 'https://bot.radio-t.com')


logger = logging.getLogger(__file__)


def find_bots(directory) -> dict:
    """
    Returns dict with BotConfig objects
    Dict keys are bot names
    """
    bot_configs = {}
    for dir_ in os.listdir(directory):
        dir_ = os.path.join(os.path.abspath(directory), dir_)
        if os.path.isdir(dir_):
            try:
                config = BotConfig.from_dir(dir_)
                if config.bot_name in bot_configs:
                    raise BotConfigError(
                        "Bot with name {} already exists in {}".format(
                            config.bot_name,
                            dir_
                        )
                    )
                bot_configs[config.bot_name] = config
            except BotConfigNotFound:
                pass
    return bot_configs


def run_bot_testcase(url, test_case) -> bool:
    request_data = test_case.command.as_dict()
    logger.warn('Sending message {} to {}'.format(request_data, url))
    requests.packages.urllib3.disable_warnings(InsecureRequestWarning)
    response = requests.post(url, json=request_data, verify=False,
                             allow_redirects=False)

    if response.status_code != test_case.response.status:
        logger.error(
            '"{}" HTTP status expected, "{}" given'.format(
                test_case.response.status,
                response.status_code,
            )
        )
        return False

    elif test_case.response.status != test_case.response.OK:
        # Content doesn't matter for ignored messages
        return True

    if not response.headers.get('content-type').startswith('application/json'):
        logger.error(
            '"application/json" content-type expected, {} given'.format(
                response.headers.get('content-type'),
            )
        )
        return False

    try:
        response_data = response.json()
    except ValueError:
        logger.error("Invalid JSON returned: {}".format(response_data))
        return False

    if set(response_data.keys()) != {'bot', 'text'}:
        logger.error('Bot response must contain only "bot" and "text" keys')
        logger.error('Keys received: {}'.format(
            ', '.join(k for k in response_data.keys())
        ))
        return False

    result = True
    if response_data.get('bot') != test_case.response.bot:
        logger.error(
            '"{}" bot parameter expected, "{}" given'.format(
                test_case.response.bot,
                response_data.get('bot')
            )
        )
        result = False

    if not test_case.response.text_regexp.match(response_data.get('text', "")):
        logger.error(
            '{} does not match the regexp {}.'
            ' Be careful with escaping of regex\'s special symbols.'.format(
                response_data.get("text"),
                test_case.response.text_regexp,
            )
        )
        result = False

    return result


def test_bot(config: BotConfig) -> bool:
    url = '{}/api/{}/event'.format(BASE_URL, config.bot_name)
    logger.warn("\nTesting bot: {} ({})...\n".format(config.bot_name, url))
    is_success = True
    for test_case in config.test_cases:
        if not run_bot_testcase(url, test_case):
            is_success = False
    if not is_success:
        logger.warn("\nBot test failed: {}...".format(config.bot_name))
    return is_success


def test_bot_list(bot_names: set) -> bool:
    url = '{}/list'.format(BASE_URL)
    logger.warn("\nTesting if bot list is correct (GET {})\n".format(url))
    requests.packages.urllib3.disable_warnings(InsecureRequestWarning)
    response = requests.get(url, verify=False, allow_redirects=False)
    if response.status_code != 200:
        logger.error(
            '"200" HTTP status expected, "{}" given'.format(
                response.status_code,
            )
        )
        return False 

    given_bot_names = set(response.json())
    if given_bot_names == bot_names:
        logger.warn("Bot list is actual.")
        return True

    if given_bot_names < bot_names:
        logger.error("Missing bot names in /list location: {}".format(
            ', '.join(b for b in (bot_names - given_bot_names))
        ))
    else:
        logger.error("Unexpected bot names in /list location: {}".format(
            ', '.join(b for b in (given_bot_names - bot_names))
        ))
    return False


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Test radio-t bots.')
    parser.add_argument('project_dir', type=str)
    args = parser.parse_args()
    bots = find_bots(args.project_dir)
    failed_bots = []

    is_success = True
    for bot in bots.values():
        if not test_bot(bot):
            failed_bots.append(bot)
            is_success = False

    if not is_success:
        logger.error("\nFailed bots: {}".format(
            ', '.join(b.bot_name for b in failed_bots)
        ))

    is_bot_list_ok = test_bot_list(set(bots.keys()))
    if not all([is_success, is_bot_list_ok]):
        sys.exit(1)
