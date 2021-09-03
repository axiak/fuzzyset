import os
import sys
import platform

here = os.path.dirname(__file__)


def read(fname):
    return open(os.path.join(os.path.dirname(__file__), fname)).read()


extra_kwargs = {}
ext_files = []

__version__ = "Undefined"
with open("fuzzyset/__init__.py") as fh:
    for line in fh:
        if line.startswith("__version__"):
            exec(line.strip())

if platform.python_implementation() != 'CPython':
    sys.argv.append('--pure-python')

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
    name="fuzzyset2",
    version=__version__,
    author="Michael Axiak, Adrian Altenhoff",
    author_email="adrian.altenhoff@inf.ethz.ch",
    description=("A simple python fuzzyset implementation."),
    license="BSD",
    keywords="fuzzyset fuzzy data structure",
    url="https://github.com/alpae/fuzzyset/",
    packages=['fuzzyset'],
    long_description=read('README.rst'),
    long_description_content_type="text/x-rst",
    install_requires=['python-levenshtein'],
    test_require=["texttable", "pytest"],
    classifiers=[
        "Development Status :: 3 - Alpha",
        "License :: OSI Approved :: BSD License",
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Topic :: Software Development :: Libraries',
    ],
    **extra_kwargs
)
