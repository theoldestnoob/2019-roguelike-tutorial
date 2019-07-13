# -*- coding: utf-8 -*-
"""
Created on Tue Jul  9 21:12:03 2019

@author: theoldestnoob
"""

import tcod


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
