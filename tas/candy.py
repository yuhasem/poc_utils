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
LOWEST_RNG_ADVANCES_PER_BATTLE = 1700

FRAMES_TO_GET_IN_MENU = 124
# Assumes 1 character poke name, 1 input to get to the poke, and 10 characters
# for "RARE CANDY", so it's a bit of an overestimate.
FRAMES_TO_TAKE_ITEM = 49

# Section 1: 1984 frames, rounded up because NPC RNG frames
# Section 2: Not measured yet
FRAMES_TO_HEAL = 2000
# Zigzagoon with Tackle (35), Cut (30), and Headbutt (15)
# Aron with Tackle (35), Headbutt (15), Metal Claw (35), and Mud Slap (10)
# Geodude with Tackle (35), Rock Throw (15), Magnitude (30), and Rock Tomb (10)
INITIAL_PP = 95
MAX_PP = 95

INITIAL_SEED = 0xBAAE5A7F
MAX_PARTY_SIZE = 5

# Alter this for what you're looking for.
TO_FIND = {
    # Overestimate of candies because I really just want to get Aron as much XP
    # as possible and overgrind the candies with Geodude.
    'Rare Candy': 88,
    # Forgoing Ultra Balls because it's probably faster to just buy balls in
    # a mart.  But still check if we can pick up any for free in the route.
    # 'Ultra Ball': 10,
}

BIG_NUMBER = 1 << 31


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


