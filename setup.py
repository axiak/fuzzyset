import os
import sys
import platform

here = os.path.dirname(__file__)

def read(fname):
    return open(os.path.join(os.path.dirname(__file__), fname)).read()

#if sys.version_info[0] < 3 and sys.version_info[1] < 7:
#    requirements.append('importlib')

extra_kwargs = {}

ext_files = []

if platform.python_implementation() != 'CPython':
    sys.argv.append('--pure-python')

if '--pure-python' not in sys.argv:
    try:
        import Cython
    except ImportError:
        pass

from setuptools import setup, Extension

if '--pure-python' not in sys.argv and 'sdist' not in sys.argv:
    try:
        from Cython.Distutils import build_ext
        ext_files.append('fuzzyset/cfuzzyset.pyx')
        extra_kwargs['cmdclass'] = {'build_ext': build_ext}
        try:
            os.unlink(os.path.join(here, 'fuzzyset', 'cfuzzyset.c'))
            os.unlink(os.path.join(here, 'cfuzzyset.so'))
        except:
            pass
    except ImportError:
        Cython = None
        ext_files.append('fuzzyset/cfuzzyset.c')
        if '--cython' in sys.argv:
            raise
    extra_kwargs['ext_modules'] = [Extension('cfuzzyset', ext_files)]
elif '--pure-python' in sys.argv:
    sys.argv.remove('--pure-python')

if '--cython' in sys.argv:
    sys.argv.remove('--cython')

setup(
    name = "fuzzyset",
    version = "0.0.14",
    author = "Michael Axiak",
    author_email = "mike@axiak.net",
    description = ("A simple python fuzzyset implementation."),
    license = "BSD",
    keywords = "fuzzyset fuzzy data structure",
    url = "https://github.com/axiak/fuzzyset/",
    packages=['fuzzyset'],
    long_description=read('README.rst'),
    install_requires=['python-levenshtein', 'texttable'],
    classifiers=[
        "Development Status :: 3 - Alpha",
        "License :: OSI Approved :: BSD License",
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Topic :: Software Development :: Libraries',
    ],
    **extra_kwargs
)
