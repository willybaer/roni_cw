import pprint
import getopt
import json
import sys
import app.db.connection as con
import unittest

from app.db.config import db_config
from app.model.city import City
from psycopg2 import IntegrityError, DataError
from app.austrian_locations import parse_city

class TestAustrianCities(unittest.TestCase):

    def setUp(self):
        super().setUp()
        # Clean up database
        City.delete_all_for_country_code(country_code='AT')


    def test_querying_austrian_cities(self):
        # Query City with link
        parse_city('gemeinden/40101/linz')

        # Assert that the city is exiting
        city = City.find_by_postal_code_and_alpa_2_code(postal_code='4020', alpha_2_code='AT')
        self.assertIsNotNone(city)

def main():
    env = 'test'
    con.set_db_config(db_config[env])

    # Run tests
    unittest.main()

if __name__ == '__main__':
    main()    