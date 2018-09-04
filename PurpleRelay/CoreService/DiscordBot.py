import discord
import os
import asyncio
import traceback


class DiscordBot(discord.Client):
    def __init__(self, service_module):
        super().__init__(loop=service_module.discord_loop)
        self.core: CoreService = service_module
        self.loop.set_default_executor(self.core.threadex)
        self.task_filter = self.loop.create_task(self.message_filter())
        self.task_deque = self.loop.create_task(self.message_deque())

    async def on_ready(self):
        print('-------------------')
        print('Logged in as: {}'.format(str(self.user.name)))
        invite_url = 'https://discordapp.com/api/oauth2/authorize?client_id={}&permissions=0&scope=bot'.format(
            self.user.id)
        print('Invite Link: {}'.format(invite_url))
        print('This bot is a member of:')
        print('Servers: {}'.format(str(len(self.guilds))))
        print('-------------------')

    async def message_filter(self):
        await self.wait_until_ready()
        while True:
            msg = await self.core.messages.async_q.get()
            async for c in self.core.async_all_channels():
                try:
                    await c.filter(msg)
                except Exception as ex:
                    print(ex)
            await asyncio.sleep(.1)

    async def message_deque(self):
        await self.wait_until_ready()
        while True:
            async for c in self.core.async_all_channels():
                try:
                    if c.deque_done():
                        c.set_deque_task(self.loop.create_task(c.deque_message()))
                except Exception as ex:
                    print(ex)
            await asyncio.sleep(.1)

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
            os._exit(1)
        self.run(self.core.bot_token)


from . import CoreService
