# -*- coding: utf-8 -*-
"""
Created on Wed Jul 31 21:03:24 2019

@author: theoldestnoob
"""


class Equippable:
    def __init__(self, slot, power_bonus=0, defense_bonus=0, max_hp_bonus=0):
        self.slot = slot
        self.power_bonus = power_bonus
        self.defense_bonus = defense_bonus
        self.max_hp_bonus = max_hp_bonus
