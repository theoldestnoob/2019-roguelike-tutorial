# -*- coding: utf-8 -*-
"""
Created on Tue Jul  9 21:11:17 2019

@author: theoldestnoob
"""


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

    def attack(self, target):
        results = []

        damage = self.power - target.fighter.defense

        if damage > 0:
            results.append({"message": f"{self.owner.name} attacks {target.name} for {damage} hit points."})
            results.extend(target.fighter.take_damage(damage))
        else:
            results.append({"message": f"{self.owner.name} attacks {target.name} but does no damage."})

        return results
