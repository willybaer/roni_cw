from db.model import Model


class Location(Model):
    def __init__(self,
                 name=None,
                 description=None,
                 street=None,
                 zip=None,
                 city=None,
                 country=None,
                 phone=None,
                 email=None,
                 website=None,
                 **kwargs):
        super().__init__(**kwargs)
        self.email = email
        self.phone = phone
        self.city = city
        self.street = street
        self.description = description
        self.name = name
        self.zip = zip
        self.country = country
        self.website = website
