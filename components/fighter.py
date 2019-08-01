# -*- coding: utf-8 -*-
"""
Created on Tue Jul  9 21:11:17 2019

@author: theoldestnoob
"""

import tcod

from game_messages import Message


class Fighter:
    def __init__(self, hp, defense, power, xp=0):
        self.base_max_hp = hp
        self.base_defense = defense
        self.base_power = power
        self.hp = hp
        self.xp = xp

    @property
    def max_hp(self):
        if self.owner and self.owner.equipment:
            bonus = self.owner.equipment.max_hp_bonus
        else:
            bonus = 0
        return self.base_max_hp + bonus

    @property
    def defense(self):
        if self.owner and self.owner.equipment:
            bonus = self.owner.equipment.defense_bonus
        else:
            bonus = 0
        return self.base_defense + bonus

    @property
    def power(self):
        if self.owner and self.owner.equipment:
            bonus = self.owner.equipment.power_bonus
        else:
            bonus = 0
        return self.base_power + bonus

    def take_damage(self, amount):
        results = []

        self.hp -= amount

        if self.hp <= 0:
            results.append({"dead": self.owner, "xp": [None, self.xp]})

        return results

    def heal(self, amount):
        self.hp += amount
        if self.hp > self.max_hp:
            self.hp = self.max_hp

    def attack(self, target):
        results = []

        damage = self.power - target.fighter.defense

        if damage > 0:
            atk_str = (f"{self.owner.name} attacks {target.name} "
                       f"for {damage} hit points.")
            results.append({"message": Message(atk_str, tcod.white)})
            results.extend(target.fighter.take_damage(damage))
        else:
            atk_str = (f"{self.owner.name} attacks {target.name} "
                       f"but does no damage.")
            results.append({"message": Message(atk_str, tcod.white)})

        return results
