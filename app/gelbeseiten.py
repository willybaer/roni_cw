import getopt
import sys
import json
import app.db.config as config_file
import app.db.connection as con
import logging
import re

from urllib.request import urlopen
from urllib.error import HTTPError
from bs4 import BeautifulSoup, Comment

from app.model.city import City
from app.model.location import Location
from app.model.category import Category
from app.model.location_category import LocationCategory

GELBE_SEITEN_URL = 'https://www.gelbeseiten.de'
INDUSTRIAL_SECTORS_URL = 'https://www.gelbeseiten.de/branchenbuch'

GERMAN_STATE_SITES = [
    'baden-wuerttemberg',
    'bayern',
    'saarland',
    'rheinland-pfalz',
    'hessen',
    'thueringen',
    'sachsen',
    'sachsen-anhalt',
    'brandenburg',
    'berlin',
    'nordrhein-westfalen',
    'niedersachsen',
    'bremen',
    'hamburg',
    'schleswig-holstein',
    'mecklenburg-vorpommern'
]

def query_industry_details(details_link, gelbeseiten_id, latitude, longitude):
    html = urlopen(details_link)
    soup = BeautifulSoup(html.read(), 'html5lib')

    industry_name = soup.find('h1', 'mod-TeilnehmerKopf__name').getText()
    address = soup.find('address', 'mod-TeilnehmerKopf__adresse').find_all('span')

    street = None
    postal_code = None
    for entry in address:
        prop = entry.get('property')
        if prop == 'streetAddress':
            street = entry.getText()
        elif prop == 'postalCode':
            # Remove spaces
            postal_code = entry.getText().replace(' ', '')    
        elif prop == 'addressLocality':
            city_name = entry.getText()
        else:
            continue        

    # Find city in our database
    city = City.find_by_postal_code_and_alpa_2_code(postal_code=postal_code, alpha_2_code='DE') 
    assert city is not None
    # TODO: Should we update the city name?
    
    # Check if there is already a location  
    location = Location.find_by_street_and_city_and_name(street=street, city_uuid=city.uuid, name=industry_name)
    if location is None:
        # Extracting contact information and branches
        contact_information = soup.find('section', id='kontaktdaten')
        
        # phone
        phone = contact_information.select('span[data-role="telefonnummer"]')
        if (phone is not None) and (len(phone) > 0):
            phone = phone[0].get('data-suffix')
            print(phone)

        # email
        email = contact_information.select('a[property="email"]')
        if (email is not None) and (len(email) > 0):
            email = email[0].get('content')
            print(email)
        else:
            email = None

        # website
        website = contact_information.select('a[property="url"]')
        if (website is not None) and (len(website) > 0): 
            website = website[0].get('href')
            print(website)
        else:
            website = None
        # facebook
        facebook = contact_information.select('a[href*="facebook.com"]')
        if (facebook is not None) and (len(facebook) > 0):
            facebook = facebook[0].get('href')
            print(facebook)
        else:
            facebook = None

        # Save location object
        location = Location(city.uuid, name=industry_name, street=street, phone=phone, email=email, website=website, latitude=float(latitude), longitude=float(longitude), gelbeseiten_id=gelbeseiten_id, facebook=facebook)
        location.insert()

        # categories
        categories = soup.find('section', id='branchen_und_stichworte').find('ul', 'mod-BranchenUndStichworte--branchen')
        categories = categories.find_all('li')
        for category in categories:
            category = category.getText()
            existing_category = Category.find_by_name_de(name_de=category)
            if existing_category is None:
                existing_category = Category(parent_category_uuid=None, name_de=category)   
                existing_category.insert() 

            LocationCategory(location_uuid=location.uuid, category_uuid=existing_category.uuid).insert()

    else:
        # TODO: Should we update the location?        
        print('Location is already existing: name=%s and city=%s' %(industry_name, city.name))

def query_industries_list_for_city(city_link):
    iteration = 1
    while True:
        try:
            html = urlopen('%s/s%d' % (city_link, iteration))
        except HTTPError as e:
            if e.code == 410:
                break

        soup = BeautifulSoup(html.read(), 'html5lib')
        industry_entries = soup.find_all('article', 'teilnehmer')
        for entry in industry_entries:
            entry_link = entry.get('data-href')
            data_map = entry.get('data-map')
            if data_map is not None:
                data_map = json.loads(data_map)
                query_industry_details(entry_link, data_map['realId'], data_map['wgs84Lat'], data_map['wgs84Long'])    


def query_sub_sector_in_cities(sub_sectors_link):
    for state in GERMAN_STATE_SITES:
        html = urlopen('%s/%s' % (sub_sectors_link, state))
        soup = BeautifulSoup(html.read(), 'html5lib')
        
        # Now iterate through all cities in state
        city_links = soup.find('div', 'cities').find_all('a', href=True)
        for city_link in city_links:
            link = city_link.get('href')
            query_industries_list_for_city(link)

def query_main_sector(sectors_link):
    # Can have multiple pages
    iteration = 1
    while True:
        try:
            html = urlopen('%s/s%d' % (sectors_link, iteration))
        except HTTPError as e:
            if e.code == 404:
                break

        soup = BeautifulSoup(html.read(), 'html5lib')

        # Now iterate through all sub sectors
        sub_sectors_list = soup.find('div', 'topic_home_page page_1').find_all('a', href=True)
        for sub_sectors_link in sub_sectors_list:
            link = sub_sectors_link.get('href')
            if link.startswith(INDUSTRIAL_SECTORS_URL):
                query_sub_sector_in_cities(link)

        iteration += 1        

def query_industry_sectors():
    # We are looking for the submenu "sub-menu menu_level_2 topMenuDropdown" called Branchebuch.
    html = urlopen(GELBE_SEITEN_URL)
    soup = BeautifulSoup(html.read(), 'html5lib')

    sectors_list = soup.find_all('ul', 'sub-menu menu_level_2 topMenuDropdown')
    # Should be the second entry
    # Now look for each <li><a> href value
    for sector in sectors_list[1].find_all('li'):
        sectors_link = sector.find('a', href=True).get('href')        
        query_main_sector(sectors_link)

def main():    
    logging.basicConfig(level=logging.DEBUG, stream=sys.stdout,
                        format='%(asctime)-15s %(levelname)-8s %(message)s')

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
        env = next(iter(config_file.db_config.keys()))

    con.set_db_config(config_file.db_config[env])

    # query industries
    query_industry_sectors()    

if __name__ == '__main__':
    main()