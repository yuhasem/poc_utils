# -*- coding: utf-8 -*-
"""
Created on Sat Dec 21 10:03:56 2019

@author: yuhasem
"""

PICKUP_CONFIG = {
  'sapphire': [
    {
      'level': 1,
      'odds': [
        (0.3, 'Super Potion'),
        (0.4, 'Ultra Ball'),
        (0.5, 'Full Restore'),
        (0.6, 'Full Heal'),
        (0.7, 'Nugget'),
        (0.8, 'Revive'),
        (0.9, 'Rare Candy'),
        (0.95, 'Protein'),
        (0.99, 'PP Up'),
        (1, 'King\'s Rock'),
      ]
    }
  ],
  'fire_red': [
    {
      'level': 1,
      'odds': [
        (0.15, 'Oran Berry'),
        (0.25, 'Aspear Berry'),
        (0.35, 'Cheri Berry'),
        (0.45, 'Chesto Berry'),
        (0.55, 'Pecha Berry'),
        (0.65, 'Persim Berry'),
        (0.75, 'Rawst Berry'),
        (0.8, 'Nugget'),
        (0.85, 'PP Up'),
        (0.9, 'Rare Candy'),
        (0.95, 'TM 10 (Hidden Power)'),
        (0.96, 'Belue Berry'),
        (0.97, 'Durin Berry'),
        (0.98, 'Pamtree Berry'),
        (0.90, 'Spelon Berry'),
        (1, 'Watmel Berry'),
      ]
    }
  ],
  'emerald': [
    {
      'level': 1,
      'odds': [
        (0.3, 'Potion'),
        (0.4, 'Antidote'),
        (0.5, 'Super Potion'),
        (0.6, 'Great Ball'),
        (0.7, 'Repel'),
        (0.8, 'Escape Rope'),
        (0.9, 'X Attack'),
        (0.94, 'Full Heal'),
        (0.98, 'Ultra Ball'),
        (0.99, 'Hyper Potion'),
        (1, 'Nugget'),
      ]
    },
    {
      'level': 11,
      'odds': [
        (0.3, 'Antidote'),
        (0.4, 'Super Potion'),
        (0.5, 'Great Ball'),
        (0.6, 'Repel'),
        (0.7, 'Escape Rope'),
        (0.8, 'X Attack'),
        (0.9, 'Full Heal'),
        (0.94, 'Ultra Ball'),
        (0.98, 'Hyper Potion'),
        (0.99, 'Nugget'),
        (1, 'King\'s Rock'),
      ]
    },
    {
      'level': 21,
      'odds': [
        (0.3, 'Super Potion'),
        (0.4, 'Great Ball'),
        (0.5, 'Repel'),
        (0.6, 'Escape Rope'),
        (0.7, 'X Attack'),
        (0.8, 'Full Heal'),
        (0.9, 'Ultra Ball'),
        (0.94, 'Hyper Potion'),
        (0.98, 'Rare Candy'),
        (0.99, 'King\'s Rock'),
        (1, 'Full Restore'),
      ]
    },
    {
      'level': 31,
      'odds': [
        (0.3, 'Great Ball'),
        (0.4, 'Repel'),
        (0.5, 'Escape Rope'),
        (0.6, 'X Attack'),
        (0.7, 'Full Heal'),
        (0.8, 'Ultra Ball'),
        (0.9, 'Hyper Potion'),
        (0.94, 'Rare Candy'),
        (0.98, 'Protein'),
        (0.99, 'Full Restore'),
        (1, 'Ether'),
      ]
    },
    {
      'level': 41,
      'odds': [
        (0.3, 'Repel'),
        (0.4, 'Escape Rope'),
        (0.5, 'X Attack'),
        (0.6, 'Full Heal'),
        (0.7, 'Ultra Ball'),
        (0.8, 'Hyper Potion'),
        (0.9, 'Rare Candy'),
        (0.94, 'Protein'),
        (0.98, 'Revive'),
        (0.99, 'Ether'),
        (1, 'White Herb'),
      ]
    },
    {
      'level': 51,
      'odds': [
        (0.3, 'Escape Rope'),
        (0.4, 'X Attack'),
        (0.5, 'Full Heal'),
        (0.6, 'Ultra Ball'),
        (0.7, 'Hyper Potion'),
        (0.8, 'Rare Candy'),
        (0.9, 'Protein'),
        (0.94, 'Revive'),
        (0.98, 'HP Up'),
        (0.99, 'White Herb'),
        (1, 'TM44 (Rest)'),
      ]
    },
    {
      'level': 61,
      'odds': [
        (0.3, 'X Attack'),
        (0.4, 'Full Heal'),
        (0.5, 'Ultra Ball'),
        (0.6, 'Hyper Potion'),
        (0.7, 'Rare Candy'),
        (0.8, 'Protein'),
        (0.9, 'Revive'),
        (0.94, 'HP Up'),
        (0.98, 'Full Restore'),
        (0.99, 'TM44 (Rest)'),
        (1, 'Elixir'),
      ]
    },
    {
      'level': 71,
      'odds': [
        (0.3, 'Full Heal'),
        (0.4, 'Ultra Ball'),
        (0.5, 'Hyper Potion'),
        (0.6, 'Rare Candy'),
        (0.7, 'Protein'),
        (0.8, 'Revive'),
        (0.9, 'HP Up'),
        (0.94, 'Full Restore'),
        (0.98, 'Max Revive'),
        (0.99, 'Elixir'),
        (1, 'TM01 (Focus Punch)'),
      ]
    },
    {
      'level': 81,
      'odds': [
        (0.3, 'Ultra Ball'),
        (0.4, 'Hyper Potion'),
        (0.5, 'Rare Candy'),
        (0.6, 'Protein'),
        (0.7, 'Revive'),
        (0.8, 'HP Up'),
        (0.9, 'Full Restore'),
        (0.94, 'Max Revive'),
        (0.98, 'PP Up'),
        (0.99, 'TM01 (Focus Punch)'),
        (1, 'Leftovers'),
      ]
    },
    {
      'level': 91,
      'odds': [
        (0.3, 'Hyper Potion'),
        (0.4, 'Rare Candy'),
        (0.5, 'Protein'),
        (0.6, 'Revive'),
        (0.7, 'HP Up'),
        (0.8, 'Full Restore'),
        (0.9, 'Max Revive'),
        (0.94, 'PP Up'),
        (0.98, 'Max Elixir'),
        (0.99, 'Leftovers'),
        (1, 'TM26 (Earthquake)'),
      ]
    },
  ],
  'platinum': [
    {
      'level': 1,
      'odds': [
        (0.3, 'Potion'),
        (0.4, 'Antidote'),
        (0.5, 'Super Potion'),
        (0.6, 'Great Ball'),
        (0.7, 'Repel'),
        (0.8, 'Escape Rope'),
        (0.9, 'Full Heal'),
        (0.94, 'Hyper Potion'),
        (0.98, 'Ultra Ball'),
        (0.99, 'Nugget'),
        (1, 'Hyper Potion'),
      ]
    },
    {
      'level': 11,
      'odds': [
        (0.3, 'Antidote'),
        (0.4, 'Super Potion'),
        (0.5, 'Great Ball'),
        (0.6, 'Repel'),
        (0.7, 'Escape Rope'),
        (0.8, 'Full Heal'),
        (0.9, 'Hyper Potion'),
        (0.94, 'Ultra Ball'),
        (0.98, 'Revive'),
        (0.99, 'King\'s Rock'),
        (1, 'Nugget'),
      ]
    },
    {
      'level': 21,
      'odds': [
        (0.3, 'Super Potion'),
        (0.4, 'Great Ball'),
        (0.5, 'Repel'),
        (0.6, 'Escape Rope'),
        (0.7, 'Full Heal'),
        (0.8, 'Hyper Potion'),
        (0.9, 'Ultra Ball'),
        (0.94, 'Revive'),
        (0.98, 'Rare Candy'),
        (0.99, 'Full Restore'),
        (1, 'King\'s Rock'),
      ]
    },
    {
      'level': 31,
      'odds': [
        (0.3, 'Great Ball'),
        (0.4, 'Repel'),
        (0.5, 'Escape Rope'),
        (0.6, 'Full Heal'),
        (0.7, 'Hyper Potion'),
        (0.8, 'Ultra Ball'),
        (0.9, 'Revive'),
        (0.94, 'Rare Candy'),
        (0.98, 'Dusk Stone'),
        (0.99, 'Ether'),
        (1, 'Full Restore'),
      ]
    },
    {
      'level': 41,
      'odds': [
        (0.3, 'Repel'),
        (0.4, 'Escape Rope'),
        (0.5, 'Full Heal'),
        (0.6, 'Hyper Potion'),
        (0.7, 'Ultra Ball'),
        (0.8, 'Revive'),
        (0.9, 'Rare Candy'),
        (0.94, 'Dusk Stone'),
        (0.98, 'Shiny Stone'),
        (0.99, 'White Herb'),
        (1, 'Ether'),
      ]
    },
    {
      'level': 51,
      'odds': [
        (0.3, 'Escape Rope'),
        (0.4, 'Full Heal'),
        (0.5, 'Hyper Potion'),
        (0.6, 'Ultra Ball'),
        (0.7, 'Revive'),
        (0.8, 'Rare Candy'),
        (0.9, 'Dusk Stone'),
        (0.94, 'Shiny Stone'),
        (0.98, 'Dawn Stone'),
        (0.99, 'TM44 (Rest)'),
        (1, 'White Herb'),
      ]
    },
    {
      'level': 61,
      'odds': [
        (0.3, 'Full Heal'),
        (0.4, 'Hyper Potion'),
        (0.5, 'Ultra Ball'),
        (0.6, 'Revive'),
        (0.7, 'Rare Candy'),
        (0.8, 'Dusk Stone'),
        (0.9, 'Shiny Stone'),
        (0.94, 'Dawn Stone'),
        (0.98, 'Full Restore'),
        (0.99, 'Elixir'),
        (1, 'TM44 (Rest)'),
      ]
    },
    {
      'level': 71,
      'odds': [
        (0.3, 'Hyper Potion'),
        (0.4, 'Ultra Ball'),
        (0.5, 'Revive'),
        (0.6, 'Rare Candy'),
        (0.7, 'Dusk Stone'),
        (0.8, 'Shiny Stone'),
        (0.9, 'Dawn Stone'),
        (0.94, 'Full Restore'),
        (0.98, 'Max Revive'),
        (0.99, 'TM01 (Focus Punch)'),
        (1, 'Elixir'),
      ]
    },
    {
      'level': 81,
      'odds': [
        (0.3, 'Ultra Ball'),
        (0.4, 'Revive'),
        (0.5, 'Rare Candy'),
        (0.6, 'Dusk Stone'),
        (0.7, 'Shiny Stone'),
        (0.8, 'Dawn Stone'),
        (0.9, 'Full Restore'),
        (0.94, 'Max Revive'),
        (0.98, 'PP Up'),
        (0.99, 'Leftovers'),
        (1, 'TM01 (Focus Punch)'),
      ]
    },
    {
      'level': 91,
      'odds': [
        (0.3, 'Revive'),
        (0.4, 'Rare Candy'),
        (0.5, 'Dusk Stone'),
        (0.6, 'Shiny Stone'),
        (0.7, 'Dawn Stone'),
        (0.8, 'Full Restore'),
        (0.9, 'Max Revive'),
        (0.94, 'PP Up'),
        (0.98, 'Max Elixir'),
        (0.99, 'TM26 (Earthquake)'),
        (1, 'Leftovers'),
      ]
    },
  ],
  'heart_gold': [
    {
      'level': 1,
      'odds': [
        (0.3, 'Potion'),
        (0.4, 'Antidote'),
        (0.5, 'Super Potion'),
        (0.6, 'Great Ball'),
        (0.7, 'Repel'),
        (0.8, 'Escape Rope'),
        (0.9, 'Full Heal'),
        (0.94, 'Hyper Potion'),
        (0.98, 'Ultra Ball'),
        (0.99, 'Max Repel'),
        (1, 'Nugget'),
      ]
    },
    {
      'level': 11,
      'odds': [
        (0.3, 'Antidote'),
        (0.4, 'Super Potion'),
        (0.5, 'Great Ball'),
        (0.6, 'Repel'),
        (0.7, 'Escape Rope'),
        (0.8, 'Full Heal'),
        (0.9, 'Hyper Potion'),
        (0.94, 'Ultra Ball'),
        (0.98, 'Revive'),
        (0.99, 'Nugget'),
        (1, 'King\'s Rock'),
      ]
    },
    {
      'level': 21,
      'odds': [
        (0.3, 'Super Potion'),
        (0.4, 'Great Ball'),
        (0.5, 'Repel'),
        (0.6, 'Escape Rope'),
        (0.7, 'Full Heal'),
        (0.8, 'Hyper Potion'),
        (0.9, 'Ultra Ball'),
        (0.94, 'Revive'),
        (0.98, 'Rare Candy'),
        (0.99, 'King\'s Rock'),
        (1, 'Full Restore'),
      ]
    },
    {
      'level': 31,
      'odds': [
        (0.3, 'Great Ball'),
        (0.4, 'Repel'),
        (0.5, 'Escape Rope'),
        (0.6, 'Full Heal'),
        (0.7, 'Hyper Potion'),
        (0.8, 'Ultra Ball'),
        (0.9, 'Revive'),
        (0.94, 'Rare Candy'),
        (0.98, 'Sun Stone'),
        (0.99, 'Full Restore'),
        (1, 'Ether'),
      ]
    },
    {
      'level': 41,
      'odds': [
        (0.3, 'Repel'),
        (0.4, 'Escape Rope'),
        (0.5, 'Full Heal'),
        (0.6, 'Hyper Potion'),
        (0.7, 'Ultra Ball'),
        (0.8, 'Revive'),
        (0.9, 'Rare Candy'),
        (0.94, 'Sun Stone'),
        (0.98, 'Moon Stone'),
        (0.99, 'Ether'),
        (1, 'Iron Ball'),
      ]
    },
    {
      'level': 51,
      'odds': [
        (0.3, 'Escape Rope'),
        (0.4, 'Full Heal'),
        (0.5, 'Hyper Potion'),
        (0.6, 'Ultra Ball'),
        (0.7, 'Revive'),
        (0.8, 'Rare Candy'),
        (0.9, 'Sun Stone'),
        (0.94, 'Moon Stone'),
        (0.98, 'Heart Scale'),
        (0.99, 'Iron Ball'),
        (1, 'TM56 (Fling)'),
      ]
    },
    {
      'level': 61,
      'odds': [
        (0.3, 'Full Heal'),
        (0.4, 'Hyper Potion'),
        (0.5, 'Ultra Ball'),
        (0.6, 'Revive'),
        (0.7, 'Rare Candy'),
        (0.8, 'Sun Stone'),
        (0.9, 'Moon Stone'),
        (0.94, 'Heart Scale'),
        (0.98, 'Full Restore'),
        (0.99, 'TM56 (Fling)'),
        (1, 'Elixir'),
      ]
    },
    {
      'level': 71,
      'odds': [
        (0.3, 'Hyper Potion'),
        (0.4, 'Ultra Ball'),
        (0.5, 'Revive'),
        (0.6, 'Rare Candy'),
        (0.7, 'Sun Stone'),
        (0.8, 'Moon Stone'),
        (0.9, 'Heart Scale'),
        (0.94, 'Full Restore'),
        (0.98, 'Max Revive'),
        (0.99, 'Elixir'),
        (1, 'TM86 (Grass Knot)'),
      ]
    },
    {
      'level': 81,
      'odds': [
        (0.3, 'Ultra Ball'),
        (0.4, 'Revive'),
        (0.5, 'Rare Candy'),
        (0.6, 'Sun Stone'),
        (0.7, 'Moon Stone'),
        (0.8, 'Heart Scale'),
        (0.9, 'Full Restore'),
        (0.94, 'Max Revive'),
        (0.98, 'PP Up'),
        (0.99, 'TM86 (Grass Knot)'),
        (1, 'Leftovers'),
      ]
    },
    {
      'level': 91,
      'odds': [
        (0.3, 'Revive'),
        (0.4, 'Rare Candy'),
        (0.5, 'Sun Stone'),
        (0.6, 'Moon Stone'),
        (0.7, 'Heart Scale'),
        (0.8, 'Full Restore'),
        (0.9, 'Max Revive'),
        (0.94, 'PP Up'),
        (0.98, 'Max Elixir'),
        (0.99, 'Leftovers'),
        (1, 'TM26 (Earthquake)'),
      ]
    },
  ],
  'black': [
    {
      'level': 1,
      'odds': [
        (0.3, 'Potion'),
        (0.4, 'Antidote'),
        (0.5, 'Super Potion'),
        (0.6, 'Great Ball'),
        (0.7, 'Repel'),
        (0.8, 'Escape Rope'),
        (0.9, 'Full Heal'),
        (0.94, 'Hyper Potion'),
        (0.98, 'Ultra Ball'),
        (0.99, 'Max Repel'),
        (1, 'Nugget'),
      ]
    },
    {
      'level': 11,
      'odds': [
        (0.3, 'Antidote'),
        (0.4, 'Super Potion'),
        (0.5, 'Great Ball'),
        (0.6, 'Repel'),
        (0.7, 'Escape Rope'),
        (0.8, 'Full Heal'),
        (0.9, 'Hyper Potion'),
        (0.94, 'Ultra Ball'),
        (0.98, 'Revive'),
        (0.99, 'Nugget'),
        (1, 'King\'s Rock'),
      ]
    },
    {
      'level': 21,
      'odds': [
        (0.3, 'Super Potion'),
        (0.4, 'Great Ball'),
        (0.5, 'Repel'),
        (0.6, 'Escape Rope'),
        (0.7, 'Full Heal'),
        (0.8, 'Hyper Potion'),
        (0.9, 'Ultra Ball'),
        (0.94, 'Revive'),
        (0.98, 'Rare Candy'),
        (0.99, 'King\'s Rock'),
        (1, 'Full Restore'),
      ]
    },
    {
      'level': 31,
      'odds': [
        (0.3, 'Great Ball'),
        (0.4, 'Repel'),
        (0.5, 'Escape Rope'),
        (0.6, 'Full Heal'),
        (0.7, 'Hyper Potion'),
        (0.8, 'Ultra Ball'),
        (0.9, 'Revive'),
        (0.94, 'Rare Candy'),
        (0.98, 'Sun Stone'),
        (0.99, 'Full Restore'),
        (1, 'Iron Ball'),
      ]
    },
    {
      'level': 41,
      'odds': [
        (0.3, 'Repel'),
        (0.4, 'Escape Rope'),
        (0.5, 'Full Heal'),
        (0.6, 'Hyper Potion'),
        (0.7, 'Ultra Ball'),
        (0.8, 'Revive'),
        (0.9, 'Rare Candy'),
        (0.94, 'Sun Stone'),
        (0.98, 'Moon Stone'),
        (0.99, 'Iron Ball'),
        (1, 'Lucky Egg'),
      ]
    },
    {
      'level': 51,
      'odds': [
        (0.3, 'Escape Rope'),
        (0.4, 'Full Heal'),
        (0.5, 'Hyper Potion'),
        (0.6, 'Ultra Ball'),
        (0.7, 'Revive'),
        (0.8, 'Rare Candy'),
        (0.9, 'Sun Stone'),
        (0.94, 'Moon Stone'),
        (0.98, 'Heart Scale'),
        (0.99, 'Lucky Egg'),
        (1, 'Prism Scale'),
      ]
    },
    {
      'level': 61,
      'odds': [
        (0.3, 'Full Heal'),
        (0.4, 'Hyper Potion'),
        (0.5, 'Ultra Ball'),
        (0.6, 'Revive'),
        (0.7, 'Rare Candy'),
        (0.8, 'Sun Stone'),
        (0.9, 'Moon Stone'),
        (0.94, 'Heart Scale'),
        (0.98, 'Full Restore'),
        (0.99, 'Prism Scale'),
        (1, 'Elixir'),
      ]
    },
    {
      'level': 71,
      'odds': [
        (0.3, 'Hyper Potion'),
        (0.4, 'Ultra Ball'),
        (0.5, 'Revive'),
        (0.6, 'Rare Candy'),
        (0.7, 'Sun Stone'),
        (0.8, 'Moon Stone'),
        (0.9, 'Heart Scale'),
        (0.94, 'Full Restore'),
        (0.98, 'Max Revive'),
        (0.99, 'Elixir'),
        (1, 'Prism Scale'),
      ]
    },
    {
      'level': 81,
      'odds': [
        (0.3, 'Ultra Ball'),
        (0.4, 'Revive'),
        (0.5, 'Rare Candy'),
        (0.6, 'Sun Stone'),
        (0.7, 'Moon Stone'),
        (0.8, 'Heart Scale'),
        (0.9, 'Full Restore'),
        (0.94, 'Max Revive'),
        (0.98, 'PP Up'),
        (0.99, 'Prism Scale'),
        (1, 'Leftovers'),
      ]
    },
    {
      'level': 91,
      'odds': [
        (0.3, 'Revive'),
        (0.4, 'Rare Candy'),
        (0.5, 'Sun Stone'),
        (0.6, 'Moon Stone'),
        (0.7, 'Heart Scale'),
        (0.8, 'Full Restore'),
        (0.9, 'Max Revive'),
        (0.94, 'PP Up'),
        (0.98, 'Max Elixir'),
        (0.99, 'Leftovers'),
        (1, 'Prism Scale'),
      ]
    },
  ],
  'x': [
    {
      'level': 1,
      'odds': [
        (0.3, 'Potion'),
        (0.4, 'Antidote'),
        (0.5, 'Super Potion'),
        (0.6, 'Great Ball'),
        (0.7, 'Repel'),
        (0.8, 'Escape Rope'),
        (0.9, 'Full Heal'),
        (0.94, 'Hyper Potion'),
        (0.98, 'Ultra Ball'),
        (0.99, 'Hyper Potion'),
        (1, 'Nugget'),
      ]
    },
    {
      'level': 11,
      'odds': [
        (0.3, 'Antidote'),
        (0.4, 'Super Potion'),
        (0.5, 'Great Ball'),
        (0.6, 'Repel'),
        (0.7, 'Escape Rope'),
        (0.8, 'Full Heal'),
        (0.9, 'Hyper Potion'),
        (0.94, 'Ultra Ball'),
        (0.98, 'Revive'),
        (0.99, 'Nugget'),
        (1, 'King\'s Rock'),
      ]
    },
    {
      'level': 21,
      'odds': [
        (0.3, 'Super Potion'),
        (0.4, 'Great Ball'),
        (0.5, 'Repel'),
        (0.6, 'Escape Rope'),
        (0.7, 'Full Heal'),
        (0.8, 'Hyper Potion'),
        (0.9, 'Ultra Ball'),
        (0.94, 'Revive'),
        (0.98, 'Rare Candy'),
        (0.99, 'King\'s Rock'),
        (1, 'Full Restore'),
      ]
    },
    {
      'level': 31,
      'odds': [
        (0.3, 'Great Ball'),
        (0.4, 'Repel'),
        (0.5, 'Escape Rope'),
        (0.6, 'Full Heal'),
        (0.7, 'Hyper Potion'),
        (0.8, 'Ultra Ball'),
        (0.9, 'Revive'),
        (0.94, 'Rare Candy'),
        (0.98, 'Sun Stone'),
        (0.99, 'Full Restore'),
        (1, 'Ether'),
      ]
    },
    {
      'level': 41,
      'odds': [
        (0.3, 'Repel'),
        (0.4, 'Escape Rope'),
        (0.5, 'Full Heal'),
        (0.6, 'Hyper Potion'),
        (0.7, 'Ultra Ball'),
        (0.8, 'Revive'),
        (0.9, 'Rare Candy'),
        (0.94, 'Sun Stone'),
        (0.98, 'Moon Stone'),
        (0.99, 'Ether'),
        (1, 'Iron Ball'),
      ]
    },
    {
      'level': 51,
      'odds': [
        (0.3, 'Escape Rope'),
        (0.4, 'Full Heal'),
        (0.5, 'Hyper Potion'),
        (0.6, 'Ultra Ball'),
        (0.7, 'Revive'),
        (0.8, 'Rare Candy'),
        (0.9, 'Sun Stone'),
        (0.94, 'Moon Stone'),
        (0.98, 'Heart Scale'),
        (0.99, 'Iron Ball'),
        (1, 'Prism Scale'),
      ]
    },
    {
      'level': 61,
      'odds': [
        (0.3, 'Full Heal'),
        (0.4, 'Hyper Potion'),
        (0.5, 'Ultra Ball'),
        (0.6, 'Revive'),
        (0.7, 'Rare Candy'),
        (0.8, 'Sun Stone'),
        (0.9, 'Moon Stone'),
        (0.94, 'Heart Scale'),
        (0.98, 'Full Restore'),
        (0.99, 'Prism Scale'),
        (1, 'Elixir'),
      ]
    },
    {
      'level': 71,
      'odds': [
        (0.3, 'Hyper Potion'),
        (0.4, 'Ultra Ball'),
        (0.5, 'Revive'),
        (0.6, 'Rare Candy'),
        (0.7, 'Sun Stone'),
        (0.8, 'Moon Stone'),
        (0.9, 'Heart Scale'),
        (0.94, 'Full Restore'),
        (0.98, 'Max Revive'),
        (0.99, 'Elixir'),
        (1, 'Prism Scale'),
      ]
    },
    {
      'level': 81,
      'odds': [
        (0.3, 'Ultra Ball'),
        (0.4, 'Revive'),
        (0.5, 'Rare Candy'),
        (0.6, 'Sun Stone'),
        (0.7, 'Moon Stone'),
        (0.8, 'Heart Scale'),
        (0.9, 'Full Restore'),
        (0.94, 'Max Revive'),
        (0.98, 'PP Up'),
        (0.99, 'Prism Scale'),
        (1, 'Leftovers'),
      ]
    },
    {
      'level': 91,
      'odds': [
        (0.3, 'Revive'),
        (0.4, 'Rare Candy'),
        (0.5, 'Sun Stone'),
        (0.6, 'Moon Stone'),
        (0.7, 'Heart Scale'),
        (0.8, 'Full Restore'),
        (0.9, 'Max Revive'),
        (0.94, 'PP Up'),
        (0.98, 'Max Elixir'),
        (0.99, 'Leftovers'),
        (1, 'Prism Scale'),
      ]
    },
  ],
  'omega_ruby': [
    {
      'level': 1,
      'odds': [
        (0.3, 'Potion'),
        (0.4, 'Antidote'),
        (0.5, 'Super Potion'),
        (0.6, 'Great Ball'),
        (0.7, 'Repel'),
        (0.8, 'Escape Rope'),
        (0.9, 'Full Heal'),
        (0.94, 'Hyper Potion'),
        (0.98, 'Ultra Ball'),
        (0.99, 'Hyper Potion'),
        (1, 'Nugget'),
      ]
    },
    {
      'level': 11,
      'odds': [
        (0.3, 'Antidote'),
        (0.4, 'Super Potion'),
        (0.5, 'Great Ball'),
        (0.6, 'Repel'),
        (0.7, 'Escape Rope'),
        (0.8, 'Full Heal'),
        (0.9, 'Hyper Potion'),
        (0.94, 'Ultra Ball'),
        (0.98, 'Revive'),
        (0.99, 'Nugget'),
        (1, 'King\'s Rock'),
      ]
    },
    {
      'level': 21,
      'odds': [
        (0.3, 'Super Potion'),
        (0.4, 'Great Ball'),
        (0.5, 'Repel'),
        (0.6, 'Escape Rope'),
        (0.7, 'Full Heal'),
        (0.8, 'Hyper Potion'),
        (0.9, 'Ultra Ball'),
        (0.94, 'Revive'),
        (0.98, 'Rare Candy'),
        (0.99, 'King\'s Rock'),
        (1, 'Full Restore'),
      ]
    },
    {
      'level': 31,
      'odds': [
        (0.3, 'Great Ball'),
        (0.4, 'Repel'),
        (0.5, 'Escape Rope'),
        (0.6, 'Full Heal'),
        (0.7, 'Hyper Potion'),
        (0.8, 'Ultra Ball'),
        (0.9, 'Revive'),
        (0.94, 'Rare Candy'),
        (0.98, 'Sun Stone'),
        (0.99, 'Full Restore'),
        (1, 'Ether'),
      ]
    },
    {
      'level': 41,
      'odds': [
        (0.3, 'Repel'),
        (0.4, 'Escape Rope'),
        (0.5, 'Full Heal'),
        (0.6, 'Hyper Potion'),
        (0.7, 'Ultra Ball'),
        (0.8, 'Revive'),
        (0.9, 'Rare Candy'),
        (0.94, 'Sun Stone'),
        (0.98, 'Moon Stone'),
        (0.99, 'Ether'),
        (1, 'Iron Ball'),
      ]
    },
    {
      'level': 51,
      'odds': [
        (0.3, 'Escape Rope'),
        (0.4, 'Full Heal'),
        (0.5, 'Hyper Potion'),
        (0.6, 'Ultra Ball'),
        (0.7, 'Revive'),
        (0.8, 'Rare Candy'),
        (0.9, 'Sun Stone'),
        (0.94, 'Moon Stone'),
        (0.98, 'Heart Scale'),
        (0.99, 'Iron Ball'),
        (1, 'Destiny Knot'),
      ]
    },
    {
      'level': 61,
      'odds': [
        (0.3, 'Full Heal'),
        (0.4, 'Hyper Potion'),
        (0.5, 'Ultra Ball'),
        (0.6, 'Revive'),
        (0.7, 'Rare Candy'),
        (0.8, 'Sun Stone'),
        (0.9, 'Moon Stone'),
        (0.94, 'Heart Scale'),
        (0.98, 'Full Restore'),
        (0.99, 'Destiny Knot'),
        (1, 'Elixir'),
      ]
    },
    {
      'level': 71,
      'odds': [
        (0.3, 'Hyper Potion'),
        (0.4, 'Ultra Ball'),
        (0.5, 'Revive'),
        (0.6, 'Rare Candy'),
        (0.7, 'Sun Stone'),
        (0.8, 'Moon Stone'),
        (0.9, 'Heart Scale'),
        (0.94, 'Full Restore'),
        (0.98, 'Max Revive'),
        (0.99, 'Elixir'),
        (1, 'Destiny Knot'),
      ]
    },
    {
      'level': 81,
      'odds': [
        (0.3, 'Ultra Ball'),
        (0.4, 'Revive'),
        (0.5, 'Rare Candy'),
        (0.6, 'Sun Stone'),
        (0.7, 'Moon Stone'),
        (0.8, 'Heart Scale'),
        (0.9, 'Full Restore'),
        (0.94, 'Max Revive'),
        (0.98, 'PP Up'),
        (0.99, 'Destiny Knot'),
        (1, 'Leftovers'),
      ]
    },
    {
      'level': 91,
      'odds': [
        (0.3, 'Revive'),
        (0.4, 'Rare Candy'),
        (0.5, 'Sun Stone'),
        (0.6, 'Moon Stone'),
        (0.7, 'Heart Scale'),
        (0.8, 'Full Restore'),
        (0.9, 'Max Revive'),
        (0.94, 'PP Up'),
        (0.98, 'Max Elixir'),
        (0.99, 'Leftovers'),
        (1, 'Destiny Knot'),
      ]
    },
  ],
}

# Aliases
PICKUP_CONFIG['ruby'] = PICKUP_CONFIG['sapphire']
PICKUP_CONFIG['leaf_green'] = PICKUP_CONFIG['fire_red']
PICKUP_CONFIG['diamond'] = PICKUP_CONFIG['platinum']
PICKUP_CONFIG['pearl'] = PICKUP_CONFIG['platinum']
PICKUP_CONFIG['soul_silver'] = PICKUP_CONFIG['heart_gold']
PICKUP_CONFIG['white'] = PICKUP_CONFIG['black']
PICKUP_CONFIG['y'] = PICKUP_CONFIG['x']
PICKUP_CONFIG['black2'] = PICKUP_CONFIG['x']
PICKUP_CONFIG['white2'] = PICKUP_CONFIG['x']
PICKUP_CONFIG['alpha_sapphire'] = PICKUP_CONFIG['omega_ruby']