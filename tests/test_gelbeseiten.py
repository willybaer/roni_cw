import unittest
import pprint
import getopt
import json
import sys
import app.db.connection as con

from app.db.config import db_config
from app.model.city import City
from app.model.location import Location
from app.model.category import Category
from app.model.location_category import LocationCategory

from psycopg2 import IntegrityError, DataError
from app.gelbeseiten import query_industry_details

class TestGelbeseiten(unittest.TestCase):

    def setUp(self):
        super().setUp()
        # Clean up database
        LocationCategory.delete_all()
        Location.delete_all()
        Category.delete_all()

    def test_happy_case_details(self):
        # Setup query
        gelebeseiten_id = '14e2e3be-4545-4b21-adda-73705ad630c4'
        details_url = 'https://www.gelbeseiten.de/gsbiz/14e2e3be-4545-4b21-adda-73705ad630c4'
        query_industry_details(details_link=details_url, gelbeseiten_id=gelebeseiten_id, latitude=43.222409, longitude=131.705801)        

        # Assert that is existing
        Location.find_with_categories(gelbeseiten_id=gelebeseiten_id)
        location = Location.find_by_gelebeseiten_id(gelbeseiten_id=gelebeseiten_id)
        self.assertIsNotNone(location)
        self.assertEqual(location.name, 'Autohaus D\'Onofrio GmbH')
        self.assertEqual(location.website, 'http://www.autohaus-donofrio.de/')
        self.assertEqual(location.phone, '(07361) 7 20 07')


def main():
    # Setup testdatabase
    env = 'test'
    con.set_db_config(db_config[env])

    # Run tests
    unittest.main()

if __name__ == '__main__':
    main()