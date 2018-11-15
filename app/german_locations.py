import getopt
import sys
import app.db.connection as con
import regex
import json
import string
import urllib

from bs4 import BeautifulSoup, Comment
from app.model.city import City
from psycopg2 import IntegrityError
from app.db.config import db_config

HEADERS = { 'User-Agent' : 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_12_6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/61.0.3163.100 Safari/537.36',
            'Remote Address' : '[2606:4700:20::6819:3967]:443', 
            'Request Method' : 'GET' }

def parse_content(details_url):
    print(details_url)
    req = urllib.request.Request(details_url, headers=HEADERS)
    details_html = urllib.request.urlopen(req)
    soup_details = BeautifulSoup(details_html.read(), 'html.parser')
    if soup_details:
        main = soup_details.select_one('#infobox > table')
        if main is None:
            return

        main = main.find_all('tr')
        name = soup_details.select_one('#content-loc > div > div.col-lg-12 > header > h1').getText().strip()
        state = main[1].find('td').getText().strip()
        
        map_details = soup_details.select_one('#content-loc > div > div.col-md-4 > div.panel.panel-default.no-print > div.panel-footer > div').find_all('div', 'col-xs-6')

        lat = map_details[0].getText().split(' ')
        lat = lat[len(lat) - 1]
        lng = map_details[1].getText().split(' ')
        lng = lng[len(lng) -1]

        postal_codes = main[3].find_all('a')
        if len(postal_codes) > 1 and len(main) > 4:
            postal_codes = main[4].find_all('a')

        postal_codes = list(map(lambda code: code.getText().strip(), postal_codes))
        code = postal_codes[0]
        parent_city = City.find_matched_city_by_postal_code_and_name(postal_code=code, alpha_2_code='DE', city_name=name)
        if parent_city is None:    
            parent_city = City(postal_code=postal_codes, name=name, state=state, latitude=float(lat), 
                        longitude=float(lng), country='Deutschland', alpha_2_code='DE')
            print('Creating City %s' % parent_city.postal_code)
            try:
                parent_city.insert()
            except IntegrityError as e:
                print(e)
        else:
            print('Found Matching city for name:%s and postal_code:%s', (parent_city.name, parent_city.postal_code))

        # Insert sub - cities
        sub_cities = soup_details.select_one('#ortsteile > table > tbody')    
        if sub_cities:
            sub_cities = sub_cities.find_all('tr')
            for entry in sub_cities:
                td = entry.find_all('td')
                sub_name = td[0].getText().strip()
                postal_code = postal_codes
                if len(td) > 1:
                    postal_code = td[1].find_all('a')
                    postal_code = list(map(lambda c: c.getText().strip(), postal_code))
                code = postal_code[0]
                sub_city = City.find_matched_city_by_postal_code_and_name(postal_code=code, alpha_2_code='DE', city_name=sub_name)
                if sub_city is None:
                    sub_city = City(parent_city_uuid=parent_city.uuid, postal_code=postal_code, name=sub_name, state=state, latitude=float(lat), 
                        longitude=float(lng), country='Deutschland', alpha_2_code='DE')
                    print('Creating Sub City name:%s, postal_code:%s parent:%s' % (sub_city.name, sub_city.postal_code, parent_city.name))
                    try:
                        sub_city.insert()
                    except IntegrityError as e:
                        print(e)
                else: 
                    print('Found Matching sub-city for name:%s and postal_code:%s', (sub_city.name, sub_city.postal_code))


def parse_cities():
    # 1. Iterate through all city lists
    for char in string.ascii_uppercase:
        url = 'https://www.suche-postleitzahl.org/orte?q=%s&json=1' % char
        
        req = urllib.request.Request(url, headers=HEADERS)
        res = urllib.request.urlopen(req)
        
        cities = res.read()
        cities = json.loads(cities.decode('utf-8'))['data']

        for city_entry in cities:
            city_link = regex.findall(r'(?<=href=")(.*)(?=">)', city_entry[0])[0]
            parse_content(city_link)

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
