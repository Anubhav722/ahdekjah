class BaseMedium(object):
    """
    Medium abstraction used by the chat.
    """

    def __init__(self, callback_url):
        self.callback_url = callback_url

    def send(self, message, to):
        raise NotImplementedError("Implement in subclass")
