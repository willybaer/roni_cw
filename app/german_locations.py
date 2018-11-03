import getopt
import sys
import app.db.connection as con
import regex

from urllib.request import urlopen
from bs4 import BeautifulSoup, Comment
from app.model.city import City
from psycopg2 import IntegrityError
from app.db.config import db_config


def parse_content(details_url):
    details_html = urlopen('http://www.orte-in-deutschland.de/%s' % details_url)
    soup_details = BeautifulSoup(details_html.read(), 'html.parser')
    if soup_details:
        main = soup_details.find('main')

        name = soup_details.select('#content > main > strong')[3]
        if name:
            name = name.getText()

        postal_codes = main.find_all('a', href=regex.compile('^postleitzahl.*'))
        for postal_code in postal_codes :
            code = postal_code.getText()

            state = main.find('a', href=regex.compile('.*\-bundesland\-.*'))
            if state:
                state = state.getText()

            lat = main.find(text=regex.compile('Latitude'))
            lng = main.find(text=regex.compile('Longitude'))

            if lat and lng:
                lat = regex.findall(r'(?<=\()(.*)(?=\°\))', lat)[0]
                lng = regex.findall(r'(?<=\()(.*)(?=\°\))', lng)[0]

            city = City.find_by_postal_code_and_alpa_2_code(postal_code=code, alpha_2_code='DE')
            if city is not None:
                city.name = name
                city.latitude = float(lat)
                city.longitude = float(lng)
                city.state = state
                print('Updating City %s' % city.postal_code)
            else:    
                new_city = City(postal_code=code, name=name, state=state, latitude=float(lat), longitude=float(lng), country='Deutschland', alpha_2_code='DE')
                print('Creating City %s' % new_city.postal_code)
                try:
                    new_city.insert()
                except IntegrityError as e:
                    print(e)

def parse_cities():
    # First clear cities database
    City.delete_all_for_country_code('DE')

    alphabet = list(map(chr, list(range(97, 123))))
    # 1. Iterate through all city lists
    for char in alphabet:
        for char2 in alphabet:
            html = urlopen('http://www.orte-in-deutschland.de/orte-in-deutschland-mit-%s%s.html' % (char, char2))
            soup = BeautifulSoup(html.read(), 'html.parser')

            cities_table = soup.find('div', attrs={'class': 'spaltencontainer'})
            for city_div in cities_table.children:
                if not isinstance(city_div, Comment):
                    # 2. Iterate through all cities
                    details_url = city_div.find('a', href=True).get('href')
                    if details_url:
                        # 3. Get details url
                        parse_content(details_url)

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

    parse_cities()

if __name__ == "__main__":
    main()
