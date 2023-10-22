# -*- coding: utf-8 -*-
"""
Created on Sun Nov 14 09:12:06 2021

@author: yuhasem
There is about 256 candies to get in the first section (we may want to get
more, depending on when the lead evolves).  The size of each entry in the queue
will be dominated by the size of the list of frames to get candies on.  That
will contain <256 elements, and assuming Deque implementation, will be 5KiB
max.  Assumin a max of n^2 elements being checked (probably less beause of how
linear the search space is structured), that would take around 4MiB of memory,
so we're well within acceptable bounds.

TODO: We could precisely model the wild pokemon generated and how quickly they
could be beaten, which requires knowing the main's stats and potentially move
learn levels.
"""

import rng
import heapq
import math

# Not actually the least, but it's a good enough estimate to get things going.
# This was 1-shotting a wild Zigzagoon, including the time it took to generate
# the encounter by running.  I only counted frame rng advances, not advances
# for things like PID generation, damage rolls, etc.  It took extra steps to
# get into the encounter, so it should all even out. (Plus long poke name takes
# additional battle frames).
# Ignore the above.  Experience tells me this will be at least 2000. I'll try
# to refine this estimate given the actual conditions we see in the grind.
# In reality this varies a lot based on level situation.  A more complicated
# model would be needed to take that into account, which I'm not going to build
# right now.
LOWEST_RNG_ADVANCES_PER_BATTLE = 1600
ANIMATION = rng.ROUTE_117_ANIMATION

# Stuff for PID inside battle length consideration
LOWEST_RNG_ADVANCES_WITHIN_BATTLE = 1152
CRY = 135

FRAMES_TO_GET_IN_MENU = 124
# Assumes 1 character poke name, 1 input to get to the poke, and 10 characters
# for "RARE CANDY", so it's a bit of an overestimate.
FRAMES_TO_TAKE_ITEM = 49

# Section 1: 1984 frames, rounded up because NPC RNG frames
# Section 2: Not measured yet (not needed)
FRAMES_TO_HEAL = 2000
# Zigzagoon with Tackle (35), Cut (30), and Headbutt (15)
# Aron with Tackle (35), Headbutt (15), Metal Claw (35), and Mud Slap (10)
# Geodude with Tackle (35), Rock Throw (15), Magnitude (30)
INITIAL_PP = 50
MAX_PP = 50

INITIAL_SEED = 0
MAX_PARTY_SIZE = 6

# Alter this for what you're looking for.
TO_FIND = {
    # Overestimate of candies because I really just want to get Aron as much XP
    # as possible and overgrind the candies with Geodude.
    'Rare Candy': 50,
    # Forgoing Ultra Balls because it's probably faster to just buy balls in
    # a mart.  But still check if we can pick up any for free in the route.
    # 'Ultra Ball': 10,
}

BIG_NUMBER = 1 << 31


