import re
import math
import collections
import Levenshtein

__version__ = (0, 0, 3)

_non_word_re = re.compile(r'[^\w, ]+')

__all__ = ('FuzzySet',)

class FuzzySet(object):
    " Fuzzily match a string "
    def __init__(self, iterable=(), gram_size_lower=2, gram_size_upper=3, use_levenshtein=True):
        self.exact_set = set()
        self.match_dict = collections.defaultdict(list)
        self.items = {}
        self.use_levenshtein = use_levenshtein
        self.gram_size_lower = gram_size_lower
        self.gram_size_upper = gram_size_upper
        for i in range(gram_size_lower, gram_size_upper + 1):
            self.items[i] = []
        for value in iterable:
            self.add(value)

    def add(self, value):
        value = value.lower()
        if value in self.exact_set:
            return False
        for i in range(self.gram_size_lower, self.gram_size_upper + 1):
            self.__add(value, i)

    def __add(self, value, gram_size):
        items = self.items[gram_size]
        idx = len(items)
        items.append(0)
        grams = _gram_counter(value, gram_size)
        norm = math.sqrt(sum(x**2 for x in grams.values()))
        for gram, occ in grams.items():
            self.match_dict[gram].append((idx, occ))
        items[idx] = (norm, value)
        self.exact_set.add(value)

    def __getitem__(self, value):
        value = value.lower()
        if value in self.exact_set:
            return [(1, value)]
        for i in range(self.gram_size_upper, self.gram_size_lower - 1, -1):
            results = self.__get(value, i)
            if results is not None:
                return results
        raise KeyError(value)

    def __get(self, value, gram_size):
        matches = collections.defaultdict(float)
        grams = _gram_counter(value, gram_size)
        items = self.items[gram_size]
        norm = math.sqrt(sum(x**2 for x in grams.values()))

        for gram, occ in grams.items():
            for idx, other_occ in self.match_dict.get(gram, ()):
                matches[idx] += occ * other_occ

        if not matches:
            return None

        # cosine similarity
        results = [(match_score / (norm * items[idx][0]), items[idx][1])
                   for idx, match_score in matches.items()]
        results.sort(reverse=True)

        if self.use_levenshtein:
            results = [(_distance(matched, value), matched)
                       for _, matched in results[:50]]
            results.sort(reverse=True)

        return [result for result in results
                if result[0] == results[0][0]]


    def get(self, key, default=None):
        try:
            return self[key]
        except KeyError:
            return default

def _distance(str1, str2):
    distance = Levenshtein.distance(str1, str2)
    if len(str1) > len(str2):
        return 1 - float(distance) / len(str1)
    else:
        return 1 - float(distance) / len(str2)

def _gram_counter(value, gram_size=2):
    return collections.Counter(_iterate_grams(value, gram_size))

def _iterate_grams(value, gram_size=2):
    simplified = '-' + _non_word_re.sub('', value.lower()) + '-'
    len_diff = gram_size - len(simplified)
    if len_diff > 0:
        value += '-' * len_diff
    for i in range(len(simplified) - gram_size + 1):
        yield simplified[i:i + gram_size]

def _other_test():
    with open('./origin_cities') as cities:
        for line in cities:
            result = f.get(line.strip())
            if result is None:
                print "{}: Could not find".format(line.strip())
            elif isinstance(result, list):
                print "{}: {}".format(line.strip(), result)

if __name__ == '__main__':
    pass
    #_other_test()
