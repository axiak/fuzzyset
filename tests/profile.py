#!/usr/bin/python
import random
import string
import gzip
import os

import pstats, cProfile

here = os.path.dirname(__file__)

import pyximport
pyximport.install()

from cfuzzyset import cFuzzySet as FuzzySet

checks = [''.join(random.choice(string.lowercase) for _ in range(5))
          for _ in range(200)]

def run_profile():
    f = FuzzySet()
    with gzip.GzipFile(os.path.join(here, '..', 'cities.gz')) as input_file:
        for line in input_file:
            f.add(line.rstrip())
    cProfile.runctx("profiler(f)", globals(), locals(), "Profile.prof")

    s = pstats.Stats("Profile.prof")
    s.strip_dirs().sort_stats("time").print_stats()

def profiler(f):
    for val in checks:
        f.get(val)


if __name__ == '__main__':
    run_profile()
