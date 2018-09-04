import datetime
import discord
import traceback


class PurpleMessage(object):
    def __init__(self, service_mod, account, sender, message, conversation, flags):
        self.core: CoreService = service_mod
        self.account = account
        self.sender = sender
        self.message = message
        self.conversation = conversation
        self.flags = flags
        self.time = datetime.datetime.utcnow()
        self.embed = discord.Embed(timestamp=self.time, color=discord.Color(6429101))
        self.embed.title = ""
        self.message_txt = "{} - {}".format(str(self.sender), str(self.message))
        self.embed.description = self.message_txt
        self.embed.set_footer()

    def __eq__(self, other):
        if self.sender == other.sender and self.message == other.message:
            if self.core.spam_control:
                if (self.time - other.time).total_seconds() <= self.core.spam_decay:
                    return True
                else:
                    return False
            else:
                return False
        else:
            return False

    async def post(self, channel: discord.TextChannel):
        await channel.send(content=self.core.mention, embed=self.embed)
        channel_name = "Unknown"
        try:
            channel_name = "{}".format(str(channel.name))
            channel_name += "({})".format(str(channel.guild.name))
        except Exception as ex:
            print(ex)
            traceback.print_exc()
        print("Delivered message: '{}' to channel: {}".format(self.message_txt, str(channel_name)))


from . import CoreService
