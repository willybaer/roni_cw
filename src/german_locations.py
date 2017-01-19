from urllib.request import urlopen
from bs4 import BeautifulSoup, Comment
from default.city import City
from psycopg2 import IntegrityError

import regex

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
                        details_html = urlopen('http://www.orte-in-deutschland.de/%s' % details_url)
                        soup_details = BeautifulSoup(details_html.read(), 'html.parser')
                        if soup_details:
                            main = soup_details.find('main')

                            name = soup_details.select('#content > main > strong')[3]
                            if name:
                                name = name.getText()

                            zip = main.find('a', href=regex.compile('^postleitzahl.*'))
                            if zip:
                                zip = zip.getText()

                            state = main.find('a', href=regex.compile('.*\-bundesland\-.*'))
                            if state:
                                state = state.getText()

                            lat = main.find(text=regex.compile('Latitude'))
                            lng = main.find(text=regex.compile('Longitude'))

                            if lat and lng:
                                lat = regex.findall(r'(?<=\()(.*)(?=\°\))', lat)[0]
                                lng = regex.findall(r'(?<=\()(.*)(?=\°\))', lng)[0]

                            new_city = City(zip=zip, city=name, state=state, latitude=lat, longitude=lng)
                            print('Creating City %s', new_city.uuid)
                            try:
                                new_city.insert()
                            except IntegrityError as e:
                                print(e)



if __name__ == "__main__":
    parse_cities()
