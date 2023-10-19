# -*- coding: utf-8 -*-
"""
Created on Thu Jun  9 13:15:28 2022

Be wary of lag frames.

@author: yuhasem
"""

MAX_PRINTS = 50
MAX_SEARCHES = 10000

import rng

def PassesFilters(seed, poke, filters):
    for filter in filters:
        if not filter(poke, seed=seed):
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
        if not PassesFilters(tryseed, poke, filters):
            continue
        print("At offset", i, "found", poke)
        prints += 1
        if prints >= MAX_PRINTS:
            break
        
def ZigChadNature(zig):
    return zig.nature in (1, 3, 4)

def ZigChadAttack(zig):
    return zig.att_iv >= 22

def ZigChadSpeed(zig):
    return zig.spe_iv >= 19

def GeoDudeNature(dude):
    return dude.nature in (1, 2, 3, 4)

def GeoDudeAttack(dude):
    return dude.att_iv >= 18

def GeoDudeNature2(dude):
    return dude.nature % 5 != 0 or dude.nature == 0

def GeoDudeAttack2(dude):
    return dude.att_iv >= 29

def AronAttack(dude):
    return dude.att_iv >= 25

def AronAbility(aron):
    return aron.pid % 2 == 1

def MoonStone(lunatone, **kwargs):
    item = rng.heldItem(kwargs['seed'], lunatone, rng.METEOR_FALLS_ANIMATION, 3)
    return item[0] >= 95
        

def main():
    # Finding a chad zigzagoon for 6 pickup uptime slots
    # seed = 0x1709c8ca
    seed = 0xA6FECC9
    # FindWildPokemon(seed, 320, 94, 98, [ZigChadNature, ZigChadAttack, ZigChadSpeed])
    # print("Geodude")
    # FindWildPokemon(seed, 2880, 99, 100, [GeoDudeNature, GeoDudeAttack])
    # print("oh no")
    # FindWildPokemon(seed, 160, 99, 100, [GeoDudeNature2, GeoDudeAttack2])
    # print("Aron")
    # FindWildPokemon(seed, 160, 60, 70, [GeoDudeNature, AronAttack, AronAbility])
    FindWildPokemon(seed, 160, 70, 89, [MoonStone])

if __name__ == '__main__':
    main()
