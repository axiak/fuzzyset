import re
import math
import collections

_non_word_re = re.compile(r'[^\w, ]+')

__all__ = ('FuzzySet',)

class FuzzySet(object):
    " Fuzzily match a string "
    def __init__(self, iterable=(), gram_size=2):
        self.exact_set = set()
        self.match_dict = collections.defaultdict(list)
        self.items = []
        self.gram_size = gram_size
        for value in iterable:
            self.add(value)

    def add(self, value):
        value = value.lower()
        if value in self.exact_set:
            return False
        idx = len(self.items)
        self.items.append(0)
        grams = _gram_counter(value, self.gram_size)
        norm = math.sqrt(sum(x**2 for x in grams.values()))
        for gram, occ in grams.items():
            self.match_dict[gram].append((idx, occ))
        self.items[idx] = (norm, value)
        self.exact_set.add(value)

    def __getitem__(self, value):
        value = value.lower()
        if value in self.exact_set:
            return value
        matches = collections.defaultdict(float)
        grams = _gram_counter(value, self.gram_size)
        norm = math.sqrt(sum(x**2 for x in grams.values()))

        for gram, occ in grams.items():
            for idx, other_occ in self.match_dict.get(gram, ()):
                matches[idx] += occ * other_occ
        # cosine similarity
        results = [(match_score / (norm * self.items[idx][0]), self.items[idx][1])
                   for idx, match_score in matches.items()]
        results.sort(reverse=True)
        if results:
            return [result for result in results
                    if result[0] == results[0][0]]
        else:
            raise KeyError(value)

    def get(self, key, default=None):
        try:
            return self[key]
        except KeyError:
            return default

def _gram_counter(value, gram_size=2):
    return collections.Counter(_iterate_grams(value, gram_size))

def _iterate_grams(value, gram_size=2):
    simplified = '-' + _non_word_re.sub('', value.lower()) + '-'
    len_diff = gram_size - len(simplified)
    if len_diff > 0:
        value += '-' * len_diff
    for i in range(len(simplified) - gram_size + 1):
        yield simplified[i:i + gram_size]

if __name__ == '__main__':
    with open('./cities') as input_file:
        f = FuzzySet((line.strip() for line in input_file), gram_size=2)

    while False:
        town = raw_input("Enter town name: ")
        print f[town]

    with open('./origin_cities') as cities:
        for line in cities:
            result = f.get(line.strip())
            if result is None:
                print "{}: Could not find".format(line.strip())
            elif isinstance(result, list):
                print "{}: {}".format(line.strip(), result)
