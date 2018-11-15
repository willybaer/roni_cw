from urllib.request import urlopen
from bs4 import BeautifulSoup, Comment
from app.model.city import City
from psycopg2 import IntegrityError, ProgrammingError
from app.db.config import db_config

import regex
import getopt
import sys
import app.db.connection as con

def parse_city(details_url):
    print(details_url)
    details_html = urlopen('http://www.gemeinden.at/%s' % details_url)
    soup_details = BeautifulSoup(details_html.read(), 'html5lib')
    if soup_details:
        # IF Details page will fail
        details_table = None
        try:
            details_table = soup_details.select_one('body > center > div > div:nth-of-type(4) > div:nth-of-type(2) > div.boxdarkgrey2')
        except:
            print('http://www.gemeinden.at/%s' % details_url)
            return
        
        name = soup_details.select_one('body > center > div > div:nth-of-type(4) > div:nth-of-type(2) > div.boxdarkgrey2 > div > div:nth-of-type(1) > div:nth-of-type(1) > div:nth-of-type(2) > span')
        if name:
            name = name.getText().lstrip()
            
        postal_codes = details_table.find_all('a', href=regex.compile('.*plz.*'))
        postal_codes = list(map(lambda p: p.getText(), postal_codes))

        state = details_table.find('div', text=regex.compile('.*Bundesland.*')).parent.find('a')
        if state:
            state = state.getText().strip()

        website = details_table.find('div', text=regex.compile('Homepage'))
        if website:
            website = website.parent.find('a')
            website = website.get('href')

        table = soup_details.find('div', class_='boxlightgrey')
        coords_link = table.find('img', src=regex.compile('^http:\/\/maps.googleapis.*'))
        lat = None
        lng = None
        if coords_link:
            coords_link = coords_link.get('src')
            if coords_link:
                coords_link = regex.findall(r'(?<=center\=)(.*)(?=\&zoom)', coords_link)[0]
                coords_link = coords_link.split(',')
                lat = coords_link[0]
                lng = coords_link[1]

        city = City.find_matched_city_by_postal_code_and_name(postal_code=postal_codes[0], alpha_2_code='AT', city_name=name)
        if city is None:
            new_city = City(postal_code=postal_codes, name=name, state=state, website=website,
                            latitude=lat, longitude=lng,
                            alpha_2_code='AT', country='Österreich')
            print('Creating City %s' % new_city.name)
            try:
                new_city.insert()
            except IntegrityError as e:
                print(e)
            except ProgrammingError as e:
                print(e)
        else:
            print('City already existing %s' % city.name)

def parse_cities():
    alphabet = list(map(chr, list(range(65, 91))))

    # 1. Iterate through all city lists
    for char in alphabet:
        html = urlopen('http://www.gemeinden.at/gemeinden/namen/%s' % char)
        soup = BeautifulSoup(html.read(), 'html5lib')

        cities_table = soup.find('table', attrs={'border': '0', 'cellpadding': '4'})
        if cities_table:
            cities_table = cities_table.find('tbody')
        else:
            continue
        city_entries = cities_table.findAll('tr')
        for city_row in city_entries:
            details_url = city_row.find('a', href=True)
            if not isinstance(city_row, Comment) and details_url:
                # 2. Iterate through all cities
                name = details_url.getText()
                details_url = details_url.get('href')
                if details_url:
                    parse_city(details_url)

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
