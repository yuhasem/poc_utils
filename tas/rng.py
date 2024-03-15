# -*- coding: utf-8 -*-
"""
Created on Wed Oct 13 19:24:51 2021

@author: yuhasem
"""

def top(value):
    return value >> 16

# Every step of RNG works as seed = 0x41C64E6D * seed + 0x6073
# These lists are precomputing what happens when you repeat this multiple
# times.  The entry at index i is what happens when it's repeated 2^i times.
# This makes computing many frames in advance more efficient.
multiply = [
    0x41C64E6D, 0xC2A29A69, 0xEE067F11, 0xCFDDDF21,
    0x5F748241, 0x8B2E1481, 0x76006901, 0x1711D201,
    0xBE67A401, 0xDDDF4801, 0x3FFE9001, 0x90FD2001,
    0x65FA4001, 0xDBF48001, 0xF7E90001, 0xEFD20001,
    0xDFA40001, 0xBF480001, 0x7E900001, 0xFD200001,
    0xFA400001, 0xF4800001, 0xE9000001, 0xD2000001,
    0xA4000001, 0x48000001, 0x90000001, 0x20000001,
    0x40000001, 0x80000001, 0x00000001, 0x00000001,
]
    
add = [
    0x00006073, 0xE97E7B6A, 0x31B0DDE4, 0x67DBB608,
    0xCBA72510, 0x1D29AE20, 0xBA84EC40, 0x79F01880,
    0x08793100, 0x6B566200, 0x803CC400, 0xA6B98800,
    0xE6731000, 0x30E62000, 0xF1CC4000, 0x23988000,
    0x47310000, 0x8E620000, 0x1CC40000, 0x39880000,
    0x73100000, 0xE6200000, 0xCC400000, 0x98800000,
    0x31000000, 0x62000000, 0xC4000000, 0x88000000,
    0x10000000, 0x20000000, 0x40000000, 0x80000000
]

# Same as above, but for doing RNG in reverse (it's more efficient than getting
# the index, subtracting, than playing rng forward from 0).
backwardMultiply = [
    0xEEB9EB65, 0xDC6C95D9, 0xBECE51F1, 0xB61664E1,
    0x6A6C8DC1, 0xBD562B81, 0xBC109701, 0xB1322E01,
    0x62A85C01, 0xA660B801, 0xD1017001, 0xB302E001,
    0xAA05C001, 0x640B8001, 0x08170001, 0x102E0001,
    0x205C0001, 0x40B80001, 0x81700001, 0x02E00001,
    0x05C00001, 0x0B800001, 0x17000001, 0x2E000001,
    0x5C000001, 0xB8000001, 0x70000001, 0xE0000001,
    0xC0000001, 0x80000001, 0x00000001, 0x00000001,
]

backwardAdd = [
    0x0A3561A1, 0x4D3CB126, 0x7CD1F85C, 0x9019E2F8,
    0x24D33EF0, 0x2EFFE1E0, 0x1A2153C0, 0x18A8E780,
    0x41EACF00, 0xBE399E00, 0x26033C00, 0xF2467800,
    0x7D8CF000, 0x5F19E000, 0x4E33C000, 0xDC678000,
    0xB8CF0000, 0x719E0000, 0xE33C0000, 0xC6780000,
    0x8CF00000, 0x19E00000, 0x33C00000, 0x67800000,
    0xCF000000, 0x9E000000, 0x3C000000, 0x78000000,
    0xF0000000, 0xE0000000, 0xC0000000, 0x80000000,
]

def rngCommon(seed, steps, muls, adds):
    i = 0
    while (steps > 0):
        if (steps % 2):
            seed = (seed * muls[i] + adds[i]) & 0xFFFFFFFF
        steps >>= 1
        i += 1
        if (i > 32):
            break
    return seed

def advanceRng(seed, steps):
    return rngCommon(seed, steps, multiply, add)

def reverseRng(seed, steps):
    return rngCommon(seed, steps, backwardMultiply, backwardAdd)

def index(seed):
    index = 0
    indexFind = 0
    for i in range(31):
        bit = 1 << i
        if (seed & bit) != (indexFind & bit):
            indexFind = (indexFind * multiply[i] + add[i]) & 0xFFFFFFFF
            index += bit
    bit = 1 << 31
    if (seed & bit) != (indexFind & bit):
      index += bit
    return index

class Pokemon():
    
    def __repr__(self):
        return "nat: %d, [%d,%d,%d,%d,%d,%d]" % (
            self.nature, self.hp_iv, self.att_iv, self.def_iv, self.spa_iv,
            self.spd_iv, self.spe_iv)

