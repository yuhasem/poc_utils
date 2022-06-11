# -*- coding: utf-8 -*-
"""
Created on Tue May 24 06:32:01 2022

@author: yuhasem
"""

import rng
import math

# function calculateAttack(attackBase, level, iv, nature, ev) {
#   return Math.floor((Math.floor((2*attackBase+iv+Math.floor(ev/4))*level/100)+5)*nature);
# }

# function calculateDamage(moveBasePower, attackBase, defense, level, iv, nature, ev, crit, roll, typeMultiplier, stab, guts, purePower) {
#   var attack = calculateAttack(attackBase, level, iv, nature, ev);
#   return Math.floor((Math.floor(2*level/5 + 2)*moveBasePower*(attack*guts*purePower)/defense)/50 + 2)*crit*roll*typeMultiplier*stab;
# }

def ZigAttack(iv, nature):
    return math.floor((math.floor((60+iv)*7/100)+5)*nature)

def RaltsDefense(iv, nature):
    return math.floor((math.floor((50+iv)*5/100)+5)*nature)

def RaltsHealth(iv):
    return math.floor((56+iv)*5/100)+15

def WallyDamage(attack, defense):
    return math.floor(math.floor(math.floor(140*attack/defense)/50 + 2)*1.5)  # Assumes max roll

def FastWally(seed):
    # Generate Zigzagoon
    zig = rng.StaticPokemon(seed)
    if zig.att_iv <= 12:
        # Early exit because at this point it's impossible
        return False
    zig_nature = 1  # considering only the nature's influence on attack
    if zig.nature >= 0 and zig.nature < 5:
        zig_nature += 0.1
    if zig.nature % 5 == 0:
        zig_nature -= 0.1
    zig_attack = ZigAttack(zig.att_iv, zig_nature)
    # Advances burned generating the zig
    seed = rng.advanceRng(seed, 5)
    # There are at least 651 frames between the zig gen and the ralts gen.
    seed = rng.advanceRng(seed, 651)
    # Within 120 frames (2 seconds), generate Ralts
    for i in range(120):
        tryseed = rng.advanceRng(seed, i)
        ralts = rng.WallyRaltsPokemon(tryseed)
        ralts_nature = 1  # considering only the nature's influence on defense
        if ralts.nature >= 5 and ralts.nature < 10:
            ralts_nature += 0.1
        if ralts.nature % 5 == 1:
            ralts_nature -= 0.1
        ralts_def = RaltsDefense(ralts.def_iv, ralts_nature)
        damage1 = WallyDamage(zig_attack, ralts_def)
        damage2 = WallyDamage(math.floor(2*zig_attack/3), ralts_def)
        if (damage1 + damage2 >= RaltsHealth(ralts.hp_iv)):
            print("zig:", zig.att_iv, zig_nature)
            print("ralts:", ralts.def_iv, ralts.hp_iv, ralts_nature)
            print("second frame offset:", i)
            return True
    return False

class Event():
    
    def __init__(self, name, offset, duration, occurs, weight = 100, must_happen = False):
        self.name = name
        self.first_offset = offset
        self.duration = duration
        self.occurs = occurs  # func(seed) -> bool
        self.weight = weight
        self.must_happen = must_happen

def main():
    seed = 0xF9B2
    # Accounting for Poochy need a later frame
    seed = rng.advanceRng(seed, 59600)
    for i in range(2000):
        tryseed = rng.advanceRng(seed, i)
        if (FastWally(tryseed)):
            print("Fast Wally at seed", seed, " offset:", i, "+59600")
    # for seed in range(1 << 16):
    #     # The starting RNG seeds in RSE are always of the form 0x0000XXXX where
    #     # the last 16 bits is determined by the date. So here we're searching
    #     # all possible starting seeds for ones that give access to good events
    #     # early on.
    #     # Earliest we can get to the Pickup determination of the Calvin fight.
    #     calvin_seed = rng.advanceRng(seed, 43000)
    #     candies = 0
    #     for i in range(600):
    #         # May involve parity shifting the fight, but should be fine.
    #         tryseed = rng.advanceRng(calvin_seed, i)
    #         # We have 5 zigs in a row, so need to check 5 instead of 6.
    #         candies = rng.rareCandies(tryseed, 5)
    #         if candies >= 4:
    #             print("Calvin candies", candies, "at offset", i, "+43000")
    #             break
    #     if candies < 4:
    #         # Don't consider the seed if we don't get many candies on the Calvin
    #         # fight
    #         continue
    #     # Earliest we can generate the Zig for Wall fight is here
    #     wally_seed = rng.advanceRng(seed, 57550)
    #     for i in range(120):
    #         tryseed = rng.advanceRng(wally_seed, i)
    #         if (FastWally(tryseed)):
    #             print("Fast Wally at seed", seed, " offset:", i, "+57550\n")
    #             break

if __name__ == '__main__':
    main()