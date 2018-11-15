import getopt
import sys
import app.db.connection as con
import regex

from requests_html import HTMLSession
from app.db.config import db_config
from urllib.request import urlopen
from bs4 import BeautifulSoup, Comment
from app.model.city import City
from psycopg2 import IntegrityError, ProgrammingError

def parse_city(details_link, name):
    # 3. Get details url
    details_html = urlopen(details_link)
    soup_details = BeautifulSoup(details_html.read(), 'html5lib')
    if soup_details:

        # IF Details page will fail
        print('Crawling deatils page: %s' % details_link)
        try:
            details_table = soup_details.find('table', attrs={'class': 'wikitable float-right'}).find('tbody')
        except Exception as e:
            print('Failed due to: %s' % e.__cause__)

        detail_rows = details_table.findAll('tr')

        canton = detail_rows[3].findAll('td')[1].find('a')
        if canton:
            canton = canton.getText()

        state = detail_rows[4].findAll('td')[1].find('a')
        if state:
            state = state.getText()

        postal_codes = details_table.find('a', title=regex.compile('.*Postleitzahl.*')).parent.parent.findAll('td')[1]
        if postal_codes:
            postal_codes = postal_codes.getText()
            postal_codes = regex.findall(r'\d{4}', postal_codes)

        for postal_code in postal_codes:
            coords_link = details_table.find('span', attrs={'class': 'coordinates'})
            lat = None
            lng = None
            if coords_link:
                coords_link = coords_link.find('a', attrs={'class': 'external text'})
                if coords_link:
                    coords_link = coords_link.get('href')
                    lat = regex.findall(r'(?<=params=)(.*)(?=\_N)', coords_link)[0]
                    lng = regex.findall(r'(?<=\_N_)(.*)(?=\_E)', coords_link)[0]

            website = details_table.find('a', href=regex.compile('.*www.*'))
            if website:
                website = website.getText()

            existing_city = City.find_by_postal_code_and_alpa_2_code(postal_code=postal_code, alpha_2_code='CH')
            if existing_city is not None:
                existing_city.name = name
                existing_city.website = website
                print('Updating City name:%s and postal_code:%s' % (existing_city.name, existing_city.postal_code))
                try:
                    existing_city.update()
                except IntegrityError as e:
                    print(e)
                except ProgrammingError as e:
                    print(e)
            else:
                new_city = City(postal_code=postal_code, name=name, state=state, latitude=lat,
                                longitude=lng, canton=canton, website=website,
                                alpha_2_code='CH', country='Schweiz')
                print('Creating City name:%s and postal_code:%s' % (new_city.name, new_city.postal_code))
                try:
                    new_city.insert()
                except IntegrityError as e:
                    print(e)
                except ProgrammingError as e:
                    print(e)
                    print(new_city.__dict__)

def parse_cities():
    # First clear cities in database
    alphabet = list(map(chr, list(range(65, 91))))

    # 1. Iterate through all city lists
    for char in alphabet:
        html = urlopen('https://de.wikipedia.org/wiki/Gemeinden_der_Schweiz-%s' % char)
        soup = BeautifulSoup(html.read(), 'html5lib')

        cities_table = soup.find('table', attrs={'class': 'wikitable'})
        if cities_table:
            cities_table = cities_table.find('tbody')
            city_entries = cities_table.findAll('tr')
        else:
            cities_table = soup.find('ul')
            city_entries = cities_table.findAll('li')

        for city_row in city_entries:
            details_url = city_row.find('a', href=True)
            if not isinstance(city_row, Comment) and details_url is not None:
                # 2. Iterate through all cities
                name = details_url.getText()
                details_url = details_url.get('href')
                if details_url:
                    parse_city('https://de.wikipedia.org%s' % details_url, name=name)

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
