import json
from urllib.request import urlopen
from geo.geo import Geo
from geo.map_square import MapSquare

CLIEND_ID = '33FG1P5NOGUXSXBBF24XJHBWLSUGLKIH2F0SSJT2F1ZS1FLE'
SECRET = '1EPSAW44U3M5PPPCCCNRUXURVGHHRHXUE2DAYM0VFE33DARZ'
VENUES_URL = 'https://api.foursquare.com/v2/venues/search'


def get_venues():
    MapSquare.delete_all()
    squares = Geo.calculate_map_squares([47.452498, 8.413337], [47.382922, 8.525270], 800)

    if squares:
        print(squares[1].__dict__)
        url = '%s?client_id=%s&client_secret=%s&v=20170120&m=foursquare&sw=%s&ne=%s&intent=browse' % (
            VENUES_URL,
            CLIEND_ID,
            SECRET,
            ','.join(str(x) for x in squares[1].bottom_left),
            ','.join(str(x) for x in squares[1].top_right))

        print(url)
        response = urlopen(url).read()
        venues = json.loads(response, encoding='UTF-8')['response']['venues']
        print(venues)


if __name__ == '__main__':
    get_venues()
