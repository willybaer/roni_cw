# https://github.com/Yelp/yelp-fusion/blob/master/fusion/python/sample.py
import json
import sys
import logging
import requests

from urllib.parse import quote
from urllib.parse import urlencode
from geo.map_square import MapSquare
from events.location import Location
from events.location_category import LocationCategory
from default.category import Category
from default.city import City
from psycopg2 import IntegrityError, DataError

# OAUth credentials
CLIENT_ID = 'INr7T2Mef2v0xY6-q1dGuw'
CLIENT_SECRET = 'cwaT6vlEaiiitHuC0tPnoXzByc7eg7AURmDm5XVL4dI1xxft612xJ1M8vPCrvpo5'

# API Constants
API_HOST = 'https://api.yelp.com'
SEARCH_PATH = '/v3/businesses/search'
BUSINESS_PATH = '/v3/businesses/'  # Business ID will come after slash.
TOKEN_PATH = '/oauth2/token'
GRANT_TYPE = 'client_credentials'


def get_request(host, path, bearer_token, url_params=None):
    """Given a bearer token, send a GET request to the API.
    Args:
        host (str): The domain host of the API.
        path (str): The path of the API after the domain.
        bearer_token (str): OAuth bearer token, obtained using client_id and client_secret.
        url_params (dict): An optional set of query parameters in the request.
    Returns:
        dict: The JSON response from the request.
    Raises:
        HTTPError: An error occurs from the HTTP request.
    """
    url_params = url_params or {}
    url = '{0}{1}'.format(host, quote(path.encode('utf8')))
    headers = {
        'Authorization': 'Bearer %s' % bearer_token,
    }

    print(u'Querying {0} ...'.format(url))

    response = requests.request('GET', url, headers=headers, params=url_params)

    return response.json()


def obtain_bearer_token(host, path):
    """Given a bearer token, send a GET request to the API.
    Args:
        host (str): The domain host of the API.
        path (str): The path of the API after the domain.
        url_params (dict): An optional set of query parameters in the request.
    Returns:
        str: OAuth bearer token, obtained using client_id and client_secret.
    Raises:
        HTTPError: An error occurs from the HTTP request.
    """
    url = '{0}{1}'.format(host, quote(path.encode('utf8')))
    assert CLIENT_ID, "Please supply your client_id."
    assert CLIENT_SECRET, "Please supply your client_secret."
    data = urlencode({
        'client_id': CLIENT_ID,
        'client_secret': CLIENT_SECRET,
        'grant_type': GRANT_TYPE,
    })
    headers = {
        'content-type': 'application/x-www-form-urlencoded',
    }
    response = requests.request('POST', url, data=data, headers=headers)
    bearer_token = response.json()['access_token']
    return bearer_token


def search_venues(bearer_token, latitude, longitude, radius=1130, limit=50, offset=0):
    url_params = {
        'latitude': latitude,
        'longitude': longitude,
        'radius': radius,
        'limit': limit,
        'lang': 'de',
        'offset': offset

    }
    return get_request(API_HOST, SEARCH_PATH, bearer_token, url_params=url_params)


def main():
    # 1. Get map square
    squares = MapSquare.find_all_yelp_not_queried()
    if squares and len(squares) > 0:
        bearer_token = obtain_bearer_token(API_HOST, TOKEN_PATH)

        for square in squares:
            lat = square.bottom_left[0] + ((square.top_right[0] - square.bottom_left[0]) / 2)
            lng = square.bottom_left[1] + ((square.top_right[1] - square.bottom_left[1]) / 2)

            response = search_venues(bearer_token=bearer_token, latitude=lat, longitude=lng)
            if not response:
                continue

            if response['total'] > 0:
                venues = response['businesses']
                while len(venues) < response['total']:
                    response = search_venues(bearer_token=bearer_token, latitude=lat, longitude=lng, offset=len(venues))
                    venues.extend(response['businesses'])

                filtered_venues = list(filter(lambda x: 'location' in x
                                                        and 'country' in x['location']
                                                        and 'address1' in x['location']
                                                        and 'zip_code' in x['location'], venues))

                for filtered_venue in filtered_venues:
                    # 2. Get city for given venues
                    city = City.find_by_zip_and_cc(zip=filtered_venue['location']['zip_code'], cc=filtered_venue['location']['country'])

                    if city:
                        # We will only add foursquare venues, if there is an existing city entry in our db
                        location = Location.find_by_yelp_id(filtered_venue['id'])
                        if not location:
                            # Do not create location
                            location = Location(city_uuid=city.uuid,
                                                yelp_id=filtered_venue['id'],
                                                name=filtered_venue['name'],
                                                phone=filtered_venue['phone'],
                                                street=filtered_venue['location']['address1'],
                                                latitude=filtered_venue['coordinates']['latitude'],
                                                longitude=filtered_venue['coordinates']['longitude'])
                            try:
                                location.insert()
                                logging.info('Added yelp location for id %s' % location.uuid)
                            except IntegrityError as e:
                                logging.info(e)
                                continue

                        # Add location categories reference
                        for f_category in filtered_venue['categories']:
                            category = Category.find_by_yelp_alias(f_category['alias'])
                            if not category:
                                category = Category(name_de=f_category['title'], yelp_alias=f_category['alias'])
                                category.insert()
                                logging.info('Added new yelp category for alias %s' % category.yelp_alias)

                            location_category = LocationCategory.find_by_location_and_category(location_uuid=location.uuid,
                                                                                                   category_uuid=category.uuid)
                            if not location_category:
                                # Expecting that foursquare categories are existing in the db
                                location_category = LocationCategory(location_uuid=location.uuid, category_uuid=category.uuid)
                                location_category.insert()
                                logging.info('Added location category for id %s' % location_category.uuid)

            square.update_yelp_queried_at()

if __name__ == '__main__':
    logging.basicConfig(level=logging.DEBUG, stream=sys.stdout,
                        format='%(asctime)-15s %(levelname)-8s %(message)s')
    main()
