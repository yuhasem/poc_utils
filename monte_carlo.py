# -*- coding: utf-8 -*-
"""
Created on Fri Jul 19 19:38:55 2019

@author: yuhasem
"""

from absl import app
from absl import flags

import pickup_config
import random

FLAGS = flags.FLAGS

flags.DEFINE_integer('battles', 10000000, 'Number of battles to simulate with Pickup', lower_bound=1)
flags.DEFINE_integer('search_every', None, 'How many battles should happen before Pickup items are counted and cleared.  If this is set, search_every_lower and search_every_upper will be ignored.', lower_bound=1)
flags.DEFINE_integer('search_every_lower', 1, 'When search_every_lower and search_every_upper are set, loop through all possible values and report the results of the simulation for each.', lower_bound=1)
flags.DEFINE_integer('search_every_upper', 1, 'When search_every_lower and search_every_upper are set, loop through all possible values and report the results of the simulation for each.', lower_bound=1)
flags.DEFINE_integer('party_size', None, 'How many Pickup pokemon in the party to simulate', lower_bound=1, upper_bound=6)
flags.DEFINE_integer('party_size_lower', 5, 'How many Pickup pokemon in the party to simulate, loop through all possible values and report the results of the simulation for each.', lower_bound=1, upper_bound=6)
flags.DEFINE_integer('party_size_upper', 5, 'How many Pickup pokemon in the party to simulate, loop through all possible values and report the results of the simulation for each.', lower_bound=1, upper_bound=6)
flags.DEFINE_enum('game', 'sapphire', ['ruby', 'sapphire', 'fire_red', 'leaf_green', 'emerald', 'diamond', 'pearl', 'platinum', 'heart_gold', 'soul_silver', 'black', 'white', 'black2', 'white2', 'x', 'y', 'omega_ruby', 'alpha_sapphire'], 'Which game configuration to run the simulation in')
flags.DEFINE_list('levels', [1], 'Levels of the pokemon in your party. Entries beyond on the party size are ignored. Last entry will be repeated if less than party size')

class Pickup():
    
    def __init__(self, game, level):
        self.item = ""
        self.odds = None
        base = pickup_config.PICKUP_CONFIG[game]
        for level_odds in base:
            if level >= level_odds['level']:
                self.odds = level_odds['odds']
        if self.odds is None:
            print("Something went wrong trying to get odds for this Pokemon.")
            print("game:", game)
            print("level:", level)
            # Fail-safe, so we don't crash during execution
            self.odds = [(1, "Potion")]
        
    def gen_new_item(self):
        if self.item != "":
            return
        rand = random.random()
        for odd in self.odds:
            if rand < odd[0]:
                self.item = odd[1]
                break

    def reset(self):
        self.item = ""

def _simulation(game, party_size, search_every, battles, party_levels):
    candies = 0
    team = []
    for i in range(party_size):
        team.append(Pickup(game, party_levels[i]))
    for i in range(battles):
        for pickup in team:
            if random.random() < 0.1:
                pickup.gen_new_item()
        if i % search_every == 0:
            for pickup in team:
                if pickup.item == "Rare Candy":
                    candies += 1
                pickup.reset()
    return candies

def main(argv):
    del argv  # Unused.
    if FLAGS.search_every:
        search_every_range = range(FLAGS.search_every, FLAGS.search_every + 1)
    else:
        if FLAGS.search_every_upper < FLAGS.search_every_upper:
            print("search_every_upper must be at least as large as search_every_lower")
            exit(1)
        search_every_range = range(FLAGS.search_every_lower, FLAGS.search_every_upper + 1)
    if FLAGS.party_size:
        party_size_range = range(FLAGS.party_size, FLAGS.party_size + 1)
    else:
        if FLAGS.party_size_upper < FLAGS.party_size_upper:
            print("search_every_upper must be at least as large as search_every_lower")
            exit(1)
        party_size_range = range(FLAGS.party_size_lower, FLAGS.party_size_upper + 1)
    raw_levels = FLAGS.levels[0:6]
    try:
        levels = [int(level) for level in raw_levels]
    except ValueError:
        print("all levels must be integers")
    for level in levels:
        if level <= 0:
            print("all levels must be positive")
            exit(1)
    while len(levels) < 6:
        levels.append(levels[-1])
    print("Using game: ", FLAGS.game)
    print("With levels: ", levels)
    print("Battles in each simulation: ", FLAGS.battles)
    seperator = "+------------+--------------+--------------+-------+"
    print(seperator)
    print("| Party Size | Search Every | Rare Candies |  RC % |")
    print(seperator)
    for party_size in party_size_range:
        for search_every in search_every_range:
            candies = _simulation(FLAGS.game, party_size, search_every, FLAGS.battles, levels)
            print("| {0:10d} | {1:12d} | {2:12d} | {3:.2f}% |".format(party_size, search_every, candies, (candies * 100 / FLAGS.battles)))
            print(seperator)
    return 0

if __name__ == '__main__':
    app.run(main)
