from db.model import Model


class Event(Model):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
