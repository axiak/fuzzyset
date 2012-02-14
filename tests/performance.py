#!/usr/bin/python
import os
import gzip
import timeit
import random
import texttable

here = os.path.dirname(__file__)

import fuzzyset
import cfuzzyset

test_data = [[], 0]

def run_tests():
    print 'Building data structures...'
    structures = build_structures()
    results = {}
    names = {}
    for varname, name, obj in structures:
        globals()[varname] = obj
        results[varname] = []
        names[varname] = name
    lengths = (3, 6, 10, 15, 25, 50)
    num_tests = 5000
    print 'Starting the timing tests...'
    for length in lengths:
        test_data_l = [None] * num_tests
        test_data[0] = test_data_l
        test_data[1] = 0
        for i in range(num_tests):
            test_data_l[i] = ''.join(random.choice(string) for _ in range(length))
        globals()['length'] = length
        for varname, name, obj in structures:
            t = timeit.Timer('test(length, {0}, test_data)'.format(varname),
                             'from __main__ import length, test, {0}, test_data'.format(varname))
            results[varname].append(t.timeit(number=num_tests))

    table = texttable.Texttable()
    if len(structures) <= len(lengths):
        table.add_rows([['Input length'] + [name for _, name, _ in structures]]
                       +
                       [[length] + [results[varname][i] / num_tests for varname, _, _ in structures]
                        for i, length in enumerate(lengths)])
    else:
        table.add_rows([['Structure'] + ['{0} chars'.format(l) for l in lengths]]
                       +
                       [[name] + [results[varname][i] / num_tests for i, length in enumerate(lengths)]
                        for varname, name, _ in structures])

    print table.draw()

string = 'abcdefghjijklmnopqrstuvwxyz'

def test(length, obj, test_data):
    data, test_num = test_data
    obj.get(data[test_num])
    test_num += 1

def build_structures():
    opts = (
        ('a', 'FuzzySet', fuzzyset.FuzzySet()),
        ('b', 'FuzzySet (no leven)', fuzzyset.FuzzySet()),
        ('c', 'cFuzzySet', cfuzzyset.cFuzzySet()),
        ('d', 'cFuzzySet (no leven)', cfuzzyset.cFuzzySet()),
        )
    ref = {}
    with gzip.GzipFile(os.path.join(here, '..', 'cities.gz')) as input_file:
        for line in input_file:
            line = line.rstrip()
            for _, _, structure in opts:
                structure.add(line)
            ref[line] = line

    return opts + (('ref', 'reference (dict)', ref),)


if __name__ == '__main__':
    run_tests()
