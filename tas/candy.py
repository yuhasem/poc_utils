# -*- coding: utf-8 -*-
"""
Created on Sun Nov 14 09:12:06 2021

@author: yuhasem
"""

import rng


def PickupReturn(seed, partySize):
    pickups = {}
    steps = 0
    # We return the number of steps to advance before trying again, to make
    # this more efficient (for example, if we didn't get any pickups, we know
    # we can skip the entire party size window instead of trying each extra
    # frame individually).
    retSteps = -1
    for i in range(partySize):
        seed = rng.advanceRng(seed, 1)
        steps += 1
        if rng.top(seed) % 10 != 0:
            continue
        # If we encounter a pickup in a slot other than the first, we should
        # try again with that pickup in the first slot, to maximize number of
        # potential pickups
        retSteps = steps - 1 if retSteps == -1 else retSteps
        seed = rng.advanceRng(seed, 1)
        steps += 1
        pickup = rng.top(seed) % 100
        if pickup >= 40 and pickup < 50:
            pickups['Ultra Ball'] = pickups.get('Ultra Ball', 0) + 1
        elif pickup >= 50 and pickup < 60:
            pickups['Rare Candy'] = pickups.get('Rare Candy', 0) + 1
        elif pickup >= 80 and pickup < 90:
            pickups['Nugget'] = pickups.get('Nugget', 0) + 1
        elif pickup >= 90 and pickup < 95:
            pickups['Protein'] = pickups.get('Protein', 0) + 1
        elif pickup >= 95 and pickup < 99:
            pickups['PP Up'] = pickups.get('PP Up', 0) + 1
        else:
            pickups['useless'] = pickups.get('useless', 0) + 1
    return (pickups, retSteps if retSteps != -1 else steps)


def main():
    # TODO: make these flags
    seed = 0x8E0222DD
    partySize = 6
    framesToSearch = 4800
    steps = 0

    while steps < framesToSearch:
        thisSeed = rng.advanceRng(seed, steps)
        pickups, advSteps = PickupReturn(thisSeed, partySize)
        candies = pickups.get('Rare Candy', 0)
        if candies > 1:
            print('MULTI-CANDY: Advance %d "steps" and get %s' % (steps, pickups))
        elif candies == 1:
            if ('Ultra Ball' in pickups or 'Nugget' in pickups
                or 'Protein' in pickups or 'PP Up' in pickups):
                print('CANDY+: Advance %d "steps" and get %s' % (steps, pickups))
        if advSteps > 0:
            steps += advSteps
        else:
            steps += 1
            
if __name__ == '__main__':
    main()