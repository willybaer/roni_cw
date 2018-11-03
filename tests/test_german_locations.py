import pprint
import getopt
import json
import sys
import app.db.connection as con

from app.db.config import db_config
from app.model.city import City
from psycopg2 import IntegrityError, DataError
from app.german_locations import parse_content

def before():
    # Before clean up all entries    
    City.delete_all()

def before_each():
    # Before clean up all entries    
    City.delete_all()

def testing_city_pages_with_multiple_postal_codes():
    # Example details page where a city has more than one postal code
    details_url = '81404-gemeinde-aalen.html'
    parse_content(details_url)

    # Find all cities
    cities = City.find_all()
    assert len(cities) == 3

def after():
    #before_each()
    testing_city_pages_with_multiple_postal_codes()

def main():
    env = 'test'
    con.set_db_config(db_config[env])

    #before()
    after()

if __name__ == '__main__':
    main()    