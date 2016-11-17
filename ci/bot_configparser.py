"""
Tools for processing of radio-t bot configs
"""
import re
import os
from functools import lru_cache

import yaml


class BotConfigNotFound(Exception):
    pass


class BotConfigError(Exception):
    pass


BOT_NAME_REGEXP = re.compile(r'[\w\-_]+')


class BotCommand:
    """
    Command for bot in test case
    """
    text = None
    username = None
    display_name = None

    def __init__(self, text: str, username: str, display_name: str):
        self.text = text
        self.username = username
        self.display_name = display_name

    def as_dict(self):
        return {
            'text': self.text,
            'username': self.username,
            'display_name': self.display_name,
        }


class BotResponse:
    """
    Response from bot for command
    """
    OK = 201
    EXPECTATION_FAILED = 417

    def __init__(self, status: int, text: str = None, bot: str = None):
        assert status in (self.OK, self.EXPECTATION_FAILED)
        self.status = status
        self.text = text
        self.bot = bot

    @property
    @lru_cache(maxsize=None)
    def text_regexp(self):
        return re.compile(r'{}'.format(self.text))


class BotTestCase:
    """
    Test case to check bot's correct command processing
    """
    command = None
    response = None

    def __init__(self, command: BotCommand, response: BotResponse):
        self.command = command
        self.response = response


class BotConfig:
    """
    Object representaion of bot-spec.yml file
    """
    DEFAULT_FILENAME = 'bot-spec.yml'
    DEFAULT_USERNAME = 'test_user'
    DEFAULT_DISPLAY_NAME = 'Test User'

    defaults = None
    bot_name = None
    bot_display_name = None
    test_cases = None

    def __init__(
        self, bot_name: str,
        test_cases: list, defaults: dict,
        bot_display_name=None
    ):
        self.bot_name = bot_name
        self.test_cases = test_cases
        self.defaults = defaults
        if bot_display_name is None:
            self.bot_display_name = bot_name
        else:
            self.bot_display_name = bot_display_name

    @classmethod
    def from_dict(cls, data: dict) -> 'BotConfig':
        if not isinstance(data, dict):
            raise BotConfigError('bot config data must be a dict')

        bot_name = cls._parse_bot_name(data)
        bot_display_name = data.get('bot_display_name') or bot_name
        defaults = cls._parse_defaults(data)
        ignored_commands_test_cases = cls._parse_ignored_commands(
            data, defaults
        )
        test_cases = cls._parse_test_cases(data, defaults, bot_display_name)
        return cls(
            bot_name=bot_name,
            test_cases=ignored_commands_test_cases + test_cases,
            defaults=defaults,
            bot_display_name=bot_display_name
        )

    @classmethod
    def from_file(cls, path: str) -> 'BotConfig':
        with open(path) as f:
            data = yaml.load(f)
        return cls.from_dict(data)

    @classmethod
    def from_dir(cls, path: str) -> 'BotConfig':
        config_path = os.path.join(path, cls.DEFAULT_FILENAME)
        if not os.path.exists(config_path):
            raise BotConfigNotFound(
                'No bot config found: {}'.format(config_path)
            )
        return cls.from_file(config_path)

    @classmethod
    def _parse_bot_name(cls, data):
        bot_name = data.get('bot_name')
        if bot_name is None:
            raise BotConfigError('bot_name not found')
        if not BOT_NAME_REGEXP.match(bot_name):
            raise BotConfigError('Invalid bot_name: {}'.format(bot_name))
        return bot_name

    @classmethod
    def _parse_defaults(cls, data):
        defaults = data.get('defaults', {})
        if not isinstance(defaults, dict):
            raise BotConfigError('defaults must be dict')
        defaults.setdefault('username', cls.DEFAULT_USERNAME)
        defaults.setdefault('display_name', cls.DEFAULT_DISPLAY_NAME)
        return defaults

    @classmethod
    def _parse_command(cls, command, defaults):
        allowed_keys = {'text', 'username', 'display_name'}
        if not isinstance(command, (str, dict)):
            raise BotConfigError(
                'command must be string or dict, {} given'.format(
                    command
                )
            )
        if isinstance(command, dict):
            forbidden_keys = set(command.keys()) - allowed_keys
            if forbidden_keys:
                raise BotConfigError(
                    'Not supported command keys: {}'.format(forbidden_keys)
                )
        elif isinstance(command, str):
            command = {'text': command}

        command.setdefault('username', defaults['username'])
        command.setdefault('display_name', defaults['display_name'])
        return BotCommand(
            text=command['text'],
            username=command['username'],
            display_name=command['display_name']
        )

    @classmethod
    def _parse_ignored_commands(cls, data, defaults):
        ignored_commands = data.get('ignored_commands', [])
        if not isinstance(ignored_commands, list):
            raise BotConfigError('ignored_commands must be a list')
        if len(ignored_commands) == 0:
            raise BotConfigError('ignored_commands cannot be empty')
        test_cases = []
        for x, command in enumerate(ignored_commands):
            command = cls._parse_command(command, defaults)
            result = BotResponse(status=BotResponse.EXPECTATION_FAILED)
            test_case = BotTestCase(command=command, response=result)
            test_cases.append(test_case)
        return test_cases

    @classmethod
    def _parse_test_cases(cls, data, defaults, bot_display_name):
        test_cases = data.get('test_cases', [])

        if not isinstance(test_cases, list):
            raise BotConfigError('test_cases must be a list')
        if len(test_cases) == 0:
            raise BotConfigError('test_cases cannot be empty')

        for x, test_case in enumerate(test_cases):
            if not isinstance(test_case, dict):
                raise BotConfigError('test_case must be a dict')
            if set(test_case.keys()) != {'command', 'result'}:
                raise BotConfigError(
                    'test_case must contain only "command" and "result" keys'
                )
            if not isinstance(test_case['result'], str):
                raise BotConfigError('test_case.result must be a string')
            result = BotResponse(
                status=BotResponse.OK,
                bot=bot_display_name,
                text=test_case['result']
            )
            command = cls._parse_command(test_case['command'], defaults)
            test_cases[x] = BotTestCase(command=command, response=result)

        return test_cases
