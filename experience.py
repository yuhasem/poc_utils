# -*- coding: utf-8 -*-
"""
Created on Sat Aug  3 14:53:22 2019

@author: yuhasem
"""

import csv

class Range():
    
    def __init__(self, mini, maxi):
        self.mini = mini
        self.maxi = maxi
        
    def __repr__(self):
        return "<" + str(self.mini) + ", " + str(self.maxi) + ">"
    
    def __len__(self):
        return self.maxi - self.mini + 1
        
    def nums(self):
        return [i for i in range(self.mini, self.maxi+1)]

class ExperienceCalculator():
    
    def __init__(self, experienceCsv=None, encounterSlotsCsv=None):
        experienceFile = open(experienceCsv)
        self.experience = self.LoadExperiencePerPokemon(experienceFile)
        encounterSlotsFile = open(encounterSlotsCsv)
        self.encounterSlots = self.LoadRouteEncounterSlots(encounterSlotsFile)
    
    def LoadExperiencePerPokemon(self, file):
        experience = dict()
        expReader = csv.reader(file)
        for row in expReader:
            if len(row) < 4:
                print('wraning: invalid row')
                continue
            experience[row[2].upper().strip()] = int(row[3])
        return experience
    
    def LoadRouteEncounterSlots(self, file):
        encounterSlots = {}
        slotsReader = csv.reader(file)
        lastName = ''
        times = 0
        for row in slotsReader:
            if row[0] == lastName:
                times += 1
                row[0] = lastName + " " + str(times)
            else:
                lastName = row[0]
                times = 0
            slots = list()
            for i in range(1, len(row), 2):
                name = row[i]
                row[i+1] = row[i+1].strip()
                try:
                    row[i+1].index('-')
                    s = row[i+1].split('-')
                    small = int(s[0])
                    large = int(s[1])
                except:
                    small = int(row[i+1])
                    large = small
                finally:
                    r = Range(small, large)
                slots.append((name, r))
            encounterSlots[row[0]] = slots
        return encounterSlots
    
    def Routes(self):
        return self.encounterSlots.keys()
        
    def ExperienceForRoute(self, route):
        slots = self.encounterSlots[route]
#        print(len(slots))
        slot_avgs = list()
        for slot in slots:
#            print(slot[0])
#            print(slot[1])
            slot_sum = 0
            for level in slot[1].nums():
                exp = self.ExperiencePerPokemon(slot[0], level)
#                print(exp)
                slot_sum += exp
            slot_avg = float(slot_sum) / len(slot[1])
            slot_avgs.append(slot_avg)
        if len(slot_avgs) == 12:
            probs = [0.2, 0.2, 0.1, 0.1, 0.1, 0.1, 0.05, 0.05, 0.04, 0.04, 0.01, 0.01]
        elif len(slot_avgs) == 5:
            probs = [0.6, 0.3, 0.05, 0.04, 0.01]
        elif len(slot_avgs) == 2:
            probs = [0.7, 0.3]
        else:
            return 0
        route_sum = 0
        for i in range(len(probs)):
            route_sum += slot_avgs[i] * probs[i]
        return route_sum
    
    def ExperiencePerPokemon(self, pokemon, level):
        base = self.experience[pokemon]
        return base * level // 7

def main():
    calc = ExperienceCalculator('pokemon_exp.csv', 'pokemon_firered_encounters_land.csv')
#    print(calc.experience)
#    for route in calc.Routes():
#        average_exp = calc.ExperienceForRoute(route)
#        print(route + ' -> ' + str(average_exp))
    avgs = [(calc.ExperienceForRoute(route), route) for route in calc.Routes()]
    avgs.sort(reverse=True)
    print(avgs)
    f = open('average_expereince.csv', 'w', newline='')
    w = csv.writer(f)
    for avg in avgs:
        w.writerow(avg)

if __name__ == '__main__':
    main()
