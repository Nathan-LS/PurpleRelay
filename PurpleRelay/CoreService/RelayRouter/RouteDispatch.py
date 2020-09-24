from CoreService.RelayRouter.RouteSource import RouteSource
from typing import List
import asyncio
from CoreService.PurpleAPI.PurpleMessage import PurpleMessage


class RouteDispatch(object):
    def __init__(self, relays: list):
        self.relays: List[RouteSource] = relays
        self.loop = asyncio.get_event_loop()

    def start_relay_dequeue_tasks(self):
        for r in self.relays:
            r.start_dequeue_task()

    def queue_message(self, m: PurpleMessage):
        self.loop.create_task(self.submit_message_to_relays(m))

    async def submit_message_to_relays(self, m: PurpleMessage):
        for r in self.relays:
            await r.queue_message(m)

    def get_all_route_targets(self):
        route_targets = []
        for r in self.relays:
            route_targets += r.get_targets()
        return route_targets
