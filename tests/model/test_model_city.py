import pprint
import getopt
import json
import sys
import app.db.connection as con

from app.db.config import db_config
from app.model.city import City
from psycopg2 import IntegrityError, DataError

def before():
    # Before clean up all entries    
    City.delete_all()

def before_each():
    # Before clean up all entries    
    City.delete_all()

def happy_case():
    # Test - Testing that insert a new city is working correct
    city = City(postal_code='123456', name='Werner', state='Baden-Württemberg', country='Deutschland', website='hallo', alpha_2_code='DE') 
    city.insert()

    # Test that everything was correctly stored
    city_stored = City.find(uuid=city.uuid)
    assert city.postal_code == city_stored.postal_code
    assert city.name == city_stored.name
    assert city.state == city_stored.state
    assert city.country == city_stored.country
    assert city.website == city_stored.website

def missing_required_field_name():
    # Test - Testing that name is missing, should throw exception
    error = None
    try:
        city = City(postal_code='123456', name=None, state='Baden-Württemberg', country='Deutschland', website='hallo', alpha_2_code='DE') 
        city.insert()
    except IntegrityError as e:
        error = e
    assert error is not None

def update_case():
    # Creating new city
    city = City(postal_code='123456', name='Werner', state='Baden-Württemberg', country='Deutschland', website='hallo', alpha_2_code='DE') 
    city.insert()

    # Update city name and save it
    city_stored = City.find(uuid=city.uuid)
    assert city_stored.name == 'Werner'
    city_stored.name = 'Werner2'
    city_stored.update()

    # Check that name is changed
    city_stored = City.find(uuid=city.uuid)
    assert city_stored.name == 'Werner2'

def city_with_same_name_different_postal_code():
    # Creating new city - Karlsruhe
    city = City(postal_code='123456', name='Karlsruhe', state='Baden-Württemberg', country='Deutschland', website='hallo', alpha_2_code='DE') 
    city.insert()

    # Creating new city - Karlsruhe with different postal code
    other_city = City(postal_code='123457', name='Karlsruhe', state='Baden-Württemberg', country='Deutschland', website='hallo', alpha_2_code='DE') 
    other_city.insert()

def after():
    before_each()
    happy_case()
    before_each()
    missing_required_field_name()
    before_each()
    update_case()
    before_each()
    city_with_same_name_different_postal_code()

def main():
    argv = sys.argv
    try:
        opts, args = getopt.getopt(argv[1:], 'd:', ['db='])
    except getopt.GetoptError:
        sys.exit(2)

    # Setup DB environment
    env = list(filter(lambda x: x[0] in ('-d', '--db'), opts))
    if env and len(env) > 0:
        env = env[0][1]
    else:
        env = next(iter(db_config.keys()))

    con.set_db_config(db_config[env])

    before()
    after()