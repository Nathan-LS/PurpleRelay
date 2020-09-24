import datetime
import html
from bs4 import BeautifulSoup


class PurpleMessage(object):
    def __init__(self, account, sender, message, conversation, flags):
        self.account = account
        self.sender = sender
        self.message_html = message
        self.message = BeautifulSoup(self.message, 'html.parser').get_text()
        self.conversation = conversation
        self.flags = flags
        self.time = datetime.datetime.utcnow()

    def str_object(self):
        """returns string of the entire object for verbose printing mode"""
        s = "Time: \"{}\"\n".format(self.time)
        s += "Account: \"{}\"\n".format(self.account)
        s += "Sender: \"{}\"\n".format(self.sender)
        s += "Conversation: \"{}\"\n".format(self.conversation)
        s += "Flags: \"{}\"\n".format(self.flags)
        s += "Message: \"{}\"\n".format(self.message)
        return s

    def __str__(self):
        return self.str_object()

    # def __eq__(self, other):
    #     if self.sender == other.sender and self.message == other.message:
    #         if self.core.spam_control:
    #             if (self.time - other.time).total_seconds() <= self.core.spam_decay:
    #                 return True
    #             else:
    #                 return False
    #         else:
    #             return False
    #     else:
    #         return False
    #
    # def get_time(self):
    #     return self.time

    # def filter(self, channel_object):
    #     assert isinstance(channel_object, Channel.Channel)
    #     if not any(self.sender.lower() == i.lower() for i in channel_object.from_filter):
    #         return False
    #     return True
    #
    # async def post(self, channel: discord.TextChannel):
    #     await channel.send(content=self.core.mention, embed=self.embed)
    #     channel_name = "Unknown"
    #     try:
    #         channel_name = "{}".format(str(channel.name))
    #         channel_name += "({})".format(str(channel.guild.name))
    #     except Exception as ex:
    #         print(ex)
    #         traceback.print_exc()
    #     print("Delivered message: '{}' to channel: {}".format(self.message_txt, str(channel_name)))


