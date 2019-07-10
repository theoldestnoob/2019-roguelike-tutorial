# -*- coding: utf-8 -*-
"""
Created on Tue Jul  9 21:12:03 2019

@author: theoldestnoob
"""

import tcod


class IdleMonster:
    def take_turn(self):
        print(f"The {self.owner.name} wonders when it will get to move.")


class BasicMonster:
    def take_turn(self, target, game_map, entities):
        monster = self.owner
        if tcod.map_is_in_fov(monster.fov_map, target.x, target.y):
            if monster.distance_to(target) >= 2:
                monster.move_towards(target.x, target.y, game_map, entities)
            elif target.fighter.hp > 0:
                print(f"The {monster.name} insults the {target.name}! Its ego is damaged!")
