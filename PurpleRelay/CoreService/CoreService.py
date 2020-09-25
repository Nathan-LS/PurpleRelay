from concurrent.futures import ThreadPoolExecutor
import sys
import json
import os
import traceback
import asyncio
from CoreService.RelayRouter.RouteSource import RouteSource
from CoreService.RelayRouter.RouteTarget import RouteTarget
from CoreService.RelayRouter.RouteDispatch import RouteDispatch
from CoreService.DiscordBot.DiscordBot import DiscordBot
from CoreService.PurpleAPI.Purple import Purple
from typing import List
import PurpleLogger
import logging


class CoreService(object):
    def __init__(self):

        self.relays: List[RouteSource] = []
        self.bot_token = ""
        self.max_dbus_reconnect = 5

        self.threadex = ThreadPoolExecutor(max_workers=3)
        self.discord_loop = asyncio.new_event_loop()
        self.discord_loop.set_default_executor(self.threadex)
        asyncio.set_event_loop(self.discord_loop)
        self.read_config()
        self.route_dispatcher = RouteDispatch(self.relays)
        self.route_dispatcher.start_relay_dequeue_tasks()
        self.purple = Purple(route_dispatch=self.route_dispatcher, core_service=self,
                             reconnect_attempts=self.max_dbus_reconnect)
        self.bot = DiscordBot(core_service=self)

        self.discord_loop.create_task(self.purple.start())

        self.bot.start_bot()

    def read_config(self):
        try:
            with open("routes.json", "r") as f:
                d: dict = json.load(f)
                logger: dict = d.get("logger")
                if not isinstance(logger, dict):
                    raise KeyError("Missing logger dictionary in route.json.")
                self.log_loader(logger)
                config: dict = d.get("config")
                if not isinstance(config, dict):
                    raise KeyError("Missing config dictionary in route.json.")
                self.bot_token = config.get("token", "")
                self.max_dbus_reconnect = int(config.get("max_dbus_reconnect", 5))
                routes: list = d.get("routes", [])
                i = 1
                for r in routes:
                    self.route_loader(i, r)
                    i += 1
        except FileNotFoundError:
            print("Missing 'routes.json' file. No message routing can occur. "
                  "Did you forget to copy your 'routes-example.json' file?")
            sys.exit(1)
        except Exception as ex:
            print(ex)
            traceback.print_exc()
            sys.exit(1)

    def route_loader(self, route_number: int, r: dict):
        targets = []
        target_number = 1
        for t in r.get("targets", []):
            new_target = RouteTarget(target_number, t.get("name"), t.get("channel_id"), t.get("title"), t.get("embed"),
                                     t.get("embed_color"), t.get("mention"), t.get("strip_mention"),
                                     t.get("spam_control"), t.get("spam_decay"), t.get("timestamp"))
            targets.append(new_target)
            target_number += 1
        route_source = RouteSource(route_number, r.get("name"), r.get("src"), r.get("account"), r.get("sender"),
                                   r.get("conversation"), r.get("message"), r.get("flags"), targets)
        self.relays.append(route_source)

    def log_loader(self, logger_dict: dict):
        days_delete_after = int(logger_dict.get("days_delete_after", 5))
        if bool(logger_dict.get("log_purple_messages", True)):
            PurpleLogger.PurpleLogger.get_logger('PurpleChat', 'purpleChat.log', level=logging.DEBUG,
                                                 days_delete_after=days_delete_after)
        else:
            PurpleLogger.PurpleLogger.get_logger('PurpleChat', 'purpleChat.log', level=logging.INFO,
                                                 days_delete_after=days_delete_after)
        if bool(logger_dict.get("log_routed_messages", True)):
            PurpleLogger.PurpleLogger.get_logger('RelayRoutes', 'relayRoutes.log', level=logging.DEBUG,
                                                 days_delete_after=days_delete_after)
        else:
            PurpleLogger.PurpleLogger.get_logger('RelayRoutes', 'relayRoutes.log', level=logging.INFO,
                                                 days_delete_after=days_delete_after)

    @classmethod
    def run(cls):
        cls()

    def shutdown_self(self, exit_code=0, hard_exit=False):
        print("Exiting application... Goodbye")
        try:
            self.purple._stop()
        except Exception as ex:
            hard_exit = True
            print(ex)
        self.threadex.shutdown(wait=False)
        if not hard_exit:
            sys.exit(exit_code)
        else:
            os._exit(exit_code)
