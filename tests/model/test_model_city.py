import pprint
import getopt
import json
import sys
import app.db.connection as con
import unittest

from app.db.config import db_config
from app.model.city import City
from psycopg2 import IntegrityError, DataError

class TestModelCity(unittest.TestCase):

    def setUp(self):
        super().setUp()
        City.delete_all()

    def test_happy_case(self):
        # Test - Testing that insert a new city is working correct
        city = City(postal_code='123456', name='Werner', state='Baden-Württemberg', country='Deutschland', website='hallo', alpha_2_code='DE') 
        city.insert()

        # Test that everything was correctly stored
        city_stored = City.find(uuid=city.uuid)
        self.assertEqual(city.postal_code, city_stored.postal_code)
        self.assertEqual(city.name, city_stored.name)
        self.assertEqual(city.state, city_stored.state)
        self.assertEqual(city.country, city_stored.country)
        self.assertEqual(city.website, city_stored.website)

    def test_missing_required_field_name(self):
        # Test - Testing that name is missing, should throw exception
        error = None
        try:
            city = City(postal_code='123456', name=None, state='Baden-Württemberg', country='Deutschland', website='hallo', alpha_2_code='DE') 
            city.insert()
        except IntegrityError as e:
            error = e
        assert error is not None

    def test_update_case(self):
        # Creating new city
        city = City(postal_code='123456', name='Werner', state='Baden-Württemberg', country='Deutschland', website='hallo', alpha_2_code='DE') 
        city.insert()

        # Update city name and save it
        city_stored = City.find(uuid=city.uuid)
        self.assertEqual(city_stored.name, 'Werner')
        city_stored.name = 'Werner2'
        city_stored.postal_code = '12345'
        city_stored.update()

        # Check that name is changed
        city_stored = City.find(uuid=city.uuid)
        self.assertEqual(city_stored.name, 'Werner2')
        self.assertEqual(city_stored.postal_code, ['12345'])

    def test_city_with_same_name_different_postal_code(self):
        # Creating new city - Karlsruhe
        city = City(postal_code='123456', name='Karlsruhe', state='Baden-Württemberg', country='Deutschland', website='hallo', alpha_2_code='DE') 
        city.insert()

        # Creating new city - Karlsruhe with different postal code
        other_city = City(postal_code='123457', name='Karlsruhe', state='Baden-Württemberg', country='Deutschland', website='hallo', alpha_2_code='DE') 
        other_city.insert()

    def test_find_by_postal_code(self):
        # Creating new city - Karlsruhe
        city = City(postal_code='12345', name='Karlsruhe-Süd', state='Baden-Württemberg', country='Deutschland', website='hallo', alpha_2_code='DE') 
        city.insert()

        # Creating new city - Karlsruhe with different postal code
        other_city = City(postal_code=['12345', '12344'], name='Karlsruhe', state='Baden-Württemberg', country='Deutschland', website='hallo', alpha_2_code='DE') 
        other_city.insert()

        all = City.find_by_postal_code_and_alpa_2_code(postal_code='12345', alpha_2_code='DE')
        self.assertEqual(len(all), 2)

    def test_best_match(self):
        # Creating new city - Karlsruhe
        aachen_city = City(postal_code=['52062', '52064', '52066', '52068', '52070', '52072', '52074', '52076', '52078'], name='Aachen', state='Baden-Württemberg', country='Deutschland', website='hallo', alpha_2_code='DE') 
        aachen_city.insert()

        # Creating new city - Karlsruhe with different postal code
        aachen_mitte_city = City(parent_city_uuid=aachen_city.uuid, postal_code=['52062', '52064', '52066', '52068', '52070', '52072', '52074', '52076', '52078'], name='Aachen-Mitte', state='Baden-Württemberg', country='Deutschland', website='hallo', alpha_2_code='DE') 
        aachen_mitte_city.insert()

        aalen_city = City(postal_code=['52062', '52064', '52066', '52068', '52070', '52072', '52074', '52076', '52078'], name='Aalen', state='Baden-Württemberg', country='Deutschland', website='hallo', alpha_2_code='DE') 
        aalen_city.insert()

        aalen_city = City(parent_city_uuid=aalen_city.uuid, postal_code=['52062', '52064', '52066', '52068', '52070', '52072', '52074', '52076', '52078'], name='Höfen', state='Baden-Württemberg', country='Deutschland', website='hallo', alpha_2_code='DE') 
        aalen_city.insert()

        match = City.find_matched_city_by_postal_code_and_name(postal_code='52062', alpha_2_code='DE', city_name='Aachen')
        self.assertEqual(match.name, 'Aachen')

        match = City.find_matched_city_by_postal_code_and_name(postal_code='52062', alpha_2_code='DE', city_name='Aachen-')
        self.assertEqual(match.name, 'Aachen')

        match = City.find_matched_city_by_postal_code_and_name(postal_code='52062', alpha_2_code='DE', city_name='Aachen-Mitte')
        self.assertEqual(match.name, 'Aachen-Mitte')

        match = City.find_matched_city_by_postal_code_and_name(postal_code='52062', alpha_2_code='DE', city_name='Aaalen-Höfen')
        self.assertEqual(match.name, 'Höfen')

        match = City.find_matched_city_by_postal_code_and_name(postal_code='52062', alpha_2_code='DE', city_name='Höfen')
        self.assertEqual(match.name, 'Höfen')

        
        
def main():
    # Setup testdatabase
    env = 'test'
    con.set_db_config(db_config[env])

    # Run tests
    unittest.main()

if __name__ == '__main__':
    main()