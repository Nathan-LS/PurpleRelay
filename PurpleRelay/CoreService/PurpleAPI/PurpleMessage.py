import datetime
from bs4 import BeautifulSoup
import re
import hashlib


class PurpleMessage(object):
    def __init__(self, account, sender, message, conversation, flags):
        self.account = str.encode(account, encoding="utf-8", errors="ignore").decode("utf-8", errors="ignore")
        self.sender = str.encode(sender, encoding="utf-8", errors="ignore").decode("utf-8", errors="ignore")
        self.message_raw = message
        self.message: str = self.parse_html(self.message_raw)
        self.conversation = str.encode(conversation, encoding="utf-8", errors="ignore").decode("utf-8", errors="ignore")
        self.flags = str(flags)
        self.time = datetime.datetime.utcnow()
        self.time_str = self.time.strftime("%Y-%m-%d %H:%M")
        self.discord_char_limit = 1999
        self.send_attempts = 0
        self.max_send_attempts = 3
        self.hash_sha512 = hashlib.sha512(self.message.encode(encoding="utf-8", errors="ignore")).hexdigest()
        self.posted_at = None

    def parse_html(self, html_message):
        message_text = html_message.replace("<b>", "**").replace("</b>", "**").replace("< /b>", "**")
        message_text = message_text.replace("<i>", "*").replace("</i>", "*").replace("< /i>", "*")
        soup = BeautifulSoup(message_text, 'html.parser')
        for line_break in soup.find_all("br"):
            line_break.replace_with("\n")
        return str.encode(soup.get_text(), encoding="utf-8", errors="ignore").decode(encoding="utf-8", errors="ignore")

    def str_object(self):
        """returns string of the entire object for verbose printing mode"""
        s = "Time: \"{}\"\n".format(self.time)
        s += "Account: \"{}\"\n".format(self.account)
        s += "Sender: \"{}\"\n".format(self.sender)
        s += "Conversation: \"{}\"\n".format(self.conversation)
        s += "Flags: \"{}\"\n".format(self.flags)
        s += "Message_raw: \"{}\"\n".format(self.message_raw)
        s += "Message: \"{}\"\n".format(self.message.replace("\n", "\\n"))
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
            if timestamp:
                response += "{} - ".format(title)
            else:
                response += "{}".format(title)
        if timestamp:
            response += "{}".format(self.time_str)

        if len(response) != 0:
            response += "\n"
        if self.sender:
            response += "{}: ".format(self.sender)
        if strip_mention:
            message_content = self.message.replace("@here", "").replace("@everyone", "")
        else:
            message_content = self.message
        response += message_content
        return response[:self.discord_char_limit]

    def eq_message_text(self, other):
        return self.hash_sha512 == other.hash_sha512

    def seconds_since_posted(self) -> int:
        """returns the seconds since posted"""
        if isinstance(self.posted_at, datetime.datetime):
            return int((datetime.datetime.utcnow() - self.posted_at).total_seconds())
        else:
            raise TypeError("Message is missing posted_at timestamp as it was not set.")

    def set_posted(self):
        self.posted_at = datetime.datetime.utcnow()
