#!/usr/bin/python

import unittest
import fuzzyset
from numbers import Real

class TestFuzzySetSetup(unittest.TestCase):
    def test_type_directInstantiation(self):
        fs = fuzzyset.FuzzySet() 
        self.assertTrue(isinstance(fs, fuzzyset.FuzzySet))
    def test_type_factoryMethod(self):
        #must give parameters to create a fuzzy set
        self.assertRaises(ValueError, fuzzyset.CreateFuzzySet) 
        fs = fuzzyset.CreateFuzzySet(mf=fuzzyset.TriangularMf(-1,0,1))
        self.assertTrue(isinstance(fs, fuzzyset.FuzzySet))
    def test_inheritance(self):
        self.assertTrue(issubclass(fuzzyset.TriangularFs,Real))
        pass
class TestTriangularFs(unittest.TestCase):
    def setUp(self):
        self.fs = fuzzyset.CreateFuzzySet(mf=fuzzyset.TriangularMf(-1,1,0))
    def test_inheritance(self):
        self.assertTrue(issubclass(fuzzyset.TriangularFs,Real))
        pass
    def test_type(self):
        self.assertTrue(isinstance(self.fs, fuzzyset.FuzzySet))
        self.assertTrue(isinstance(self.fs, fuzzyset.TriangularFs))
    def test_values(self):
        self.assertEquals(self.fs(0),1)
        self.assertEquals(self.fs(1),0)
        self.assertEquals(self.fs(-1),0)
        self.assertEquals(self.fs(-.5),.5)
        self.assertEquals(self.fs(.25),.75)

setupsuite = unittest.TestLoader().loadTestsFromTestCase(TestFuzzySetSetup)
triangularsuite = unittest.TestLoader().loadTestsFromTestCase(TestTriangularFs)
suite = unittest.TestSuite([setupsuite,triangularsuite])
unittest.TextTestRunner(verbosity=2).run(suite)
#suite = unittest.TestLoader().loadTestsFromTestCase(TestTriangularFs)
#unittest.TextTestRunner(verbosity=2).run(suite)

# if __name__ == '__main__':
#     unittest.main()
