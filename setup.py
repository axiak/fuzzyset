import os
from setuptools import setup

def read(fname):
    return open(os.path.join(os.path.dirname(__file__), fname)).read()

setup(
    name = "fuzzyset",
    version = "0.0.1",
    author = "Michael Axiak",
    author_email = "mike@axiak.net",
    description = ("A simple python fuzzyset implementation."),
    license = "BSD",
    keywords = "fuzzyset fuzzy data structure",
    url = "https://github.com/axiak/fuzzyset/",
    packages=['fuzzyset'],
    long_description=read('README.rst'),
    classifiers=[
        "Development Status :: 3 - Alpha",
        "License :: OSI Approved :: BSD License",
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Topic :: Software Development :: Libraries',
    ],
)
