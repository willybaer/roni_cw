import unittest
import pprint
import getopt
import json
import sys
import app.db.connection as con

from app.db.config import db_config
from app.model.location import Location
from app.model.category import Category
from app.model.city import City
from app.model.location_category import LocationCategory

from psycopg2 import IntegrityError, DataError

class TestModelLocation(unittest.TestCase):

    def setUp(self):
        super().setUp()
        # Clean up database
        LocationCategory.delete_all()
        Location.delete_all()
        Category.delete_all()

    def test_happy_find_location_with_categories(self):
        # Create Location and Category
        city = City(postal_code='code', name='name_de', state='state_de', country='Deutschland', alpha_2_code='DE')
        city.insert()

        category = Category(name_de='category_de')
        category.insert()

        second_category = Category(name_de='second_category_de')
        second_category.insert()

        gelbeseiten_id = '14e2e3be-4545-4b21-adda-73705ad630c4'
        location = Location(city.uuid, name='name_de', street='street', phone='phone', gelbeseiten_id=gelbeseiten_id)
        location.insert()

        LocationCategory(location_uuid=location.uuid, category_uuid=category.uuid).insert()
        LocationCategory(location_uuid=location.uuid, category_uuid=second_category.uuid).insert()

        found_location = Location.find_with_categories(gelbeseiten_id=gelbeseiten_id)        
        self.assertIsNotNone(found_location)
        self.assertIsNotNone(found_location.categories)

def main():
    # Setup testdatabase
    env = 'test'
    con.set_db_config(db_config[env])

    # Run tests
    unittest.main()

if __name__ == '__main__':
    main()