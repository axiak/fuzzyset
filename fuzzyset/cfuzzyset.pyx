# encoding: utf-8

import re
import math
import cython
import collections
import Levenshtein

__version__ = (0, 0, 2)

from libc.math cimport sqrt

cdef _non_word_re = re.compile(r'[^\w, ]+')

cdef class cFuzzySet:
    " Fuzzily match a string "

    cdef set exact_set
    cdef dict match_dict
    cdef dict items
    cdef int gram_size_lower
    cdef int gram_size_upper
    cdef int use_levenshtein

    def __cinit__(self, iterable=(), int gram_size_lower=2, int gram_size_upper=3, int use_levenshtein=True):
        assert gram_size_upper < 4 and gram_size_upper > 0
        assert gram_size_lower < 4 and gram_size_lower > 0
        assert gram_size_lower <= gram_size_upper
        self.exact_set = set()
        self.match_dict = {}
        self.items = {}
        cdef int i
        for i in range(gram_size_lower, gram_size_upper + 1):
            self.items[i] = []
        self.gram_size_lower = gram_size_lower
        self.gram_size_upper = gram_size_upper
        self.use_levenshtein = use_levenshtein
        for value in iterable:
            self.add(value)

    def add(self, object in_val):
        value = _convert_val(in_val)
        with cython.nonecheck(True):
            value = value.lower()
        if value in self.exact_set:
            return
        cdef int i
        for i in range(self.gram_size_lower, self.gram_size_upper + 1):
            self._add(value, i)

    @cython.nonecheck(False)
    cpdef _add(self, unicode value, int gram_size):
        cdef list items = self.items[gram_size]
        cdef int idx = len(items)
        items.append(0)
        cdef dict grams = _gram_counter(value, gram_size)
        cdef double total = 0
        cdef int i
        cdef int tmp
        cdef list values = grams.values()
        with cython.boundscheck(False):
            for i in range(len(values)):
                tmp = values[i]
                total += tmp * tmp
        cdef double norm = sqrt(total)
        items[idx] = (norm, value)
        cdef tuple new_val
        for gram, occ in grams.items():
            new_val = (idx, occ)
            if gram in self.match_dict:
                self.match_dict[gram].append(new_val)
            else:
                self.match_dict[gram] = [new_val]
        self.exact_set.add(value)

    @cython.nonecheck(False)
    @cython.boundscheck(False)
    def __getitem__(self, object in_val):
        cdef unicode value = _convert_val(in_val)
        with cython.nonecheck(True):
            value = value.lower()
        if value in self.exact_set:
            return [(1, value)]
        cdef int i
        results = None
        for i in range(self.gram_size_upper, self.gram_size_lower - 1, -1):
            results = self._get(value, i)
            if results is not None:
                return results
        raise KeyError(in_val)

    @cython.nonecheck(False)
    @cython.boundscheck(False)
    cpdef _get(self, unicode value, int gram_size):
        cdef dict matches = {}
        cdef dict grams = _gram_counter(value, gram_size)
        cdef double norm = 0
        cdef int tmp
        cdef list values = grams.values()
        for tmp in values:
            norm += tmp * tmp
        norm = sqrt(norm)
        cdef int idx
        cdef int other_occ
        cdef int occ
        cdef int match_score
        cdef unicode gram
        cdef list items = self.items[gram_size]

        for gram, occ in grams.items():
            if gram in self.match_dict:
                for idx, other_occ in self.match_dict[gram]:
                    if idx in matches:
                        matches[idx] += occ * other_occ
                    else:
                        matches[idx] = occ * other_occ

        if not matches:
            return None

        # cosine similarity
        cdef list results = [(match_score / items[idx][0], items[idx][1])
                             for idx, match_score in matches.items()]
        results.sort(reverse=True)

        if self.use_levenshtein:
            results = [(distance(matched, value), matched)
                       for _, matched in results[:50]]
            results.sort(reverse=True)

            return [result for result in results
                    if result[0] == results[0][0]]
        else:
            return [(score / norm, value)
                    for score, value in results
                    if score == results[0][0]]

    def get(self, object key, object default=None):
        try:
            return self[key]
        except KeyError:
            return default

@cython.boundscheck(False)
cdef dict _gram_counter(unicode value, int gram_size=2):
    cdef dict results = {}
    cdef list grams = _iterate_grams(value, gram_size)
    cdef unicode gram
    cdef int i
    for i in range(len(grams)):
        gram = grams[i]
        if gram not in results:
            results[gram] = 1
        else:
            results[gram] += 1
    return results

cdef unicode hyphens = u'-----------'

cdef list _iterate_grams(unicode value, int gram_size=2):
    cdef unicode simplified = u'-' + _non_word_re.sub('', value) + u'-'
    cdef int len_diff = gram_size - len(simplified)
    cdef list result = []
    with cython.boundscheck(False):
        if len_diff > 0:
            value += hyphens[:len_diff]
    cdef int iterations = len(simplified) - gram_size + 1
    cdef int i
    with cython.boundscheck(False):
        for i in range(iterations):
            result.append(simplified[i:i + gram_size])
    return result

cdef unicode _convert_val(object value):
    if isinstance(value, unicode):
        return value
    elif isinstance(value, str):
        return unicode(value)
    else:
        raise TypeError("Expecting string or unicode, received " + value)

cdef double distance(unicode str1, unicode str2):
    cdef double result = Levenshtein.distance(str1, str2)
    if len(str1) > len(str2):
        return 1 - result / len(str1)
    else:
        return 1 - result / len(str2)
