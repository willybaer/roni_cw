import getopt
import sys
import json
import app.db.config as config_file
import app.db.connection as con
import logging
import re
import string
import json
import xml.etree.ElementTree as ET
import os
import gzip
import shutil

from urllib.request import urlopen
from urllib.error import HTTPError
from bs4 import BeautifulSoup, Comment
from roni_utils.argsextractor import filter_args

from roni_database.models.city import City
from roni_database.models.location import Location
from roni_database.models.category import Category
from roni_database.models.location_category import LocationCategory

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

ALPHABET_LIST = [
    '%23'
]
ALPHABET_LIST.extend(string.ascii_lowercase)

def query_industry_details(details_link, gelbeseiten_id):
    print(details_link)
    try:
        html = urlopen(details_link)
    except HTTPError as e:
        print(e)
        if e.code == 410:
            return
    
    soup = BeautifulSoup(html.read(), 'html5lib')

    latitude = soup.find('meta',  property='latitude')
    longitude = soup.find('meta',  property='longitude')
    if latitude and longitude:
        latitude = float(latitude['content'])
        longitude = float(longitude['content'])

    industry_name = soup.find('h1', 'mod-TeilnehmerKopf__name').getText()
    assert industry_name is not None
    address = soup.find('address', 'mod-TeilnehmerKopf__adresse').find_all('span')

    street = None
    postal_code = None
    city_name = None
    for entry in address:
        prop = entry.get('property')
        if prop == 'streetAddress':
            street = entry.getText()
            print(street)
        elif prop == 'postalCode':
            # Remove spaces
            postal_code = entry.getText().replace(' ', '') 
            print(postal_code)   
        elif prop == 'addressLocality':
            city_name = entry.getText()
            print(city_name)
        else:
            continue        

    # Find city in our database
    if postal_code is None:
        print('----- Missing information about the postal code IGNORING-----')
        return

    if city_name is None:
        print('----- Missing information about the postal code IGNORING-----')
        return

    city = City.find_matched_city_by_postal_code_and_name(postal_code=postal_code, alpha_2_code='DE', city_name=city_name) 
    if city is None:
        print('---- NO CITY FOUND -----')
        return

    # Extracting contact information and branches
    contact_information = soup.find('section', id='kontaktdaten')
    
    # phone
    phone = None
    phone_info = contact_information.select('span[data-role="telefonnummer"]')
    if (phone_info is not None) and (len(phone_info) > 0):
        phone = phone_info[0].get('data-suffix')
    
    # Check if there is already a location
    location = None
    if street is not None:
        location = Location.find_by_street_and_city_and_name(street=street, city_uuid=city.uuid, name=industry_name)
    elif phone is not None:      
        location = Location.find_by_phone_and_city_and_name(phone=phone, city_uuid=city.uuid, name=industry_name)
    else:
        print('----- Missing information about industry IGNORING. Name: %s ------' % industry_name)
        return
            
    if location is None:
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
        location = Location(city_uuid=city.uuid, name=industry_name, street=street, phone=phone, email=email, website=website, latitude=latitude, longitude=longitude, gelbeseiten_id=gelbeseiten_id, facebook=facebook)
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

'''
SCRAPPING

Crawling for the details pages by searching for industry sectors and 
than to extract all locations for a given industry
'''
def query_industries_list_for_city(city_link):
    print('Industires list for city: %s ' % city_link)

    iteration = 1
    while True:
        try:
            url = '%s/s%d' % (city_link, iteration)
            print(url)
            html = urlopen(url)
        except HTTPError as e:
            print(e)
            if e.code == 410:
                break

        soup = BeautifulSoup(html.read(), 'html5lib')
        industry_entries = soup.find_all('article', 'teilnehmer')
        for entry in industry_entries:
            entry_link = entry.get('data-href')
            data_map = entry.get('data-map')
            if data_map is not None:
                data_map = json.loads(data_map)
                query_industry_details(entry_link, data_map['realId'])    

        iteration = iteration + 1

# It Changed - Now we have to query first the the locations for each state
def query_branches_for_letter(letters_link):
    html = urlopen(letters_link)
    soup = BeautifulSoup(html.read(), 'html5lib')

    branches_links = soup.find('table', class_='table--single-md').find_all('a', class_='link')
    return list(map(lambda branch: branch.get('href'), branches_links)) 

def query_branches_for_location(location_link):
    for letter in ALPHABET_LIST:
        url = '%s/branchen/%s' % (location_link, letter)
        branches = query_branches_for_letter(url)
        for branch_link in branches:
            query_industries_list_for_city(branch_link)


def query_locations_for_state(state):
    url = '%s/branchenbuch/%s/orte' % (GELBE_SEITEN_URL, state)    
    html = urlopen(url)
    soup = BeautifulSoup(html.read(), 'html5lib')

    locations = soup.find('tbody', class_='cityTable__body')
    locations = locations.find_all('a', 'link')
    return list(map(lambda location: GELBE_SEITEN_URL + location.get('href'), locations)) 

