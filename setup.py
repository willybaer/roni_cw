#!/usr/bin/env python
import setuptools

setuptools.setup(
    name="roni_crawler",
    version="0.0.1",
    author="Wilhelm Dewald",
    author_email="Wilhelm Dewald",
    description="My Crawler project",
    long_description="long_description",
    long_description_content_type="text/markdown",
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    entry_points={
        "console_scripts": [
            "roni_migrations=app.db.migration:main",
            "test_city=tests.model.test_model_city:main",
            "test_german_locations=tests.test_german_locations:main",
            "crawl_german_locations=app.german_locations:main",
            "crawl_gelbeseiten=app.gelbeseiten:main"
        ],
    },
)