class Node():
    
    def __init__(self, items, partyItems, advances, actions):
        """
        Parameters
        ----------
        items : Dict[str]int
            Which items are currently obtained. (Rare Candy, Protein, Ultra 
            Ball, PP Up, Nuggest are tracked).
        partyItems : int
            How many party memebers are carrying items
        advances : int
            How many rng advances happened to get to this node.
        actions: List[Action]
            Actions taken to get to this node (result).
        """
        self.items = items
        self.partyItems = partyItems
        self.advances = advances
        self.actions = actions
        
    def heuristic(self):
        """Returns an underestimate of the number of frames it will take to
        complete pickups from this node.
        
        Technically there are edge cases where it's an overestimate, but those
        are rare enough and would only be found near the end of the chain."""
        num = 0
        for item in ['Rare Candy', 'Protein', 'Ultra Ball', 'PP Up', 'Nugget']:
            num += max(0, TO_FIND.get(item, 0) - self.items.get(item, 0))
        return math.ceil(num/3)*(LOWEST_RNG_ADVANCES_PER_BATTLE+120) + (num//2)*menuFrames(3)
    
    def g(self):
        return self.advances

    def f(self):
        return self.g() + self.heuristic()
    
    def __lt__(self, other):
        return self.f() < other.f()


def copyItems(fromO, toO):
    for item in ['Rare Candy', 'Protein', 'Ultra Ball', 'PP Up', 'Nugget']:
        toO[item] = fromO[item]
        
def menuFrames(n):
    return FRAMES_TO_GET_IN_MENU + n*FRAMES_TO_TAKE_ITEM


def hashableInventory(items, partyItems):
    s = str(partyItems)
    for item in ['Rare Candy', 'Protein']:  # , 'Ultra Ball', 'PP Up', 'Nugget'
        s += item + str(items.get(item, 0))
    return s


def main():
    """This does an A* search to find a good battle/menuing chain to get to
    TO_FIND items. It should reutrn something close to optimal, but to keep
    things efficient, the heuristic can be outdone by superb RNG."""
    # Best g seen for each inventory state.  Used to not explore nodes that we
    # know can't be good.
    bestSeen = {}
    pq = []
    heapq.heappush(pq, Node({}, 0, 0, []))
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
            print("Expected advances: %d" % node.advances)
            break
        # If there are any items on the party, consider removing them
        if node.partyItems > 0:
            newItems = {}
            copyItems(node.items, newItems)
            newActions = []
            for action in node.actions:
                newActions.append(action)
            newActions.append(Action('M', menuFrames(node.partyItems)))
            newAdvances = node.advances + menuFrames(node.partyItems)
            
            # Check if this new node has already been explored at the same or
            # earlier frame.
            inv = hashableInventory(newItems, 0)
            seen = bestSeen.get(inv, BIG_NUMBER)
            if newAdvances >= seen:
                # Note that if we're equal we also abandon this state. Something
                # else has already investigated from this position (or better) so
                # we don't need to contine.
                continue
            bestSeen[inv] = newAdvances
            
            heapq.heappush(pq, Node(newItems, 0, newAdvances, newActions))
        pp_spent = 0
        pp_compare = INITIAL_PP
        for i in range(len(node.actions) - 1, -1, -1):
            if node.actions[i].action == "H":
                pp_compare = MAX_PP
                break
            if node.actions[i].action == "B":
                pp_spent += 1
        if pp_spent > pp_compare - 10:
            # We're almost out of PP, consider healing
            newItems = {}
            copyItems(node.items, newItems)
            newActions = []
            for action in node.actions:
                newActions.append(action)
            newActions.append(Action('H', FRAMES_TO_HEAL))
            newAdvances = node.advances + FRAMES_TO_HEAL
            heapq.heappush(pq, Node(newItems, node.partyItems, newAdvances, newActions))
            if pp_spent == pp_compare:
                # We must heal.  Don't consider anything else for this node.
                continue

        # Start searching for candies after at least 1 battle
        seed = rng.advanceRng(INITIAL_SEED, node.advances + LOWEST_RNG_ADVANCES_PER_BATTLE)

        party = MAX_PARTY_SIZE - node.partyItems
        # Assuming that if we wait this long, we might as well have gotten
        # another item in between.
        framesToSearch = 3 * LOWEST_RNG_ADVANCES_PER_BATTLE

        steps = 0
        while steps < framesToSearch:
            thisSeed = rng.advanceRng(seed, steps)
            pickups, advSteps = PickupReturn(thisSeed, party)
            oldSteps = steps
            if advSteps > 0:
                steps += advSteps
            else:
                steps += 1

            numTotalPickups = 0
            numUsefulPickups = 0
            newItems = {}
            for item in ['Rare Candy', 'Protein', 'Ultra Ball', 'PP Up', 'Nugget']:
                numTotalPickups += pickups.get(item, 0)
                newItems[item] = node.items.get(item, 0) + pickups.get(item, 0)
                if node.items.get(item, 0) < TO_FIND.get(item, 0):
                    numUsefulPickups += pickups.get(item, 0)
            # We didn't find anything good, so don't bother recording this action.
            if numUsefulPickups == 0:
                continue
            # Don't forget to count useless pickups because it still affects party size!
            numTotalPickups += pickups.get('useless', 0)

            newActions = []
            for action in node.actions:
                newActions.append(action)
            newActions.append(Action('B', LOWEST_RNG_ADVANCES_PER_BATTLE + oldSteps))
            newPartyItems = node.partyItems + numTotalPickups
            newAdvances = node.advances + LOWEST_RNG_ADVANCES_PER_BATTLE + oldSteps + 120

            newPartySize = party - numTotalPickups
            if newPartySize < 0:
                newPartySize = 0
                print ('uh oh')
            if newPartySize == 0:
                newActions.append(Action('M', menuFrames(MAX_PARTY_SIZE)))
                newAdvances += menuFrames(MAX_PARTY_SIZE)
                newPartyItems = 0
                
            # Check if this new node has already been explored at the same or
            # earlier frame.
            inv = hashableInventory(newItems, newPartyItems)
            seen = bestSeen.get(inv, BIG_NUMBER)
            if newAdvances >= seen:
                # Note that if we're equal we also abandon this state. Something
                # else has already investigated from this position (or better) so
                # we don't need to contine.
                continue
            bestSeen[inv] = newAdvances

            heapq.heappush(pq, Node(newItems, newPartyItems, newAdvances, newActions))

            
if __name__ == '__main__':
    # main()
    seed = rng.advanceRng(0xc40b7e38, 1800)
    GoodFrames(seed, 5, 100)