def query_locations_and_states():
    for state in GERMAN_STATE_SITES:
        locations = query_locations_for_state(state)
        for location_link in locations:
            query_branches_for_location(location_link)

'''
SITEMAPS

Extrating details pages form the sitemaps xml
'''
def write_failed_details_page(details_link):
    # Assert that the folder exists
    full_path = os.path.realpath(__file__)
    file_dir = os.path.split(full_path)[0]
    visited_dir = '%s/%s' % (file_dir, VISITED_FOLDER)
    assert os.path.exists(visited_dir)

    failed_crawling = '%s/failed_crawling' % visited_dir
    mode = 'w'
    if os.path.isfile(failed_crawling):
        mode = 'a' #Appending mode

    with open(failed_crawling, mode) as f:
        f.write('%s\n' % details_link)

def start_through_sitemaps():
    entries = take_first_in_next_sitemap(limit=100)
    for entry in entries:
        try:
            query_industry_details(entry, gelbeseiten_id=entry.split('/')[-1])
        except Exception as e:
            print(e)
            write_failed_details_page(entry)

    if len(entries) == 100:    
        start_through_sitemaps()    

VISITED_FOLDER = './gelbeseiten_visited'
def take_first_in_next_sitemap(limit=50):
    '''
    This function returns the an given amount of 
    sitemap entries and deleting the file after there are no more entries
    '''
    
    # Assert that the folder exists
    full_path = os.path.realpath(__file__)
    file_dir = os.path.split(full_path)[0]
    visited_dir = '%s/%s' % (file_dir, VISITED_FOLDER)
    assert os.path.exists(visited_dir)

    # Assert that there are files
    src_files = os.listdir(visited_dir)
    assert len(src_files) > 0

    # Read the entries from the file
    entries = []
    limit_left = limit
    for file_name in src_files:
        print('Extracting from file: %s' % file_name)

        full_file_name = os.path.join(visited_dir, file_name)
        f = open(full_file_name, 'r')
        xml = BeautifulSoup(f.read(), 'xml')
        f.close()
        
        sitemap_tags = xml.find_all("url", limit=limit_left)
        entries.extend(list(map(lambda s:  s.extract().find('loc').getText(), sitemap_tags)))
        limit_left = limit - len(entries)
        
        if limit_left == 0:
            # Write back content
            f = open(full_file_name, 'w')
            f.write(xml.prettify())
            f.close()
            break
        else:
            os.remove(full_file_name) # Delete file   

        
    return entries

def copy_sitemaps():
    '''
    Copy all txt files from the originals folder
    '''    
    
    # Check if the folder exists
    full_path = os.path.realpath(__file__)
    file_dir = os.path.split(full_path)[0]
    visited_dir = '%s/%s' % (file_dir, VISITED_FOLDER)
    if not os.path.exists(visited_dir):
        os.makedirs(visited_dir)
    
    # Remove all from destination folder
    dest_files = os.listdir(visited_dir)
    for file_name in dest_files:
        full_file_name = os.path.join(visited_dir, file_name)
        if os.path.isfile(full_file_name):
            os.remove(full_file_name)

    # Copy all .txt files from folder originals to visited
    downloads_dir = '%s/%s' % (file_dir, DOWNLOADS_FOLDER)
    assert os.path.exists(visited_dir)
        
    src_files = list(filter(lambda f: f.endswith('.txt'), os.listdir(downloads_dir)))
    for file_name in src_files:
        full_file_name = os.path.join(downloads_dir, file_name)
        if os.path.isfile(full_file_name):
            shutil.copy(full_file_name, visited_dir)    


DOWNLOADS_FOLDER = './gelbeseiten_originals'
def download_details_sitemap():
    # Check if the folder exists
    full_path = os.path.realpath(__file__)
    file_dir = os.path.split(full_path)[0]
    downloads_dir = '%s/%s' % (file_dir, DOWNLOADS_FOLDER)

    if not os.path.exists(downloads_dir):
        os.makedirs(downloads_dir)

    url = 'https://www.gelbeseiten.de/sitemap_index_Detailseite.xml'
    
    xml = urlopen(url)
    soup = BeautifulSoup(xml.read())
    
    sitemapTags = soup.find_all("sitemap")
    for child in sitemapTags:
        # Check if file exists
        url = child.find('loc').getText()
        name = url.split('/')
        name = name[-1]
        
        # gz and txt file
        filename = '%s/%s' % (downloads_dir, name)
        if os.path.exists(filename):
            os.remove(filename)
        filename_txt = '%s/%s.txt' % (downloads_dir, name.split('.')[0])
        if os.path.exists(filename_txt):
            os.remove(filename_txt)

        # Download gz file
        with open(filename, "wb") as f:
            r = urlopen(url)
            f.write(r.read())

        # Unzip gz
        with gzip.open(filename, 'rb') as f_in:
            with open(filename_txt, 'wb') as f_out:
                shutil.copyfileobj(f_in, f_out)