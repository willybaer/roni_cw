import getopt
import sys
import json
import db.config as config_file
import db.connection as con
import geo.config as geo_config
import logging

from urllib.request import urlopen
from geo.geo import Geo
from geo.map_square import MapSquare
from default.city import City
from events.location import Location
from default.category import Category
from events.location_category import LocationCategory
from psycopg2 import IntegrityError

CLIEND_ID = '33FG1P5NOGUXSXBBF24XJHBWLSUGLKIH2F0SSJT2F1ZS1FLE'
SECRET = '1EPSAW44U3M5PPPCCCNRUXURVGHHRHXUE2DAYM0VFE33DARZ'
VENUES_URL = 'https://api.foursquare.com/v2/venues/search'


def get_venues():
    squares = MapSquare.find_all_not_queried()
    for square in squares:
        url = '%s?client_id=%s&client_secret=%s&v=20170120&m=foursquare&sw=%s&ne=%s&intent=browse' % (
            VENUES_URL,
            CLIEND_ID,
            SECRET,
            ','.join(str(x) for x in square.bottom_left),
            ','.join(str(x) for x in square.top_right))

        logging.info(url)
        response = urlopen(url).read().decode('utf8') # Verarbeiten von urllib.error.HTTPError: HTTP Error 403: Forbidden wenn die Requests aufgebraucht sind
        venues = json.loads(response, encoding='UTF-8')['response']['venues']

        # Filter venues where a full location is existing
        if len(venues) > 0:
            filtered_venues = list(filter(lambda x: 'location' in x
                                                    and 'cc' in x['location']
                                                    and 'country' in x['location']
                                                    and 'address' in x['location']
                                                    and 'postalCode' in x['location']
                                                    and 'city' in x['location'], venues))

            for filtered_venue in filtered_venues:
                city = City.find_by_zip_and_cc(zip=filtered_venue['location']['postalCode'],
                                                cc=filtered_venue['location']['cc'])
                if city:
                    # We will only add foursquare venues, if there is an existing city entry in our db
                    location = Location.find_by_foursquare_id(filtered_venue['id'])
                    if not location:
                        # Do not create location
                        location = Location(city_uuid=city.uuid,
                                            foursquare_id=filtered_venue['id'],
                                            name=filtered_venue['name'],
                                            street=filtered_venue['location']['address'],
                                            latitude=filtered_venue['location']['lat'],
                                            longitude=filtered_venue['location']['lng'])
                        try:
                            location.insert()
                            logging.info('Added foursquare location for id %s' % location.uuid)
                        except IntegrityError as e:
                            logging.info(e)
                            continue

                    # Add location categories reference
                    for f_category in filtered_venue['categories']:
                        category = Category.find_by_foursquare_id(f_category['id'])
                        if category:
                            location_category = LocationCategory.find_by_location_and_category(location_uuid=location.uuid,
                                                                                               category_uuid=category.uuid)
                            if not location_category:
                                # Expecting that foursquare categories are existing in the db
                                location_category = LocationCategory(location_uuid=location.uuid, category_uuid=category.uuid)
                                location_category.insert()
                                logging.info('Added location category for id %s' % location_category.uuid)
        # Finally update that square was used for a query
        square.update_queried_at()


def setup():
    # Delete all squares
    MapSquare.delete_all()

    # Top Left and bottom right
    for box in geo_config.bounding_boxes['switzerland']:
        squares = Geo.calculate_map_squares(box['top_left'],
                                            box['bottom_right'], 800)

        logging.info('Trying to insert %s squares' % len(squares))
        MapSquare.insert_all(squares)
        logging.info('Inserted %s squares' % len(squares))


def main(argv):
    try:
        opts, args = getopt.getopt(argv[1:], 'svd:', ['setup', 'venue', 'db='])
    except getopt.GetoptError:
        sys.exit(2)

    # DB environment
    env = list(filter(lambda x: x[0] in ('-d', '--db'), opts))
    if env and len(env) > 0:
        env = env[0][1]
    else:
        env = next(iter(config_file.db_config.keys()))

    con.set_db_config(config_file.db_config[env])

    for opt, arg in opts:
        if opt in ('-s', '--setup'):
            setup()
        elif opt in ('-v', '--venue'):
            get_venues()


if __name__ == '__main__':
    logging.basicConfig(level=logging.DEBUG, stream=sys.stdout,
                        format='%(asctime)-15s %(levelname)-8s %(message)s')
    main(sys.argv)
