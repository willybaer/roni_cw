from urllib.request import urlopen
from bs4 import BeautifulSoup, Comment
from default.city import City
from psycopg2 import IntegrityError, ProgrammingError

import regex


def parse_cities():
    # First clear cities in database
    City.delete_all_for_country_code('AT')

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
                    # 3. Get details url
                    details_html = urlopen('http://www.gemeinden.at/%s' % details_url)
                    soup_details = BeautifulSoup(details_html.read(), 'html5lib')
                    if soup_details:
                        # IF Details page will fail
                        try:
                            details_table = soup_details.find('div', attrs={'class': 'boxdarkgrey2'})
                        except:
                            print('http://www.gemeinden.at/%s' % details_url)
                            continue

                        zip = details_table.find('a', href=regex.compile('.*plz.*'))
                        if zip:
                            zip = zip.getText()

                        state = details_table.find('div', text=regex.compile('Bundesland')).parent.find('a')
                        if state:
                            state = state.getText()

                        website = details_table.find('div', text=regex.compile('Homepage'))
                        if website:
                            website = website.parent.find('a')
                            website = website.get('href')

                        details_table = soup_details.find('div', attrs={'class': 'boxlightgrey'})
                        coords_link = details_table.find('img', src=regex.compile('^http://maps.google.*'))
                        if coords_link:
                            coords_link = coords_link.get('src')
                            if coords_link:
                                coords_link = regex.findall(r'(?<=center\=)(.*)(?=\&zoom)', coords_link)[0]
                                coords_link = coords_link.split(',')
                                lat = coords_link[0]
                                lng = coords_link[1]

                        new_city = City(zip=zip, city=name, state=state, website=website,
                                        latitude=lat, longitude=lng,
                                        alpha_2_code='AT', country='Österreich')
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
