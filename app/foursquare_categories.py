import json
from urllib.request import urlopen
from default.category import Category

CLIEND_ID = '33FG1P5NOGUXSXBBF24XJHBWLSUGLKIH2F0SSJT2F1ZS1FLE'
SECRET = '1EPSAW44U3M5PPPCCCNRUXURVGHHRHXUE2DAYM0VFE33DARZ'
CATEGORIES_URL = 'https://api.foursquare.com/v2/venues/categories'


def setup_categories():
    Category.delete_all()

    # Make an api call to get all categories
    for language in ['en', 'de', 'fr', 'it', 'ja', 'es']:
        response = urlopen('%s?client_id=%s&client_secret=%s&v=20170120&m=foursquare&locale=%s' %
                           (CATEGORIES_URL, CLIEND_ID, SECRET, language)).read()

        categories = json.loads(response, encoding='UTF-8')['response']['categories']
        save_category(parent_category_id=None, categories=categories, language=language)


def save_category(parent_category_id, categories, language):
    for category in categories:
        new_category = Category.find_by_foursquare_id(category['id'])
        if not new_category:
            # Create a new root category
            new_category = Category(foursquare_id=category['id'],
                                    foursquare_icon=category['icon']['prefix'])
            new_category.insert()
            print('Created new category %s' % new_category.uuid)

        # Update category attrs
        new_category.paren_category_uuid = parent_category_id
        setattr(new_category, 'name_%s' % language, category['name'])
        new_category.update()

        save_category(new_category.uuid, category['categories'], language)

if __name__ == '__main__':
    setup_categories()
