from dbus.mainloop.glib import DBusGMainLoop
from gi.repository import GLib
from dbus import SessionBus
import dbus
from CoreService.PurpleAPI.PurpleMessage import PurpleMessage
from CoreService import CoreService
import traceback
import sys
from CoreService.RelayRouter.RouteDispatch import RouteDispatch
import os
import asyncio
import signal
from functools import partial


class Purple(object):
    def __init__(self, route_dispatch, core_service, reconnect_attempts):
        self.route_dispatch: RouteDispatch = route_dispatch
        self.core: CoreService = core_service
        self.loop = None
        self.purple = None
        self.reconnect_attempts = reconnect_attempts

    def purple_init(self, no_sys_exit, suppress_error):
        bus = dbus.SessionBus()
        try:
            purple_bus = bus.get_object("im.pidgin.purple.PurpleService", "/im/pidgin/purple/PurpleObject")
            self.purple = dbus.Interface(purple_bus, dbus_interface="im.pidgin.purple.PurpleInterface")
            self.purple.connect_to_signal(signal_name="ReceivedImMsg", handler_function=self.on_message)
            self.purple.connect_to_signal(signal_name="ReceivedChatMsg", handler_function=self.on_message)
            self.purple.connect_to_signal(signal_name="AccountConnecting", handler_function=self.account_connecting)
            self.purple.connect_to_signal(signal_name="AccountSignedOn", handler_function=self.account_signed_on)
            self.purple.connect_to_signal(signal_name="AccountSignedOff", handler_function=self.account_signed_off)
            self.purple.connect_to_signal(signal_name="AccountConnectionError",
                                          handler_function=self.account_connection_error)
            print("Successfully connected to purple over the session bus")
        except Exception as ex:
            if not suppress_error:
                print(ex)
                traceback.print_exc()
                print("Is pidgin/finch running? Unable to connect over the session bus.")
            if not no_sys_exit:
                sys.exit(1)

    def on_message(self, account, sender, message, conversation, flags):
        account_name = self.purple.PurpleAccountGetUsername(account)
        conv_title = self.purple.PurpleConversationGetTitle(conversation)
        message_obj = PurpleMessage(account_name, sender, message, conv_title, flags)
        self.route_dispatch.queue_message(message_obj)

    def account_connecting(self, account):
        account_name = self.purple.PurpleAccountGetUsername(account)
        print("Account: \"{}\" is connecting...".format(account_name))

    def account_signed_on(self, account):
        account_name = self.purple.PurpleAccountGetUsername(account)
        print("Account: \"{}\" is signed on.".format(account_name))

    def account_signed_off(self, account):
        account_name = self.purple.PurpleAccountGetUsername(account)
        print("Account: \"{}\" is signed off.".format(account_name))

    def account_connection_error(self, account, err, desc):
        account_name = self.purple.PurpleAccountGetUsername(account)
        print("Account: \"{}\" had a connection error. \nError: \"{}\"\nDescription: \"{}\"".format(account_name, err, desc))

    def _run(self, no_sys_exit=False, suppress_error=False):
        print("Attempting to establish connection to pidgin/finch via dbus...")
        DBusGMainLoop(set_as_default=True)
        self.purple_init(no_sys_exit=no_sys_exit, suppress_error=suppress_error)
        self.loop = GLib.MainLoop()
        self.loop.run()

    def _stop(self):
        if isinstance(self.loop, GLib.MainLoop):
            if self.loop.is_running():
                self.loop.quit()

    def _restart(self):
        self._stop()
        self._run(no_sys_exit=True, suppress_error=True)

    def _watcher_test(self):
        try:
            self.purple.PurpleAccountsGetAllActive()
            return True
        except:
            return False

    async def _dbus_watcher(self):
        loop = asyncio.get_event_loop()
        fail_limit = self.reconnect_attempts
        fail_count = 0
        while True:
            if isinstance(self.loop, GLib.MainLoop):
                if not await loop.run_in_executor(None, self._watcher_test):
                    if fail_count == fail_limit and fail_limit != 0:
                        print("Reached the max number of failed DBUS restart attempts... Program exiting...")
                        self._stop()
                        self.core.shutdown_self(1, hard_exit=True)
                        break
                    else:
                        fail_count += 1
                    print("Restarting the DBUS connection to PurpleService... Attempt {} of {}".format(fail_count, fail_limit))
                    loop.run_in_executor(None, self._restart)
                    await asyncio.sleep(15)
                else:
                    fail_count = 0
                    await asyncio.sleep(2)

    async def start(self):
        """"only call once to initially start main thread and watcher"""
        loop = asyncio.get_event_loop()
        loop.run_in_executor(None, partial(self._run, True, False))
        loop.create_task(self._dbus_watcher())




