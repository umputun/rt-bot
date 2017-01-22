import unittest
from unittest.mock import patch
from collections import OrderedDict

from mockredis import mock_strict_redis_client

from karma import (
    Message, KarmaCmd, KarmaApp,
    KARMA_INCR, KARMA_DECR, KARMA_STAT, KARMA_TOP
)


class MessageTestCase(unittest.TestCase):

    def test_init(self):
        message = Message("joe", "Hello!", "Joe")
        self.assertEqual(message.username, "joe")
        self.assertEqual(message.text, "Hello!")
        self.assertEqual(message.display_name, "Joe")

    def test_from_string(self):
        with self.assertRaises(ValueError):
            Message.from_string("invalid json")
        with self.assertRaises(ValueError):
            Message.from_string(
                '''{
                    "invalid_key": "value",
                    "username": "joe",
                    "text": "Hello!",
                    "display_name": "Joe",
                }'''
            )
        message = Message.from_string(
            '''{
                "username": "joe",
                "text": "Hello!",
                "display_name": "Joe"
            }'''
        )
        self.assertEqual(message.username, "joe")
        self.assertEqual(message.text, "Hello!")
        self.assertEqual(message.display_name, "Joe")


class KarmaCmdTestCase(unittest.TestCase):

    def test_init(self):
        cmd = KarmaCmd(KARMA_INCR, "joe")
        self.assertEqual(cmd.username, "joe")
        self.assertEqual(cmd.type, KARMA_INCR)

        cmd = KarmaCmd(KARMA_DECR, "joe2")
        self.assertEqual(cmd.type, KARMA_DECR)
        self.assertEqual(cmd.username, "joe2")

    def test_from_invalid_message(self):
        message = Message(username="joe", text="hello",
                          display_name="Joe")
        self.assertIsNone(KarmaCmd.from_message(message))

    def test_from_incr_message(self):

        valid_messages = [
            'foobar++', '@foobar++', '@foobar ++', '@foobar +1', '@foobar+1',
            '@foobar, +1', '@foobar, + 1 ',
        ]

        for msg in valid_messages:
            message = Message(username="joe", text=msg,
                              display_name="Joe")
            cmd = KarmaCmd.from_message(message)
            self.assertEqual(cmd.type, KARMA_INCR)
            self.assertEqual(cmd.username, "foobar")

        message = Message(username="joe", text='foo__bar++',
                          display_name="Joe")
        cmd = KarmaCmd.from_message(message)
        self.assertEqual(cmd.type, KARMA_INCR)
        self.assertEqual(cmd.username, "foo__bar")

        message = Message(username="joe", text='foo-bar++',
                          display_name="Joe")
        cmd = KarmaCmd.from_message(message)
        self.assertEqual(cmd.type, KARMA_INCR)
        self.assertEqual(cmd.username, "foo-bar")

        message = Message(username="joe", text="foo Bar++",
                          display_name="Joe")
        self.assertIsNone(KarmaCmd.from_message(message))

    def test_from_decr_message(self):
        valid_messages = [
            'foobar--', '@foobar--', '@foobar --', '@foobar -1', '@foobar-1',
            '@foobar, -1', '@foobar, - 1 ',
        ]

        for msg in valid_messages:
            message = Message(username="joe", text=msg,
                              display_name="Joe")
            cmd = KarmaCmd.from_message(message)
            self.assertEqual(cmd.type, KARMA_DECR)
            self.assertEqual(cmd.username, "foobar")

        message = Message(username="joe", text='foo__bar--',
                          display_name="Joe")
        cmd = KarmaCmd.from_message(message)
        self.assertEqual(cmd.type, KARMA_DECR)
        self.assertEqual(cmd.username, "foo__bar")

        message = Message(username="joe", text='foo-bar--',
                          display_name="Joe")
        cmd = KarmaCmd.from_message(message)
        self.assertEqual(cmd.type, KARMA_DECR)
        self.assertEqual(cmd.username, "foo-bar")

        message = Message(username="joe", text="foo Bar--",
                          display_name="Joe")
        self.assertIsNone(KarmaCmd.from_message(message))

    def test_from_stat_message(self):
        message = Message(username="joe", text="/karma",
                          display_name="Joe")
        cmd = KarmaCmd.from_message(message)
        self.assertEqual(cmd.type, KARMA_STAT)
        self.assertEqual(cmd.username, "joe")

        message = Message(username="joe", text="/KARMA ",
                          display_name="Joe")
        cmd = KarmaCmd.from_message(message)
        self.assertEqual(cmd.type, KARMA_STAT)
        self.assertEqual(cmd.username, "joe")

        message = Message(username="joe", text="Моя карма",
                          display_name="Joe")
        cmd = KarmaCmd.from_message(message)
        self.assertEqual(cmd.type, KARMA_STAT)
        self.assertEqual(cmd.username, "joe")

        message = Message(username="joe", text="/karma foobar",
                          display_name="Joe")
        cmd = KarmaCmd.from_message(message)
        self.assertEqual(cmd.type, KARMA_STAT)
        self.assertEqual(cmd.username, "foobar")

        message = Message(username="joe", text="/karma foobar  ",
                          display_name="Joe")
        self.assertEqual(cmd.type, KARMA_STAT)
        self.assertEqual(cmd.username, "foobar")

    def test_from_top(self):
        message = Message(username="joe", text="/karma-top",
                          display_name="Joe")
        cmd = KarmaCmd.from_message(message)
        self.assertEqual(cmd.type, KARMA_TOP)
        self.assertEqual(cmd.username, "joe")
        self.assertEqual(cmd.args, (10,))

        message = Message(username="joe2", text="/karma-top 100",
                          display_name="Joe")
        cmd = KarmaCmd.from_message(message)
        self.assertEqual(cmd.type, KARMA_TOP)
        self.assertEqual(cmd.username, "joe2")
        self.assertEqual(cmd.args, (100,))


