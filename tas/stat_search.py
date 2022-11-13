# -*- coding: utf-8 -*-
"""
Created on Thu Jun  9 13:15:28 2022

Be wary of lag frames.

@author: yuhasem
"""

MAX_PRINTS = 200
MAX_SEARCHES = 100000

import rng

def PassesFilters(poke, filters):
    for filter in filters:
        if not filter(poke):
            return False
    return True

def FindWildPokemon(seed, density, min_slot, max_slot, filters=[]):
    prints = 0
    for i in range(MAX_SEARCHES):
        tryseed = rng.advanceRng(seed, i)
        if rng.top(tryseed) % 2880 >= density:
            continue
        tryseed = rng.advanceRng(tryseed, 1)
        if (rng.top(tryseed) % 100 < min_slot
            or rng.top(tryseed) % 100 >= max_slot):
            continue
        poke = rng.WildPokemon(tryseed)
        if not PassesFilters(poke, filters):
            continue
        print("At offset", i, "found", poke)
        prints += 1
        if prints >= MAX_PRINTS:
            break
        
def ZigChadNature(zig):
    if zig.nature in (1, 3, 4):
        return True
    return False

def ZigChadAttack(zig):
    if zig.att_iv >= 22:
        return True
    return False

def ZigChadSpeed(zig):
    if zig.spe_iv >= 19:
        return True
    return False

def GeoDudeNature(dude):
    if dude.nature in (1, 2, 3, 4):
        return True
    return False

def GeoDudeAttack(dude):
    if dude.att_iv >= 28:
        return True
    return False

def AronAttack(dude):
    if dude.att_iv >= 31:
        return True
    return False
        

def main():
    # Finding a chad zigzagoon for 6 pickup uptime slots
    # seed = 0x1709c8ca
    seed = 0xc4ce3f43
    # FindWildPokemon(seed, 320, 94, 98, [ZigChadNature, ZigChadAttack, ZigChadSpeed])
    print("Geodude")
    FindWildPokemon(seed, 160, 99, 100, [GeoDudeNature, GeoDudeAttack])
    print("Aron")
    FindWildPokemon(seed, 160, 60, 70, [GeoDudeNature, AronAttack])

if __name__ == '__main__':
    main()
