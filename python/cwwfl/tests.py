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
        self.fs1 = fuzzyset.CreateFuzzySet(mf=fuzzyset.TriangularMf(-1,1,0))
        self.fs2 = fuzzyset.CreateFuzzySet(mf=fuzzyset.TriangularMf(0,3,2))
    def test_inheritance(self):
        self.assertTrue(issubclass(fuzzyset.TriangularFs,Real))
        pass
    def test_type(self):
        self.assertTrue(isinstance(self.fs1, fuzzyset.FuzzySet))
        self.assertTrue(isinstance(self.fs1, fuzzyset.TriangularFs))
    def test_values(self):
        self.assertEquals(self.fs1(0),1)
        self.assertEquals(self.fs1(1),0)
        self.assertEquals(self.fs1(-1),0)
        self.assertEquals(self.fs1(-.5),.5)
        self.assertEquals(self.fs1(.25),.75)

        self.assertEquals(self.fs2(0),0)
        self.assertEquals(self.fs2(3),0)
        self.assertEquals(self.fs2(2),1)
        self.assertEquals(self.fs2(1),.5)
        self.assertEquals(self.fs2(2.5),.5)
        self.assertEquals(self.fs2("bunk"),0)
        



setupsuite = unittest.TestLoader().loadTestsFromTestCase(TestFuzzySetSetup)
triangularsuite = unittest.TestLoader().loadTestsFromTestCase(TestTriangularFs)
suite = unittest.TestSuite([setupsuite,triangularsuite])
unittest.TextTestRunner(verbosity=2).run(suite)
#suite = unittest.TestLoader().loadTestsFromTestCase(TestTriangularFs)
#unittest.TextTestRunner(verbosity=2).run(suite)

# if __name__ == '__main__':
#     unittest.main()
