from gi.repository import GObject
from pydbus import SessionBus
from .PurpleMessage import PurpleMessage
import traceback
import sys
from . import CoreService


class Purple(object):
    def __init__(self, service_module):
        self.core: CoreService = service_module
        bus = SessionBus()
        try:
            self.purple = bus.get("im.pidgin.purple.PurpleService", "/im/pidgin/purple/PurpleObject")
            self.purple.ReceivedImMsg.connect(self.on_message)
            print("Connected to Pidgin")
        except Exception as ex:
            print(ex)
            traceback.print_exc()
            print("Is pidgin/finch running?")
            sys.exit(1)

    def on_message(self, account, sender, message, conversation, flags):
        message_obj = PurpleMessage(self.core, account, sender, message, conversation, flags)
        self.core.messages.sync_q.put_nowait(message_obj)

    def run(self):
        GObject.MainLoop().run()


