# -*- coding: utf-8 -*-
"""
Created on Wed Oct 20 06:37:50 2021

@author: yuhasem
"""

import rng

# The game generates a random number up to a maximum size, determined by
# indexing this list.  Only the relevant numbers for FID generation are
# populated.
#
# Actually sometime these numbers are indicies to another list, but that's not
# used by FID generation so I haven't tried to figure out why yet.
MAX_NUMBERS = [0,0,0,0,0,0,0,0,0,0,0x45,0,0x2D,0x36]

class Candidate():
    
    def __init__(self, halfWord1, FID, trendy1, trendy2):
        # Half word 3 and 4 unused
        self.swapper = halfWord1
        self.FID = FID
        self.firstTrendyWord = trendy1
        self.secondTrendyWord = trendy2
        
    def __lt__(self, other):
        if (self.swapper & 0x3F) == (other.swapper & 0x3F):
            return (self.swapper >> 7) < (other.swapper >> 7)
        return (self.swapper & 0x3F) < (other.swapper & 0x3F)
    
    def __str__(self):
        return '{FID:X} with lower swap {swap}'.format(FID=self.FID, swap=(self.swapper & 0x3F))
    
    def __repr__(self):
        return '%x,%x,%x,%x' % (self.swapper, self.FID, self.firstTrendyWord, self.secondTrendyWord)
        

def getTrendyWord(seed, index):
    "The half-word which describes a word to put in the trendy phrase."
    max_num = MAX_NUMBERS[index]
    seed = rng.advanceRng(seed, 1)
    print("trendy word with list %s and seed %x" % (index, seed))
    value = rng.top(seed) % max_num
    print("index %s" % value)
    index = (index & 0x7F) << 9
    result = value & 0x1FF
    return (seed, index | result)

def getComparator(seed, injectVblank):
    """The half-word which is used to compare candidates.
    
    There is a small difference in this code between Ruby and Sapphire.  Needs
    more investigation to know if there's an actualy difference in
    functionality."""
    # I have no idea why this individual bit needs it's own RNG call.
    seed = rng.advanceRng(seed, 1)
    halfword = 0 if rng.top(seed) & 1 == 0 else 0x40
    print("starting comparator %s" % halfword)
    
    if injectVblank == 4:
        seed = rng.advanceRng(seed, 1)
    # This is how is makes a variable number of RNG calls.
    seed = rng.advanceRng(seed, 1)
    print("%x" % seed)
    if rng.top(seed) % 0x62 > 0x32:
        print("continue")
        if injectVblank == 5:
            seed = rng.advanceRng(seed, 1)
        seed = rng.advanceRng(seed, 1)
        print("%x" % seed)
        if rng.top(seed) % 0x62 > 0x50:
            print("continue")
            if injectVblank == 6:
                seed = rng.advanceRng(seed, 1)
            seed = rng.advanceRng(seed, 1)
            print("%x" % seed)
    rand = rng.top(seed) % 0x62
    print("final rand %x" % rand)
    top7 = rand + 0x1E
    # The game also does a & 0x7F here, but we're guaranteed not to lose
    # information even without it.
    top7 <<= 7
    halfword |= top7
    
    if injectVblank == 7:
        seed = rng.advanceRng(seed, 1)
    seed = rng.advanceRng(seed, 1)
    # You thought variable number of RNG calls was weird, now we're doing a
    # random number between 0 and a random number.
    bottom7 = rng.top(seed) % (rand + 1)
    bottom7 += 0x1E
    print("bottom rand %x" % bottom7)
    # Again the game does a & 07F, but again we don't lose information.
    halfword |= bottom7
    # bit 6 is now the random number from the top or'ed with this new random
    # number (which is not likely to be 1). It's...uhh...weird. And I don't
    # fully understand why it's needed.
    return (seed, halfword)

def generateCandidateFID(seed, injectVblank=-1):
    """Generates a full CandidateFID at the given seed, injecting an extra
    RNG advancement at the index given by injectVblank.
    
    Args:
        seed: the starting seed to generate from.
        injectVblank: optional.  Where to inject an extra rng advancement.
          Valid values are 0 to 8 inclusive."""
    if injectVblank == 0:
        seed = rng.advanceRng(seed, 1)
    seed, firstTrendyWord = getTrendyWord(seed, 0xA)

    if injectVblank == 1:
        seed = rng.advanceRng(seed, 1)
    seed = rng.advanceRng(seed, 1)
    print("%x" % rng.top(seed))
    nextIndex = 0xD if rng.top(seed) & 1 == 0 else 0xC
    print("picked random list %s" % nextIndex)
    
    if injectVblank == 2:
        seed = rng.advanceRng(seed, 1)
    seed, secondTrendyWord = getTrendyWord(seed, nextIndex)

    if injectVblank == 3:
        seed = rng.advanceRng(seed, 1)
    seed, comparator = getComparator(seed, injectVblank)
    
    if injectVblank == 8:
        seed = rng.advanceRng(seed, 1)
    seed = rng.advanceRng(seed, 1)
    FID = rng.top(seed)
    
    # print("\t%x" % firstHalfWord)
    # print("\tFID: %x" % FID)
    # print("\t%x" % thirdHalfWord)
    # print("\t%x" % fourthHalfWord)
    
    return seed, Candidate(comparator, FID, firstTrendyWord, secondTrendyWord)

def generateFID(seed):
    candidateFIDs = []
    for i in range(5):
        # print("Candidate FID %d:" % i)
        inject = 3 if i == 1 else -1
        seed, candidate = generateCandidateFID(seed, inject)
        candidateFIDs.append(candidate)
    for candidate in candidateFIDs:
       print(candidate)
    print()
    candidateFIDs.sort()
    for candidate in candidateFIDs:
       print(candidate) 
    

def main():
    seed = 0xAFCBA65D
    seed = rng.advanceRng(seed, 2)  # Either 1 or 2
    print("%x " % seed)
    print(generateCandidateFID(seed, 0))
    
    # for i in range(45):
    #     saveSeed = rng.advanceRng(saveSeed, 1)
    #     print("%x" % (rng.top(saveSeed)))

if __name__ == '__main__':
    main()