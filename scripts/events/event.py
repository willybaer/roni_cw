from db.model import Model


class Event(Model):
    def __init__(self, description=None, **kwargs):
        super().__init__(**kwargs)
        self.description = description
