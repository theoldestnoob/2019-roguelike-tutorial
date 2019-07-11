# -*- coding: utf-8 -*-
"""
Created on Tue Jul  9 21:12:03 2019

@author: theoldestnoob
"""

import tcod


class IdleMonster:
    def take_turn(self, *args, **kwargs):
        results = []
        results.append({"message": f"The {self.owner.name} wonders when it will get to move."})
        return results


class BasicMonster:
    def take_turn(self, target, game_map, entities):
        results = []
        monster = self.owner
        if tcod.map_is_in_fov(monster.fov_map, target.x, target.y):
            if monster.distance_to(target) >= 2:
                monster.move_astar(target, entities, game_map)
            elif target.fighter and target.fighter.hp > 0:
                attack_results = monster.fighter.attack(target)
                results.extend(attack_results)
        return results
