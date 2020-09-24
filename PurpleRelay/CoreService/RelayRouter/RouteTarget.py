import re


class RouteTarget(object):
    def __init__(self, order_number: int, name: str, channel_id: int, title: str, embed: bool, embed_color: int,
                 mention: str, strip_mention: bool, spam_control: bool, spam_decay: int):
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

        if spam_control is None:
            self.spam_control: bool = False
        elif not isinstance(spam_control, bool):
            raise TypeError("Route target 'spam_control' must be of type bool. Got '{}'".format(spam_control))
        else:
            self.spam_control: bool = spam_control

        if spam_decay is None:
            self.spam_decay: int = 0
        elif not isinstance(spam_decay, int):
            raise TypeError("Route target 'spam_decay' must be of type int. Got '{}'".format(spam_decay))
        else:
            self.spam_decay: int = spam_decay
