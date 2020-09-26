import discord
import os
import asyncio
import traceback
from CoreService import CoreService
from CoreService.RelayRouter.RouteDispatch import RouteDispatch
from typing import List


class DiscordBot(discord.Client):
    def __init__(self, core_service):
        self.loop = asyncio.get_event_loop()
        super().__init__(loop=self.loop)
        self.core: CoreService = core_service
        self.route_dispatch: RouteDispatch = self.core.route_dispatcher
        self.loop.create_task(self.init_route_targets())

    async def on_ready(self):
        print('-------------------')
        print('Logged in as: {}'.format(str(self.user.name)))
        invite_url = 'https://discordapp.com/api/oauth2/authorize?client_id={}&permissions=149504&scope=bot'.format(
            self.user.id)
        print('Invite Link: {}'.format(invite_url))
        print('This bot is a member of:')
        print('Servers: {}'.format(str(len(self.guilds))))
        print('-------------------')

    async def init_route_targets(self):
        await self.wait_until_ready()
        print("===========Loading Relay Targets===========")
        first_load = True
        while True:
            relay_targets = self.route_dispatch.get_all_route_targets()
            for r in relay_targets:
                await r.init_discord_target(discord_client=self, first_load=first_load)
            if first_load:
                print("Done loading relay targets...")
            first_load = False
            await asyncio.sleep(60)

    async def on_message(self, message):
        """no commands for now"""
        await self.wait_until_ready()
        try:
            if message.author.id == self.user.id:
                return
            else:
                return
        except Exception as ex:
            print(ex)
            traceback.print_exc()

    def start_bot(self):
        if not self.core.bot_token:
            print("Config bot token missing")
            self.core.shutdown_self(exit_code=1, hard_exit=False)
        try:
            self.run(self.core.bot_token)
        except Exception as ex:
            print(ex)
            traceback.print_exc()
            self.core.shutdown_self(exit_code=1, hard_exit=False)

    async def close(self):
        print("===========Received signal to shut down.===========")
        print("Logging out from Discord...")
        try:
            await super().close()
            self.core.shutdown_self(exit_code=0, hard_exit=False)
        except Exception as ex:
            print(ex)
            self.core.shutdown_self(exit_code=1, hard_exit=True)
