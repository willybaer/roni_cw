from db.model import Model


class Location(Model):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
