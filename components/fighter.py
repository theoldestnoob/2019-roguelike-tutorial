# -*- coding: utf-8 -*-
"""
Created on Tue Jul  9 21:11:17 2019

@author: theoldestnoob
"""

import tcod

from game_messages import Message


class Fighter:
    def __init__(self, hp, defense, power):
        self.max_hp = hp
        self.hp = hp
        self.defense = defense
        self.power = power

    def take_damage(self, amount):
        results = []

        self.hp -= amount

        if self.hp <= 0:
            results.append({"dead": self.owner})

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
