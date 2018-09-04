from concurrent.futures import ThreadPoolExecutor
from .Purple import Purple
from .DiscordBot import DiscordBot
from .Channel import Channel
import PurpleRelay.Exc as exc
import configparser
import sys
import janus
import asyncio
import json
import time
import traceback


class CoreService(object):
    def __init__(self):
        self.channels = {}
        self.mention = None
        self.bot_token = None
        self.spam_control = None
        self.spam_decay = None
        self.read_config()
        self.threadex = ThreadPoolExecutor(max_workers=3)
        self.purple = Purple(self)

        self.discord_loop = asyncio.new_event_loop()
        self.messages = janus.Queue(loop=self.discord_loop)
        self.bot = DiscordBot(self)
        self.task_purple = self.threadex.submit(self.purple.run)
        self.bot.start_bot()

    def read_config(self):
        config_file = configparser.ConfigParser()
        try:
            with open("config.ini", 'r'):
                pass
            config_file.read("config.ini")
            self.mention = config_file.get("relay", "mention", fallback="")
            self.bot_token = config_file.get("discord", "token", fallback=None)
            self.spam_control = config_file.getboolean("relay", "spam_control", fallback=False)
            self.spam_decay = config_file.getint("relay", "spam_decay", fallback=30)
        except FileExistsError:
            print("Missing config.ini file.")
            sys.exit(1)

    def load_channel(self, id):
        try:
            result: Channel = self.channels.get(id)
            if result is None:
                try:
                    c = Channel(id, self.bot)
                    self.channels[id] = c
                    print("Loaded channel with ID of: {}".format(str(id)))
                except exc.PurpleRelayException.ChannelNotFound as ex:
                    print(ex)
            else:
                try:
                    result.reload_channel()
                except exc.PurpleRelayException.ChannelNotFound as ex:
                    print(ex)
                    self.remove_channel(id)
        except Exception as ex:
            print(ex)
            traceback.print_exc()

    def remove_channel(self, id):
        try:
            del self.channels[id]
            print("Removed channel with ID of {}.".format(str(id)))
        except Exception as ex:
            print(ex)

    async def async_all_channels(self):
        for c in self.get_channels():
            yield c

    def get_channels(self):
        return self.channels.values()

    def get_channel_ids(self):
        return self.channels.keys()

    def get_channel(self, id):
        return self.channels.get(id)

    def read_json(self):
        while True:
            all_ids = []
            try:
                with open("routes.json", "r") as f:
                    data: dict = json.load(f)
                    r_msg = data.get('master').get('messages')
                    for items in r_msg.values():
                        all_ids += [id for id in items]
                    all_ids = set(all_ids)
                    for id in all_ids:
                        self.load_channel(id)
                    for id in list(set(self.get_channel_ids()) - all_ids):
                        self.remove_channel(id)
                    for from_ad, channel_ids in r_msg.items():
                        for id in channel_ids:
                            ch_obj: Channel = self.get_channel(id)
                            if ch_obj is not None:
                                ch_obj.add_from(from_ad)
                    for c in self.get_channels():
                        c.finalize()
            except FileNotFoundError:
                print(
                    "Missing 'routes.json' file. No message routing can occur. Did you forget to copy your 'routes-example.json' file?")
            except Exception as ex:
                print(ex)
                traceback.print_exc()
            time.sleep(30)

    @classmethod
    def run(cls):
        cls()
