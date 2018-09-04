class PurpleRelayException(Exception):
    def __init__(self, message="Missing error message"):
        super().__init__(message)


class ChannelNotFound(PurpleRelayException):
    def __init__(self, id):
        super().__init__("Could not load a channel with ID of '{}'. Check your routes.json file".format(str(id)))
