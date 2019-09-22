# -*- coding: utf-8 -*-
"""
Created on Sun Sep 22 09:17:50 2019

@author: yuhasem
"""

import unittest
import experience

import csv
import os

class ExperienceTest(unittest.TestCase):
    
    @classmethod
    def setUpClass(cls):
        """Test data is written in setup class so that it only needs to be done
        once.  These values should not be modified by the execution of anything
        withing experience.py."""
        f = open('test_exp.csv', 'w', newline='')
        w = csv.writer(f)
        w.writerow(['unused', 'unused', 'Cleese', '6'])
        w.writerow(['unsued', 'unused', 'Idle', '7'])
        w.writerow(['unused', 'unsued', 'Chapman', '8', 'unused'])
        f = open('test_slots.csv', 'w', newline='')
        w = csv.writer(f)
        w.writerow(['The Bruce Sketch', 'CLEESE', '1', 'CLEESE', '2'])
        w.writerow(['The Argument Sketch', 'CLEESE', '1', 'CLEESE', '1', 'IDLE', '5', 'CHAPMAN', '5', 'IDLE', '5'])
        w.writerow(['The Chemist Sketch', 'CLEESE', '7', 'CLEESE', '7', 'IDLE', '7', 'IDLE', '7', 'IDLE', '7', 'IDLE', '7', 'CHAPMAN', '7', 'CHAPMAN', '7', 'CLEESE', '7', 'CLEESE', '7', 'IDLE', '7', 'IDLE', '7'])
        w.writerow(['The Architect Sketch', 'CLEESE', '1', 'NONAME', '1'])
        w.writerow(['The Dead Parrot Sketch', 'CLEESE', '1', 'CLEESE', '1', 'CLEESE', '1'])
        w.writerow(['The Cheese Shop Sketch', 'CLEESE', '5-10', 'CLEESE', '5-10'])
        w.writerow(['Biggus Dickus', 'CLEESE', ' 5-10', 'CLEESE', ' 5-10'])
        w.writerow(['Same Name', 'CLEESE', '1', 'CLEESE', '2'])
        w.writerow(['Same Name', 'CLEESE', '2', 'CLEESE', '2'])
        
    @classmethod
    def tearDownClass(cls):
        os.remove('test_exp.csv')
        os.remove('test_slots.csv')
    
    def setUp(self):
        self.calc = experience.ExperienceCalculator('test_exp.csv', 'test_slots.csv')
    
    def testExperiencePerPokemon(self):
        self.assertEqual(self.calc.ExperiencePerPokemon('CLEESE', 7), 6)
        self.assertEqual(self.calc.ExperiencePerPokemon('CLEESE', 1), 0)
        self.assertEqual(self.calc.ExperiencePerPokemon('IDLE', 1), 1)
        self.assertEqual(self.calc.ExperiencePerPokemon('CHAPMAN', 1), 1)
    
    def testRoutes(self):
        routes = self.calc.Routes()
        self.assertIn('The Bruce Sketch', routes)
        self.assertIn('Same Name', routes)
        self.assertIn('Same Name 1', routes)
    
    def testAverageExperienceWithTwoSlots(self):
        self.assertAlmostEqual(self.calc.ExperienceForRoute('The Bruce Sketch'), 0.3)
    
    def testAverageExperienceWithFiveSlots(self):
        self.assertAlmostEqual(self.calc.ExperienceForRoute('The Argument Sketch'), 0.5)
    
    def testAverageExperienceWithTwelveSlots(self):
        self.assertAlmostEqual(self.calc.ExperienceForRoute('The Chemist Sketch'), 6.62)
    
    def testAverageExperienceWithInvalidSlot(self):
        self.assertRaises(KeyError, self.calc.ExperienceForRoute, 'The Architect Sketch')
    
    def testAverageExperienceWithInvalidNumberOfSlots(self):
        self.assertEqual(self.calc.ExperienceForRoute('The Dead Parrot Sketch'), 0)
    
    def testAverageExperienceWithInvalidRouteName(self):
        self.assertRaises(KeyError, self.calc.ExperienceForRoute, 'Philosophers World Cup')
    
    def testAverageExperienceWithLevelRanges(self):
        self.assertAlmostEqual(self.calc.ExperienceForRoute('The Cheese Shop Sketch'), 6.0)
    
    def testAverageExperienceWithSpacesInLevelRange(self):
        # This test exists because Excel is dumb and tries to interpret XX-XX
        # as a date all the time, even when you tell it not to. As a result
        # some of the values have a space in front of them.
        self.assertAlmostEqual(self.calc.ExperienceForRoute('The Cheese Shop Sketch'), 6.0)
    
    def testAverageExperienceSameNameRoutesDoNotInterfere(self):
        self.assertAlmostEqual(self.calc.ExperienceForRoute('Same Name'), 0.3)
        self.assertAlmostEqual(self.calc.ExperienceForRoute('Same Name 1'), 1.0)

if __name__ == '__main__':
    unittest.main()