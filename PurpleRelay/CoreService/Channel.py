import discord
import PurpleRelay.Exc as exc
import asyncio
from .PurpleMessage import PurpleMessage
import traceback


class Channel(object):
    def __init__(self, channel_id, discord_client):
        self.id = channel_id
        self.client: discord.Client = discord_client
        self.channel_object = None
        self.from_filter = []
        self.tmp_from_filter = []
        self.reload_channel()
        self.sent_messages = []
        self.message_deque = asyncio.Queue(loop=self.client.loop)
        self.__deque_task = None

    def deque_done(self):
        try:
            assert isinstance(self.__deque_task, asyncio.Task)
            return self.__deque_task.done()
        except AssertionError:
            return True

    def set_deque_task(self, deq_task: asyncio.Task):
        assert isinstance(deq_task, asyncio.Task)
        self.__deque_task = deq_task

    def reload_channel(self):
        self.channel_object = self.client.get_channel(self.id)
        if self.channel_object is None:
            raise exc.PurpleRelayException.ChannelNotFound(self.id)
        self.tmp_from_filter = []

    def add_from(self, from_txt):
        self.tmp_from_filter.append(str(from_txt))

    def finalize(self):
        self.from_filter = self.tmp_from_filter

    async def filter(self, msg: PurpleMessage):
        if msg in self.sent_messages:
            return
        if not any(msg.sender.lower() == i.lower() for i in self.from_filter):
            return
        await self.message_deque.put(msg)

    async def deque_message(self):
        while True:
            try:
                msg: PurpleMessage = await self.message_deque.get()
                await msg.post(self.channel_object)
                self.sent_messages.append(msg)
            except Exception as ex:
                print(ex)
                traceback.print_exc()
