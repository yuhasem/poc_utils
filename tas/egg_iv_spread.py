# -*- coding: utf-8 -*-
"""
Created on Sat Dec  6 06:47:53 2025

@author: hando
"""

import random

# Based on https://bulbapedia.bulbagarden.net/wiki/Pok%C3%A9mon_breeding#Inheriting_stats

# Order: HP, ATK, DEF, SPA, SPD, SPE
MOTHER = [0, 15, 24, 29, 24, 8]
FATHER = [12, 29, 22, 13, 4, 6]

EGGS = 100000000

def egg(mother, father):
    inherited = [False, False, False, False, False, False]
    egg = [0, 0, 0, 0, 0, 0]
    # First IV is inherited from either parent, and any IV
    parent = mother
    if random.random() < 0.5:
        parent = father
    stat_index = random.randint(0, 5)
    egg[stat_index] = parent[stat_index]
    inherited[stat_index] = True
    # Second IV is inherited from either parent, and any IV except HP
    parent = mother
    if random.random() < 0.5:
        parent = father
    stat_index = random.randint(1, 5)
    egg[stat_index] = parent[stat_index]
    inherited[stat_index] = True
    # Third IV is inerited from either parent, and an IV except HP or DEF
    parent = mother
    if random.random() < 0.5:
        parent = father
    stat_index = random.randint(1, 4)
    if (stat_index != 1):
        stat_index += 1
    egg[stat_index] = parent[stat_index]
    inherited[stat_index] = True
    # Uninherited IVs are determined at random
    for i in range(len(inherited)):
        if not inherited[i]:
            egg[i] = random.randint(0, 31)
    return egg

def main():
    ivs = [0 for _ in range(187)]
    for i in range(EGGS):
        e = egg(MOTHER, FATHER)
        ivsum = 0
        for j in e:
            ivsum += j
        ivs[ivsum] += 1
    for i in range(len(ivs)):
        print(f'{i}\t{ivs[i]}')

if __name__ == '__main__':
    main()
