import datetime
import html
from bs4 import BeautifulSoup
import re


class PurpleMessage(object):
    def __init__(self, account, sender, message, conversation, flags):
        self.account = str.encode(account, encoding="utf-8", errors="ignore").decode("utf-8", errors="ignore")
        self.sender = str.encode(sender, encoding="utf-8", errors="ignore").decode("utf-8", errors="ignore")
        self.message_html = message
        self.message: str = str.encode(BeautifulSoup(message, 'html.parser').get_text(),
                                       encoding="utf-8", errors="ignore").decode("utf-8", errors="ignore")
        self.conversation = str.encode(conversation, encoding="utf-8", errors="ignore").decode("utf-8", errors="ignore")
        self.flags = str(flags)
        self.time = datetime.datetime.utcnow()
        self.time_str = self.time.strftime("%Y-%m-%d %H:%M")
        self.discord_char_limit = 1999
        self.send_attempts = 0
        self.max_send_attempts = 3

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

    def max_retries_exceeded(self):
        return self.send_attempts >= self.max_send_attempts

    def increment_attempt_account(self):
        self.send_attempts += 1

    def get_send_attempts(self):
        return self.send_attempts

    def get_max_send_attempts(self):
        return self.max_send_attempts

    def passes_filter(self, account: re.Pattern, sender: re.Pattern, conversation: re.Pattern, message: re.Pattern,
                      flags: re.Pattern):
        if account.fullmatch(self.account) is None:
            return False
        if sender.fullmatch(self.sender) is None:
            return False
        if conversation.fullmatch(self.conversation) is None:
            return False
        if message.fullmatch(self.message) is None:
            return False
        if flags.fullmatch(self.flags) is None:
            return False
        return True

    def get_discord_string(self, title: str, timestamp: bool, mention: str, strip_mention: bool):
        response = ""
        if mention:
            response += "{} ".format(mention)
        if title:
            response += "{} ".format(title)
        if timestamp:
            response += "{} - ".format(self.time_str)
        if self.sender:
            response += "{}: ".format(self.sender)
        if strip_mention:
            message_content = self.message.replace("@here", "").replace("@everyone", "")
        else:
            message_content = self.message
        response += message_content
        return response[:self.discord_char_limit]

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


