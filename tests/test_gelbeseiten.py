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
from app.gelbeseiten import query_industry_details, query_locations_for_state, query_branches_for_letter, \
    query_industries_list_for_city, download_details_sitemap, copy_sitemaps, take_first_in_next_sitemap

class TestGelbeseiten(unittest.TestCase):

    def setUp(self):
        super().setUp()
        # Clean up database
        #LocationCategory.delete_all()
        #Location.delete_all()
        #Category.delete_all()

    def test_happy_case_details(self):
        # Setup query
        gelebeseiten_id = '14e2e3be-4545-4b21-adda-73705ad630c4'
        details_url = 'https://www.gelbeseiten.de/gsbiz/711bf123-90ea-4927-90d7-8b2cc37fe293'
        query_industry_details(details_link=details_url, gelbeseiten_id=gelebeseiten_id)        

        # Assert that is existing
        Location.find_with_categories(gelbeseiten_id=gelebeseiten_id)
        location = Location.find_by_gelebeseiten_id(gelbeseiten_id=gelebeseiten_id)
        self.assertIsNotNone(location)
        self.assertEqual(location.name, 'Autohaus D\'Onofrio GmbH')
        self.assertEqual(location.website, 'http://www.autohaus-donofrio.de')
        self.assertEqual(location.phone, '(07361) 7 20 07')

    def test_locations_query(self):
        state = 'baden-wuerttemberg'    
        locations = query_locations_for_state(state)

        self.assertEqual(len(locations), 824)

    def test_branches_query(self):
        # First test that the branches query works
        url = 'https://www.gelbeseiten.de/branchenbuch/baden-wuerttemberg/ostalbkreis/aalen/branchen/a'
        branches = query_branches_for_letter(url)

        self.assertEqual(len(branches), 98)

        # Second test check that the list of industries is also working
        query_industries_list_for_city(branches[0])

        locations = Location.find_with_limit(limit=1)
        self.assertEqual(len(locations), 1)
        industry_sectors = Category.find_with_limit(limit=1)
        self.assertEqual(len(industry_sectors), 1)

    def test_robots_xml(self):
        download_details_sitemap()

    def test_copy_sitemaps_folder(self):
        copy_sitemaps()

    def take_first_in_next_sitemap(self):
        entries = take_first_in_next_sitemap(50)
        self.assertEqual(len(entries), 50)
        e = entries[0]
        entries = take_first_in_next_sitemap(50)
        self.assertEqual(len(entries), 50)
        self.assertNotEqual(e, entries[0])

def main():
    # Setup testdatabase
    env = 'test'
    con.set_db_config(db_config[env])

    # Run tests
    unittest.main()

if __name__ == '__main__':
    main()