class KarmaAppTestCase(unittest.TestCase):

    @patch('karma.redis.StrictRedis', mock_strict_redis_client)
    def test_get(self):
        app = KarmaApp({"joe": 5, "bob": 10})
        self.assertEqual(app.get("joe"), 5)
        self.assertEqual(app.get("bob"), 10)
        self.assertEqual(app.get("joe2"), 0)
        self.assertEqual(app.get("joe3"), 0)

    @patch('karma.redis.StrictRedis', mock_strict_redis_client)
    def test_incr(self):
        app = KarmaApp()
        self.assertEqual(app.get("joe"), 0)
        self.assertEqual(app.get("joe2"), 0)
        app.incr("joe")
        app.incr("joe")
        self.assertEqual(app.get("joe"), 2)
        self.assertEqual(app.get("joe2"), 0)
        app.incr("joe2")
        self.assertEqual(app.get("joe2"), 1)
        app.incr("joe2")
        app.incr("joe2")
        app.incr("joe2")
        self.assertEqual(app.get("joe2"), 4)

    @patch('karma.redis.StrictRedis', mock_strict_redis_client)
    def test_decr(self):
        app = KarmaApp()
        self.assertEqual(app.get("joe"), 0)
        app.decr("joe")
        app.decr("joe")
        self.assertEqual(app.get("joe"), -2)
        app.decr("joe")
        self.assertEqual(app.get("joe"), -3)
        self.assertEqual(app.get("joe2"), 0)

    @patch('karma.redis.StrictRedis', mock_strict_redis_client)
    def test_top(self):
        app = KarmaApp({"joe": 5, "bob": 10, "alice": 7})
        self.assertEqual(
            app.top(10),
            OrderedDict([
                ['bob', 10],
                ['alice', 7],
                ['joe', 5],
            ])
        )
        self.assertEqual(
            app.top(2),
            OrderedDict([
                ['bob', 10],
                ['alice', 7],
            ])
        )
        self.assertEqual(
            app.top(1),
            OrderedDict([
                ['bob', 10],
            ])
        )
