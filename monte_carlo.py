# -*- coding: utf-8 -*-
"""
Created on Fri Jul 19 19:38:55 2019

@author: yuhasem
"""

import random

LOOP = 10000000  # 10 million
SEARCH_EVERY = 3
PARTY_SIZE = 4

class Pickup():
    
    def __init__(self):
        self.item = ""
        
    def gen_new_item(self):
        if self.item != "":
            return
        rand = random.random()
        if rand < 0.3:
            self.item = "Super Potion"
        elif rand < 0.4:
            self.item = "Ultra Ball"
        elif rand < 0.5:
            self.item = "Full Restore"
        elif rand < 0.6:
            self.item = "Full Heal"
        elif rand < 0.7:
            self.item = "Nugget"
        elif rand < 0.8:
            self.item = "Revive"
        elif rand < 0.9:
            self.item = "Rare Candy"
        elif rand < 0.95:
            self.item = "Protein"
        elif rand < 0.99:
            self.item = "PP Up"
        else:
            self.item = "King's Rock"

    def reset(self):
        self.item = ""

def main():
    candies = 0
    team = []
    for i in range(PARTY_SIZE):
        team.append(Pickup())
    for i in range(LOOP):
        for pickup in team:
            if random.random() < 0.1:
                pickup.gen_new_item()
        if i % SEARCH_EVERY == 0:
            for pickup in team:
                if pickup.item == "Rare Candy":
                    candies += 1
                pickup.reset()
    print("Final Rare Candies = ", candies)
    print("loops = ", LOOP)
    print("search every = ", SEARCH_EVERY)

if __name__ == '__main__':
    main()
