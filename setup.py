#!/usr/bin/env python
import setuptools

setuptools.setup(
    name="ronicrawlergermany",
    version="0.0.1",
    author="Wilhelm Dewald",
    author_email="Wilhelm Dewald",
    description="Crawling stuff for the country germany",
    long_description_content_type="text/markdown",
    packages=setuptools.find_packages(),
    entry_points={
        "console_scripts": [
            "crawl_german_locations=app.german_locations:main",
            "crawl_gelbeseiten=app.gelbeseiten_main:main"
        ],
    },
    install_requires=[
        'roniutils',
        'ronidatabase',
        'roniscrapper'
        ]
)
