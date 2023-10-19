# -*- coding: utf-8 -*-
"""
Created on Tue Jul 23 20:51:00 2019

@author: yuhasem
"""

import heapq

SEEDS = 1 << 16
FIND_FIRST = 1
# 1-3, 105, 119, 132, 144, and 296-298 are all unfishable tiles.
# 4-22 can only be accessed with Waterfall, which doesn't suit the challenge
# I'm attempting.
IGNORE_TILES = frozenset([1,2,3,4,5,6,7,8,9,10,11,12,13,14,15,16,17,18,19,20,21,22,105,119,132,144,296,297,298])
UNFISHABLE_TILES = frozenset([1,2,3,105,119,132,144,296,297,298])
tileToSeeds = dict()
optimalSet = None
numPossibleTiles = 0

def rng(seed):
    return (0x41c64e6d * seed + 0x3039) % (1 << 32)

def getTilesFromSeed(seed):
    tiles = []
    i = 0
    while i <= 5:
        seed = rng(seed)
        tile = ((seed >> 16) & 0xffff) % 0x1bf
        if tile == 0:
            tile = 447
        if tile >= 4:
            i += 1
            tiles.append(tile)
    return sorted(set(tiles))

class TileSet():
    
    def __init__(self, tiles):
        self.tiles = set(tiles)
    
    def __eq__(self, other):
        self.tiles == other.tiles
    
    def __lt__(self, other):
        return self.f() < other.f()
    
    def f(self):
        """Returns the cost to get from start to here plus the estimated cost
        to get from here to the end."""        
        return self.g() + self.h()
    
    def g(self):
        """Returns the cost to get from start to here."""
        return len(self.tiles)
    
    def h(self):
        """Returns the estimated cost to get from here to the end."""
        seeds = set()
        for tile in self.tiles:
            for seed in tileToSeeds[tile]:
                seeds.add(seed)
        # This is a vast overestimate, but the important thing is that it will
        # never underestimate.
        return (SEEDS - len(seeds)) / (6 * SEEDS / float(numPossibleTiles))

def searchForMinimumSet(tiles, tileToSeeds):
    """A* search."""
    openNodes = []
    closedNodes = []
    start = TileSet([])
    heapq.heappush(openNodes, (start.f(), start))
    closedNodes.append((start.f(), start))
    solutions = []
    while len(openNodes) > 0:
        current = heapq.heappop(openNodes)
        if current[1].h() == 0:
            # There is no distance, hence it is a goal node
            print(current[1].tiles)
            print(len(current[1].tiles))
            solutions.append(current[1].tiles)
            if len(solutions) >= FIND_FIRST:
                return solutions
            else:
                continue
        for tile in tiles:
            if tile not in current[1].tiles:
                ls = [tile]
                ls.extend(current[1].tiles)
                newNode = TileSet(ls)
            else:
                continue
            canContinue = False
            for node in openNodes:
                if newNode == node[1]:
                    canContinue = True
                    break
            if canContinue:
                continue
            for node in closedNodes:
                if newNode == node[1]:
                    canContinue = True
                    break
            if canContinue:
                continue
            heapq.heappush(openNodes, (newNode.f(), newNode))
        closedNodes.append(current)

def isUpperRiver(tiles):
    for tile in tiles:
        if tile > 298:
            return False
    return True
    
def isLowerRiver(tiles):
    for tile in tiles:
        if tile > 23 and tile < 299:
            return False
    return True

def main():
    global SEEDS
    global tileToSeeds
    global optimalSet
    global numPossibleTiles
    seedToTiles = dict()
    
    for i in range(SEEDS):
        tiles = getTilesFromSeed(i)
        if frozenset(tiles).issubset(IGNORE_TILES):
            print("Warning! Tiles for seed %d are all ignored." % i)
            SEEDS -= 1
#        if isUpperRiver(tiles):
#            print("Tiles for seed %d are exclusively in the upper river." % i)
#        if isLowerRiver(tiles):
#            print("Tiles for seed %d are exclusively in the lower river." % i)
        seedToTiles[i] = tiles
        for tile in tiles:
            if tile in tileToSeeds:
                tileToSeeds[tile].append(i)
            else:
                tileToSeeds[tile] = [i]
    print("Done finding tiles per seed (and inverse).")
    possibleTiles = set(tileToSeeds.keys())
    possibleTiles.difference_update(IGNORE_TILES)
    numPossibleTiles = len(possibleTiles)
    solutions = searchForMinimumSet(possibleTiles, tileToSeeds)
    optimalSet = solutions[0]
    print ("Done finding optimal covers.")
    # Check the odds of missing a Feebas in one fish of every square in the optimal set
    sumChanceToMiss = 0.0
    for i in range(SEEDS):
        chanceToMiss = 1.0
        for tile in seedToTiles[i]:
            if tile in optimalSet:
                chanceToMiss *= 0.5
        sumChanceToMiss += chanceToMiss
    average = sumChanceToMiss / SEEDS
    print("Average chance to miss a Feebas in optimal set: %f" % average)
    # Check the odds of missing a Feebas in one fish of every square
    sumChanceToMiss = 0.0
    for i in range(SEEDS):
        chanceToMiss = 1.0
        for tile in seedToTiles[i]:
            if tile in possibleTiles:
                chanceToMiss *= 0.5
        sumChanceToMiss += chanceToMiss
    average = sumChanceToMiss / SEEDS
    print("Average chance to miss a Feebas in full set: %f" % average)
    
    
if __name__ == '__main__':
    # main()
    print(getTilesFromSeed(0xF90B))
