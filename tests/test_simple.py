import os.path
import gzip
import unittest
import Levenshtein
from fuzzyset import FuzzySet
from cfuzzyset import cFuzzySet


def load_cities():
    with gzip.open(os.path.join(os.path.dirname(__file__), '..', 'cities.gz'), 'rb') as fh:
        for line in fh:
            yield line.decode().strip()


class FuzzySetTests(unittest.TestCase):
    impl = FuzzySet

    def test_simple_fuzzyset(self):
        f = self.impl(["New York", "New Jersey", "Los Angeles"])
        f.add("New Braunfels")
        self.assertIn("New York", [x[1] for x in f.get("ew Kork")])
        self.assertNotIn("New York", [x[1] for x in f.get("ew Braun")])
        self.assertIn("New Braunfels", [x[1] for x in f.get("ew Braun")])

    def test_sim_cutoff_size(self):
        f = self.impl(load_cities(), rel_sim_cutoff=.9)
        query = "Steemboot Sprints"
        res = f.get(query)
        self.assertGreaterEqual(2, len(res))
        self.assertGreaterEqual(res[-1][0], 0.9*res[0][0])
        for x in res:
            self.assertAlmostEqual(x[0], 1-(Levenshtein.distance(query, x[1])/max(len(query), len(x[1]))))


class CFuzzySetTests(FuzzySetTests):
    impl = cFuzzySet


if __name__ == '__main__':
    unittest.main()
