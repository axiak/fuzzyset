#!/usr/bin/python
import os
import gzip

here = os.path.dirname(__file__)

try:
    from cfuzzyset import cFuzzySet as FuzzySet
except ImportError:
    from fuzzyset import FuzzySet


def _interactive_test():
    with gzip.GzipFile(os.path.join(here, '..', 'cities.gz')) as input_file:
        f = FuzzySet((line.strip() for line in input_file))
    while True:
        town = raw_input("Enter town name: ")
        print f.get(town)

if __name__ == '__main__':
    _interactive_test()
