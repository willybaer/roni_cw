import pprint
import getopt
import json
import sys
import app.db.connection as con
import unittest

from app.db.config import db_config
from app.model.city import City
from psycopg2 import IntegrityError, DataError
from app.swiss_locations import parse_city

class TestSwissCities(unittest.TestCase):

    def setUp(self):
        super().setUp()
        # Clean up database
        City.delete_all_for_country_code(country_code='CH')

    def test_happy_create_swiss_city_with_multiple_postal_code(self):
        details_url = 'https://de.wikipedia.org/wiki/Glarus_S%C3%BCd'
        parse_city(details_url, name='Glarus Süd')

        # Check that 13 entries are existing for each postal code
        city = City.find_by_postal_code_and_alpa_2_code('8774', 'CH')
        self.assertIsNotNone(city)

    def test_happy_create_swiss_city_also_sepcial_case(self):
        # Also a special case
        details_url = 'https://de.wikipedia.org/wiki/Aadorf'
        parse_city(details_url, name='Aadorf')

        city = City.find_by_postal_code_and_alpa_2_code('8355', 'CH')
        self.assertIsNotNone(city)    

def main():
    env = 'test'
    con.set_db_config(db_config[env])

    # Run tests
    unittest.main()

if __name__ == '__main__':
    main()    