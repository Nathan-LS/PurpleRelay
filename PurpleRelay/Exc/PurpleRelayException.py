class PurpleRelayException(Exception):
    def __init__(self, message="Missing error message"):
        super().__init__(message)


class ChannelNotFound(PurpleRelayException):
    def __init__(self, id):
        super().__init__("Could not load a channel with ID of '{}'. Check your routes.json file".format(str(id)))


class PermissionCannotText(PurpleRelayException):
    def __init__(self, channel_id):
        super().__init__("Unable to send text messages to {} due to a permissions error.".format(str(channel_id)))
