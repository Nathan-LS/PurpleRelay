import re
from re import Pattern
from CoreService.RelayRouter.RouteTarget import RouteTarget
from CoreService.PurpleAPI.PurpleMessage import PurpleMessage
from typing import List
import asyncio
import traceback


class RouteSource(object):
    def __init__(self, order_number: int, name: str, src: str, account: str, sender: str, conversation: str,
                 message: str, flags: str, targets: list):
        self.queue_unprocessed: asyncio.Queue = asyncio.Queue(loop=asyncio.get_event_loop())
        self.task = None
        if name is None:
            self.name: str = "relay_{}".format(order_number)
        elif not isinstance(name, str):
            raise TypeError("Route source 'name' must be of type str. Got '{}'".format(name))
        else:
            self.name: str = name

        if src is None:
            self.src: str = ""
        elif not isinstance(src, str):
            raise TypeError("Route source 'src' must be of type str. Got '{}'".format(src))
        else:
            self.src: str = src

        if not account:
            self.account: Pattern = re.compile(".*", re.DOTALL)
        elif not isinstance(account, str):
            raise TypeError("Route source 'account' must be of type regex str pattern. Got '{}'".format(account))
        else:
            self.account: Pattern = re.compile(account, re.DOTALL)

        if not sender:
            self.sender: Pattern = re.compile(".*", re.DOTALL)
        elif not isinstance(sender, str):
            raise TypeError("Route source 'sender' must be of type regex str pattern. Got '{}'".format(sender))
        else:
            self.sender: Pattern = re.compile(sender, re.DOTALL)

        if not conversation:
            self.conversation: Pattern = re.compile(".*", re.DOTALL)
        elif not isinstance(conversation, str):
            raise TypeError("Route source 'conversation' must be of type regex str pattern. Got '{}'".format(conversation))
        else:
            self.conversation: Pattern = re.compile(conversation, re.DOTALL)

        if not message:
            self.message: Pattern = re.compile(".*", re.DOTALL)
        elif not isinstance(message, str):
            raise TypeError("Route source 'message' must be of type regex str pattern. Got '{}'".format(message))
        else:
            self.message: Pattern = re.compile(message, re.DOTALL)

        if not flags:
            self.flags: Pattern = re.compile(".*", re.DOTALL)
        elif not isinstance(flags, str):
            raise TypeError("Route source 'flags' must be of type regex str pattern. Got '{}'".format(flags))
        else:
            self.flags: Pattern = re.compile(flags, re.DOTALL)

        for r in targets:
            if not isinstance(r, RouteTarget):
                raise TypeError("RouteSource was passed a non-relay object in target list.")
        self.targets: List[RouteTarget] = targets
        print(self.str_config())

    def str_config(self):
        s = "Name: \"{}\"\n".format(self.name)
        s += "SrcType: \"{}\"\n".format(self.src)
        s += "Regex input filter account: \"{}\"\n".format(self.account.pattern)
        s += "Regex input filter sender: \"{}\"\n".format(self.sender.pattern)
        s += "Regex input filter conversation: \"{}\"\n".format(self.conversation.pattern)
        s += "Regex input filter message: \"{}\"\n".format(self.message.pattern)
        s += "Regex input filter flags: \"{}\"\n".format(self.flags.pattern)
        target_list = []
        for r in self.targets:
            target_list.append("{}({})".format(r.channel_id, r.name))
        s += "Relay targets: {}\n".format(str(target_list))
        return s

    def get_targets(self):
        return self.targets

    async def queue_message(self, m: PurpleMessage):
        await self.queue_unprocessed.put(m)

    def start_dequeue_task(self):
        self.task = asyncio.get_event_loop().create_task(self.dequeue_task())

    async def passes_filter(self, purple_message: PurpleMessage):
        return purple_message.passes_filter(account=self.account, sender=self.sender, conversation=self.conversation,
                                            message=self.message, flags=self.flags)

    async def dequeue_task(self):
        while True:
            try:
                m = await self.queue_unprocessed.get()
                if await self.passes_filter(m):
                    for r in self.targets:
                        await r.queue_message(m)
            except Exception as ex:
                print(ex)
                traceback.print_exc()
                await asyncio.sleep(1)
