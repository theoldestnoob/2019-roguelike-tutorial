# -*- coding: utf-8 -*-
"""
Created on Tue Jul  9 21:12:03 2019

@author: theoldestnoob
"""

import tcod
from random import randint

from game_messages import Message
from map_objects.geometry import Coord


class IdleMonster:
    def take_turn(self, *args, **kwargs):
        actions = []
        # act_msg = f"The {self.owner.name} wonders when it will get to move."
        # actions.append({"message": act_msg})
        actions.append({"wait": 100})
        return actions


class BasicMonster:
    def take_turn(self, target, game_map, entities):
        actions = []
        monster = self.owner
        # if tcod.map_is_in_fov(monster.fov_map, target.x, target.y):
        if monster.fov_map.fov[target.y][target.x]:
            if monster.distance_to(target) >= 2:
                actions.append({"move_astar": (monster, target)})
            elif target.fighter and target.fighter.hp > 0:
                actions.append({"melee": (monster, target)})
            else:
                actions.append({"wait": 100})
        else:
            actions.append({"wait": 100})
        return actions


class ConfusedMonster:
    def __init__(self, previous_ai, number_of_turns=10):
        self.previous_ai = previous_ai
        self.number_of_turns = number_of_turns

    def take_turn(self, target, game_map, entities):
        actions = []

        if self.number_of_turns > 0:
            random_x = self.owner.x + randint(0, 2) - 1
            random_y = self.owner.y + randint(0, 2) - 1

            if random_x != self.owner.x and random_y != self.owner.y:
                target = Coord(random_x, random_y)
                actions.append({"move_astar": (self.owner, target)})
            else:
                actions.append({"wait": 100})

            self.number_of_turns -= 1

        else:
            self.owner.ai = self.previous_ai
            msg_str = f"The {self.owner.name} is no longer confused!"
            actions.append({"message": Message(msg_str, tcod.red)})

        return actions