# A lower bound (wrong) estimate of how many frames were spent
#  search for mon (x1.25) | animation (x1) | battle (x2) | fadeout (x2) | fadeout (x1)
# |-----------------------|----------------|-------------|--------------|-------------|
#  minimum 40             | around 120     | variable    | 41           | 33
#  wrong because need pid | constants in rng.py | wrong because acc/crit/roll check |||
MINIMUM_BATTLE_FRAMES = ((LOWEST_RNG_ADVANCES_PER_BATTLE - 50 - ANIMATION) // 2) + 40 + ANIMATION + 41 + 33


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
    # TODO: fix retSteps so that it will actually dectect solo Rare Candy grabs
    # on the last mon.
    return (pickups, 1)


def GoodFrames(seed, partySize, framesToSearch):
    """Use This to find locally good item grabs."""
    steps = 0

    while steps < framesToSearch:
        thisSeed = rng.advanceRng(seed, steps)
        pickups, advSteps = PickupReturn(thisSeed, partySize)
        candies = pickups.get('Rare Candy', 0)
        balls = pickups.get('Ultra Ball', 0)
        if candies > 1:
            print('MULTI-CANDY: Advance %d and get %s' % (steps, pickups))
        elif candies == 1:
            print('CANDY+: Advance %d and get %s' % (steps, pickups))
        elif candies < 1:
            if ('Ultra Ball' in pickups or 'PP Up' in pickups or 'Protein' in pickups):
                print('ITEM+: Advance %d and get %s' % (steps, pickups))
        # if candies + balls >= 2:
        #     print('GOOD-FRAME: Advance %d and get %s' % (steps, pickups))
        if advSteps > 0:
            steps += advSteps
        else:
            steps += 1
            
def TripleCandy(seed, partySize, framesToSearch):
    steps = 0

    while steps < framesToSearch:
        thisSeed = rng.advanceRng(seed, steps)
        pickups, advSteps = PickupReturn(thisSeed, partySize)
        candies = pickups.get('Rare Candy', 0)
        balls = pickups.get('Ultra Ball', 0)
        if (candies + balls) >= 3:
            print('BEST FRAME: Advance %d and get %s' % (steps, pickups))
        elif (candies + balls) == 2:
            print('FRAME: Advance %d and get %s' % (steps, pickups))
        if advSteps > 0:
            steps += advSteps
        else:
            steps += 1


class Action():
    
    def __init__(self, action, advances):
        """action: str = which action (Menu/Battle).
        advances: int = how many rng advacnes to wait."""
        self.action = action
        self.advances = advances
        
    def __str__(self):
        return "%s for %s" % (self.action, self.advances)
    
    def __repr__(self):
        return str(self)
    
    
class Battle(Action):
    
    def __init__(self, advances, candies, pickups, pid, pidDelay):
        self.action = 'B'
        self.advances = advances
        self.candies = candies
        self.pickups = pickups
        self.pid = pid
        self.pidDelay = pidDelay
        
    def __str__(self):
        return f"{self.action} (pid {self.pid} in {self.pidDelay}) for {self.advances} ({self.candies}RC/{self.pickups})"


class Node():
    
    def __init__(self, items, partyItems, frames, advances, actions, pp):
        """
        Parameters
        ----------
        items : Dict[str]int
            Which items are currently obtained. (Rare Candy, Protein, Ultra 
            Ball, PP Up, Nuggest are tracked).
        partyItems : int
            How many party memebers are carrying items
        frames : int
            How many frames it took to get to this node.
        advances : int
            How many rng advances happened to get to this node.
        actions: List[Action]
            Actions taken to get to this node (result).
        pp : int
            How much pp is remaining
        """
        self.items = items
        self.partyItems = partyItems
        self.frames = frames
        self.advances = advances
        self.actions = actions
        self.pp = pp
        
    def heuristic(self):
        """Returns an underestimate of the number of frames it will take to
        complete pickups from this node.
        
        Technically there are edge cases where it's an overestimate, but those
        are rare enough and would only be found near the end of the chain."""
        num = 0
        for item in TO_FIND.keys():
            num += max(0, TO_FIND.get(item, 0) - self.items.get(item, 0))
        return math.ceil(num/3)*(MINIMUM_BATTLE_FRAMES) + (num//2)*menuFrames(3)
    
    def g(self):
        return self.frames

    def f(self):
        return self.g() + self.heuristic()
    
    def __lt__(self, other):
        return self.f() < other.f()


def copyItems(original):
    copy = {}
    for item in ['Rare Candy', 'Protein', 'Ultra Ball', 'PP Up', 'Nugget']:
        copy[item] = original.get(item, 0)
    return copy

def copyActions(original):
    copy = []
    for action in original:
        copy.append(action)
    return copy
        
def menuFrames(n):
    return FRAMES_TO_GET_IN_MENU + n*FRAMES_TO_TAKE_ITEM


def hashableInventory(items, partyItems):
    s = str(partyItems)
    for item in ['Rare Candy', 'Protein']:  # , 'Ultra Ball', 'PP Up', 'Nugget'
        s += item + str(items.get(item, 0))
    return s

def battleFrames(pickupAdvances: int, pidAdvances: int, pid: int):
    """Returns the number of frames it takes to complete a battle (from first
    movement in overworld to ability to move in overworld).  Returns -1 if the
    pickup cannot be hit given the pidAdvances/pid combination."""
    advancesToPickup = pidAdvances + pid + CRY*2 + LOWEST_RNG_ADVANCES_WITHIN_BATTLE
    if advancesToPickup < LOWEST_RNG_ADVANCES_PER_BATTLE:
        return -1
    pidFrames = 32 + ((pidAdvances - 32)*4 // 5)
    battleFrames = (pickupAdvances - pidAdvances - pid - ANIMATION) // 2
    return pidFrames + ANIMATION + battleFrames + 41 + 33


def nextNodeFromMenuAction(node):
    newItems = copyItems(node.items)
    newActions = copyActions(node.actions)
    frames = menuFrames(node.partyItems)
    newActions.append(Action('M', frames))
    
    return Node(newItems, 0, node.frames + frames, node.advances + frames,
                newActions, node.pp)


def nextNodeFromHealAction(node):
    newActions = copyActions(node.actions)
    newActions.append(Action('H', FRAMES_TO_HEAL))
    
    return Node(node.items, node.partyItems, node.frames + FRAMES_TO_HEAL,
                node.advances + FRAMES_TO_HEAL, newActions, MAX_PP)


def nextNodeFromBattleAction(node, steps, pickup, total):
    newItems = copyItems(node.items)
    for item in pickup:
        newItems[item] = newItems.get(item, 0) + pickup[item]
    newActions = copyActions(node.actions)
    newActions.append(
        Battle(
            LOWEST_RNG_ADVANCES_PER_BATTLE + steps,
            pickup.get('Rare Candy', 0),
            total,
            0,
            0))
    newPartyItems = node.partyItems + total
    newAdvances = node.advances + LOWEST_RNG_ADVANCES_PER_BATTLE + steps + 120
    # A lower bound (wrong) estimate of how many frames were spent
    #  search for mon (x1.25) | animation (x1) | battle (x2) | fadeout (x2) | fadeout (x1)
    # |-----------------------|----------------|-------------|--------------|-------------|
    #  minimum 40             | around 120     | variable    | 41           | 33
    #  wrong because need pid | constants in rng.py | wrong because acc/crit/roll check |||
    monSearchAdvances = 40 * 1.25
    battleAdvances = (LOWEST_RNG_ADVANCES_PER_BATTLE + steps) - monSearchAdvances - ANIMATION
    newFrames = node.frames + 40 + ANIMATION + (battleAdvances // 2) + 41 + 33
    
    if newPartyItems == MAX_PARTY_SIZE:
        menu = menuFrames(MAX_PARTY_SIZE)
        newActions.append(Action('M', menu))
        newAdvances += menu
        newFrames += menu
        newPartyItems = 0

    return Node(newItems, newPartyItems, newFrames, newAdvances, newActions, node.pp - 1)


def shouldAbandonState(node: Node, bestSeen: dict) -> bool:
    """Checks whether `node` can be abandoned

    Parameters
    ----------
    node : Node
        The node to investigate if it can be abandoned.
    bestSeen : TYPE
        A dict from inventories to the smallest number of frames to reach that
        inventory.

    Returns
    -------
    bool
        Whether the state can be abandoned because a better state has already
        been investigated.

    """
    inv = hashableInventory(node.items, node.partyItems)
    seen = bestSeen.get(inv, BIG_NUMBER)
    bestSeen[inv] = min(node.frames, seen)
    return node.frames >= seen


def usefulAndTotalPickups(pickup, node):
    """Depends on the node because some pickups only matter if you haven't
    got everything you need in that category."""
    numUsefulPickups = 0
    numTotalPickups = 0
    for item in pickup.keys():
        numTotalPickups += pickup.get(item)
        if item in TO_FIND and node.items.get(item, 0) < TO_FIND.get(item):
            numUsefulPickups += pickup.get(item)
    return numUsefulPickups, numTotalPickups


def candySearch(node, steps, seed, bestSeen):
    pickups, advSteps = PickupReturn(seed, MAX_PARTY_SIZE - node.partyItems)
    useful, total = usefulAndTotalPickups(pickups, node)
    if useful == 0:
        return advSteps, None
    battleNode = nextNodeFromBattleAction(node, steps, pickups, total)
    if shouldAbandonState(battleNode, bestSeen):
        return advSteps, None
    return advSteps, battleNode


def battleNodes(node, bestSeen, pidCache):
    newNodes = []
    # Start searching for candies after at least 1 battle
    seed = rng.advanceRng(INITIAL_SEED, node.advances + LOWEST_RNG_ADVANCES_PER_BATTLE)
    # Assuming that if we wait this long, we might as well have gotten
    # another item in between.
    framesToSearch = 3 * LOWEST_RNG_ADVANCES_PER_BATTLE

    steps = 0
    while steps < framesToSearch:
        thisSeed = rng.advanceRng(seed, steps)
        advSteps, battleNode = candySearch(node, steps, thisSeed, bestSeen)
        if battleNode is not None:
            newNodes.append(battleNode)
        
        if advSteps > 0:
            steps += advSteps
        else:
            steps += 1
    return newNodes


def main():
    """This does an A* search to find a good battle/menuing chain to get to
    TO_FIND items. It should reutrn something close to optimal, but to keep
    things efficient, the heuristic can be outdone by superb RNG."""
    # Best g seen for each inventory state.  Used to not explore nodes that we
    # know can't be good.
    bestSeen = {}
    pidCache = {}
    pq = []
    heapq.heappush(pq, Node({}, 0, 0, 0, [], INITIAL_PP))
    # TODO: insert first node
    while len(pq) > 0:
        node = heapq.heappop(pq)
        print("Investigating node f = %d, h = %d" % (node.f(), node.heuristic()))
        print(node.items)
        print(node.partyItems)
        print()
        if node.heuristic() == 0:
            print("DONE!")
            print(node.items)
            print(node.actions)
            print("Expected frames: %d" % node.frames)
            break
        # If there are any items on the party, consider removing them
        if node.partyItems > 0:
            newNode = nextNodeFromMenuAction(node)
            
            if shouldAbandonState(newNode, bestSeen):
                continue
            
            heapq.heappush(pq, newNode)
            
        if node.pp < 5:
            # We're almost out of PP, consider healing
            heapq.heappush(pq, nextNodeFromHealAction(node))
            if node.pp == 0:
                # We must heal.  Don't consider anything else for this node.
                continue

        newNodes = battleNodes(node, bestSeen, pidCache)
        for n in newNodes:
            heapq.heappush(pq, n)

            
if __name__ == '__main__':
    main()
    # seed = rng.advanceRng(0xBEF7CFE9, 0)
    # GoodFrames(seed, 4, 900)
    # TripleCandy(0x56FC8F33, 4, 20000)