# -*- coding: utf-8 -*-
"""
Created on Wed Oct 13 19:24:51 2021

@author: Yuhas
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
 0x40000001, 0x80000001, 0x00000001, 0x00000001]
    
add = [
 0x00006073, 0xE97E7B6A, 0x31B0DDE4, 0x67DBB608,
 0xCBA72510, 0x1D29AE20, 0xBA84EC40, 0x79F01880,
 0x08793100, 0x6B566200, 0x803CC400, 0xA6B98800,
 0xE6731000, 0x30E62000, 0xF1CC4000, 0x23988000,
 0x47310000, 0x8E620000, 0x1CC40000, 0x39880000,
 0x73100000, 0xE6200000, 0xCC400000, 0x98800000,
 0x31000000, 0x62000000, 0xC4000000, 0x88000000,
 0x10000000, 0x20000000, 0x40000000, 0x80000000]

def advanceRng(seed, steps):
    i = 0
    while (steps > 0):
        if (steps % 2):
            seed = (seed * multiply[i] + add[i]) % (1 << 32)
        steps >> 1
        i += 1
        if (i > 32):
            break
    return seed

class Pokemon():

    def __init__(self, seed):
        seed = advanceRng(seed, 1)
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
    
