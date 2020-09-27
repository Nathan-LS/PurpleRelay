import re
import discord
from CoreService.PurpleAPI.PurpleMessage import PurpleMessage
from typing import List
import asyncio
import traceback
import PurpleLogger
from copy import deepcopy
import Exc


class RouteTarget(object):
    def __init__(self, order_number: int, name: str, channel_id: int, title: str, embed: bool, embed_color: int,
                 mention: str, strip_mention: bool, spam_control_seconds: int, timestamp: bool):
        self.queue_unprocessed: asyncio.Queue = asyncio.Queue(loop=asyncio.get_event_loop())
        self.task = None
        self.discord_loaded = False
        self.discord_channel_obj: discord.TextChannel = None
        self.discord_channel_name = ""
        self.discord_guild_name = ""
        self.lg = PurpleLogger.PurpleLogger.get_logger('RelayRoutes', 'relayRoutes.log')
        if name is None:
            self.name: str = "route_{}".format(order_number)
        elif not isinstance(name, str):
            raise TypeError("Route target 'name' must be of type str. Got '{}'".format(name))
        else:
            self.name: str = name

        if not channel_id or not isinstance(channel_id, int):
            raise TypeError("Route target 'channel_id' must be of type int. Got '{}'".format(channel_id))
        else:
            self.channel_id: int = channel_id

        if title is None:
            self.title: str = ""
        elif not isinstance(title, str):
            raise TypeError("Route target 'title' must be of type str. Got '{}'".format(title))
        else:
            self.title: str = title

        if embed is None:
            self.embed: bool = False
        elif not isinstance(embed, bool):
            raise TypeError("Route target 'embed' must be of type bool. Got '{}'".format(embed))
        else:
            self.embed: bool = embed

        if embed_color is None:
            self.embed_color: int = 4659341
        elif not isinstance(embed_color, int):
            raise TypeError("Route target 'embed_color' must be of type int. Got '{}'".format(embed))
        else:
            self.embed_color: int = embed_color

        if mention is None:
            self.mention: str = ""
        elif not isinstance(mention, str):
            raise TypeError("Route target 'mention' must be of type str. Got '{}'".format(mention))
        else:
            self.mention: str = mention

        if strip_mention is None:
            self.strip_mention: bool = False
        elif not isinstance(strip_mention, bool):
            raise TypeError("Route target 'strip_mention' must be of type bool. Got '{}'".format(strip_mention))
        else:
            self.strip_mention: bool = strip_mention

        if spam_control_seconds is None:
            self.spam_control_seconds: int = 0
        elif not isinstance(spam_control_seconds, int):
            raise TypeError("Route target 'spam_control_seconds' must be of type int. Got '{}'"
                            "".format(spam_control_seconds))
        else:
            self.spam_control_seconds: int = spam_control_seconds

        if timestamp is None:
            self.timestamp: bool = True
        elif not isinstance(timestamp, bool):
            raise TypeError("Route target 'timestamp' must be of type bool. Got '{}'".format(spam_control))
        else:
            self.timestamp: bool = timestamp

    async def can_embed(self):
        if not isinstance(self.discord_channel_obj, discord.TextChannel):
            return False
        permissions = self.discord_channel_obj.permissions_for(self.discord_channel_obj.guild.me)
        return permissions.embed_links

    async def can_message(self):
        if not isinstance(self.discord_channel_obj, discord.TextChannel):
            return False
        permissions = self.discord_channel_obj.permissions_for(self.discord_channel_obj.guild.me)
        return permissions.send_messages

    async def init_discord_target(self, discord_client: discord.Client, first_load=False):
        if isinstance(self.task, asyncio.Task):
            return  # already loaded no need to start or check
        c = discord_client.get_channel(self.channel_id)
        if isinstance(c, discord.TextChannel):
            self.discord_channel_obj = c
            self.discord_loaded = True
            self.discord_channel_name = c.name
            self.discord_guild_name = c.guild.name
            self.task = asyncio.get_event_loop().create_task(self.dequeue_task())
        s = "Target Name: {}\nLoaded/Found: {} \nLoaded Channel Name: {}\nLoaded Server Name: {}\nCan Text: {}\n" \
            "Can Embed: {}\n".format(self.name, self.discord_loaded, self.discord_channel_name,
                                     self.discord_guild_name, await self.can_message(), await self.can_embed())
        if first_load:
            print(s)
        else:
            if isinstance(self.task, asyncio.Task):
                print(s)

    async def queue_message(self, m: PurpleMessage):
        copied_message = deepcopy(m)
        await self.queue_unprocessed.put(copied_message)

    async def requeue_failed_message(self, m: PurpleMessage):
        attempts = m.get_send_attempts()
        if attempts == 1:
            await asyncio.sleep(10)
        elif attempts == 2:
            await asyncio.sleep(60)
        elif attempts == 3:
            await asyncio.sleep(300)
        else:
            await asyncio.sleep(900)
        await self.queue_unprocessed.put(m)

    async def dequeue_task(self):
        while True:
            try:
                m: PurpleMessage = await self.queue_unprocessed.get()
                m.increment_attempt_account()
                m_str = m.get_discord_string(title=self.title, timestamp=self.timestamp, mention=self.mention,
                                             strip_mention=self.strip_mention)
                try:
                    if await self.can_message():
                        await self.discord_channel_obj.send(content=m_str)
                        self.lg.debug("Relayed to channel id: {} Message: \"{}\"".format(self.channel_id, m_str))
                    else:
                        raise Exc.PermissionCannotText(self.channel_id)
                except Exception as ex:
                    self.lg.warning("Error when relaying message to channel id: {} - {}".format(self.channel_id, str(ex)))
                    if m.max_retries_exceeded():
                        self.lg.warning("Discarded as max retry attempts exceeded on channel id: {} Message: \"{}\"".format(
                            self.channel_id,  m_str))
                    else:
                        self.lg.warning("Requeue Attempt: {} of {} on channel id: {} "
                                        "Message: \"{}\"".format(m.get_send_attempts(), m.get_max_send_attempts(),
                                                                 self.channel_id, m_str))
                        asyncio.get_event_loop().create_task(self.requeue_failed_message(m))
            except Exception as ex:
                print(ex)
                traceback.print_exc()
                await asyncio.sleep(5)
            finally:
                await asyncio.sleep(1)
