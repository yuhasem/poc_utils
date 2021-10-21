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
    
    def __init__(self, halfWord1, FID):
        # Half word 3 and 4 unused
        self.swapper = halfWord1
        self.FID = FID
        
    def __lt__(self, other):
        if (self.swapper & 0x3F) == (other.swapper & 0x3F):
            return (self.swapper >> 7) < (other.swapper >> 7)
        return (self.swapper & 0x3F) < (other.swapper & 0x3F)
    
    def __str__(self):
        return '{FID:X} with lower swap {swap}'.format(FID=self.FID, swap=(self.swapper & 0x3F))
        

def getIndexAndRandomResult(seed, index):
    max_num = MAX_NUMBERS[index]
    seed = rng.advanceRng(seed, 1)
    value = rng.top(seed) % max_num
    index = (index & 0x7F) << 9
    result = value & 0x1FF
    return (seed, index | result)

def getSuperRandomHalfWord(seed):
    """No, I legitimately don't have a better name for this function."""
    # I have no idea why this individual bit needs it's own RNG call.
    seed = rng.advanceRng(seed, 1)
    halfword = 0 if rng.top(seed) & 1 == 0 else 0x40
    
    # vblank happening here on 2nd iteration.  Does that always happen?
    # No...another call had it happen between third and fourth half word...

    # This is how is makes a variable number of RNG calls.
    seed = rng.advanceRng(seed, 1)
    if rng.top(seed) % 0x62 > 0x32:
        seed = rng.advanceRng(seed, 1)
        if rng.top(seed) % 0x62 > 0x50:
            seed = rng.advanceRng(seed, 1)
    rand = rng.top(seed) % 0x62
    top7 = rand + 0x1E
    # The game also does a & 0x7F here, but we're guaranteed not to lose
    # information even without it.
    top7 <<= 7
    halfword |= top7
    
    seed = rng.advanceRng(seed, 1)
    # You thought variable number of RNG calls was weird, now we're doing a
    # random number between 0 and a random number.
    bottom7 = rng.top(seed) % (rand + 1)
    bottom7 += 0x1E
    # Again the game does a & 07F, but again we don't lose information.
    halfword |= bottom7
    # bit 6 is now the random number from the top or'ed with this new random
    # number (which is not likely to be 1). It's...uhh...weird. And I don't
    # fully understand why it's needed.
    return (seed, halfword)

def generateCandidateFID(seed, iteration):
    seed, thirdHalfWord = getIndexAndRandomResult(seed, 0xA)

    seed = rng.advanceRng(seed, 1)
    nextIndex = 0xD if rng.top(seed) & 1 == 0 else 0xC
    seed, fourthHalfWord = getIndexAndRandomResult(seed, nextIndex)

    if iteration == 1:
        # This is an attempt to mimic the VBlank.  It's actually most likely
        # to occur during the RNG of RNG calls during the firsHalfWord call,
        # which is also the most entropic.
        #
        # We would need a really good prediction to do this accurately...it's
        # probably impossible to predict on real hardware.
        seed = rng.advanceRng(seed, 1)
    
    seed, firstHalfWord = getSuperRandomHalfWord(seed)
    
    seed = rng.advanceRng(seed, 1)
    FID = rng.top(seed)
    
    # print("\t%x" % firstHalfWord)
    # print("\tFID: %x" % FID)
    # print("\t%x" % thirdHalfWord)
    # print("\t%x" % fourthHalfWord)
    
    return seed, Candidate(firstHalfWord, FID)

def generateFID(seed):
    candidateFIDs = []
    for i in range(5):
        # print("Candidate FID %d:" % i)
        seed, candidate = generateCandidateFID(seed, i)
        candidateFIDs.append(candidate)
    for candidate in candidateFIDs:
       print(candidate)
    print()
    candidateFIDs.sort()
    for candidate in candidateFIDs:
       print(candidate) 
    

def main():
    seed = 0x6529CF57
    seed = rng.advanceRng(seed, 77)
    seed = rng.advanceRng(seed, 2)  # Either 1 or 2
    saveSeed = seed
    generateFID(seed)
    # for i in range(45):
    #     saveSeed = rng.advanceRng(saveSeed, 1)
    #     print("%x" % (rng.top(saveSeed)))

if __name__ == '__main__':
    main()