class StaticPokemon(Pokemon):

    def __init__(self, seed):
        # The first step is the usual VBlank
        seed = advanceRng(seed, 2)
        pid = top(seed)
        seed = advanceRng(seed, 1)
        pid += top(seed) << 16
        self.nature = pid % 25;
        
        seed = advanceRng(seed, 1)
        ivs = top(seed)
        self.hp_iv = ivs & 0x1F
        ivs >>= 5
        self.att_iv = ivs & 0x1F
        ivs >>= 5
        self.def_iv = ivs & 0x1F
        
        seed = advanceRng(seed, 1)
        ivs = top(seed)
        self.spe_iv = ivs & 0x1F
        ivs >>= 5
        self.spa_iv = ivs & 0x1F
        ivs >>= 5
        self.spd_iv = ivs & 0x1F
        
class WallyRaltsPokemon(Pokemon):
    
    def __init__(self, seed):
        # VBlank + 2 steps to generate TID (which we don't track)
        seed = advanceRng(seed, 3)
        male = False
        while not male:
            pid = 0
            seed = advanceRng(seed, 1)
            pid = top(seed)
            seed = advanceRng(seed, 1)
            pid += top(seed) << 16
            male = ((pid & 0xf0) >> 4) > 7
        self.nature = pid % 25
        
        seed = advanceRng(seed, 1)
        ivs = top(seed)
        self.hp_iv = ivs & 0x1F
        ivs >>= 5
        self.att_iv = ivs & 0x1F
        ivs >>= 5
        self.def_iv = ivs & 0x1F
        
        seed = advanceRng(seed, 1)
        ivs = top(seed)
        self.spe_iv = ivs & 0x1F
        ivs >>= 5
        self.spa_iv = ivs & 0x1F
        ivs >>= 5
        self.spd_iv = ivs & 0x1F
        
class WildPokemon(Pokemon):
    
    def __init__(self, seed, method2: bool = False):
        # The first step is one to check for Synchronize, which we don't track.
        seed = advanceRng(seed, 2)
        self.advances = 2
        self.nature = top(seed) % 25
        
        tentative_nature = -1
        while tentative_nature != self.nature:
            self.pid = 0
            seed = advanceRng(seed, 1)
            self.pid = top(seed)
            seed = advanceRng(seed, 1)
            self.pid += top(seed) << 16
            tentative_nature = self.pid % 25
            self.advances += 2
        
        seed = advanceRng(seed, 1)
        ivs = top(seed)
        self.hp_iv = ivs & 0x1F
        ivs >>= 5
        self.att_iv = ivs & 0x1F
        ivs >>= 5
        self.def_iv = ivs & 0x1F
        
        if method2:
            seed = advanceRng(seed, 1)
        
        seed = advanceRng(seed, 1)
        ivs = top(seed)
        self.spe_iv = ivs & 0x1F
        ivs >>= 5
        self.spa_iv = ivs & 0x1F
        ivs >>= 5
        self.spd_iv = ivs & 0x1F
        self.advances += 2


METEOR_FALLS_ANIMATION = 124
ROUTE_117_ANIMATION = 95
            
def heldItem(seed, mon, animation, base_frames):
    """
    Args:
        seed: the RNG seed to use
        mon: the Pokemon (returned by WildPokemon) generated by the seed
        animation: the length of the animation that plays entering battle
        base_frames: the lag frames typically generated during mon generation
        
    The number of frames generating the pokemon can vary by one, which will
    change the result of held item generation, so 2 values are returned.
    
    TODO: display a confidence level for which method generated the held item,
    based on the advances that generated the mon
    """
    # oh god those constants need to be defined
    # first 5: number of frames burned in the second set of lag frames
    # second 5: number of advances burned before the held item rng
    # -1 because mon.advances over counts
    seed = advanceRng(seed, mon.advances + base_frames + animation + 5 + 5 - 1)
    method1 = top(seed) % 100
    seed = advanceRng(seed, 1)
    method2 = top(seed) % 100
    # 5% held item is >= 95, 50% is >= 45
    return method1, method2

def testItems(seed):
    for i in range(6):
        seed = advanceRng(seed, 1)
        print(top(seed) % 100)
        
def feebasTilesFromSeed(seed):
    tiles = []
    i = 0
    while i <= 5:
        seed = (0x41c64e6d * seed + 0x3039) % (1 << 32)
        tile = (top(seed) & 0xffff) % 0x1bf
        if tile == 0:
            tile = 447
        if tile >= 4:
            i += 1
            tiles.append(tile)
    return tiles

def rareCandies(seed, size=6):
    candies = 0
    for i in range(size):
      seed = advanceRng(seed, 1)
      if (top(seed) % 10 != 0):
          continue
      seed = advanceRng(seed, 1)
      item = top(seed) % 100
      if (item >= 50 and item < 60):
          candies += 1
    return candies
