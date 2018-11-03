from urllib.request import urlopen
from bs4 import BeautifulSoup, Comment
from default.city import City
from psycopg2 import IntegrityError, ProgrammingError

import regex


def parse_cities():
    # First clear cities in database
    City.delete_all_for_country_code('CH')

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
                    # 3. Get details url
                    details_html = urlopen('https://de.wikipedia.org%s' % details_url)
                    soup_details = BeautifulSoup(details_html.read(), 'html5lib')
                    if soup_details:

                        # IF Details page will fail
                        try:
                            details_table = soup_details.find('table', attrs={'class': 'wikitable float-right'}).find('tbody')
                        except:
                            print('https://de.wikipedia.org%s' % details_url)
                            continue

                        detail_rows = details_table.findAll('tr')

                        canton = detail_rows[3].findAll('td')[1].find('a')
                        if canton:
                            canton = canton.getText()

                        state = detail_rows[4].findAll('td')[1].find('a')
                        if state:
                            state = state.getText()

                        zip = details_table.find('a', title=regex.compile('.*Postleitzahl.*')).parent.parent.findAll('td')[1]
                        if zip:
                            zip = next(zip.children)

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

                        new_city = City(zip=zip, city=name, state=state, latitude=lat,
                                        longitude=lng, canton=canton, website=website,
                                        alpha_2_code='CH', country='Schweiz')
                        print('Creating City %s' % new_city.uuid)
                        try:
                            new_city.insert()
                        except IntegrityError as e:
                            print(e)
                        except ProgrammingError as e:
                            print(e)
                            print(new_city.__dict__)


if __name__ == "__main__":
    parse_cities()
