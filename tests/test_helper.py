import unittest
import getopt
import json
import sys

from app.db.helper import levenshtein_distance

class TestModelLocation(unittest.TestCase):

    def test_levenshtein_distance(self):
        distance = levenshtein_distance(source='Berlin-mitte', target='mitte')        
        self.assertEquals(distance, 2)


def main():
    unittest.main()

if __name__ == '__main__':
    main()