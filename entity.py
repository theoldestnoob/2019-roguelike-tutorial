# -*- coding: utf-8 -*-
"""
Created on Tue Jun 25 19:29:03 2019

@author: theoldestnoob
"""

import math
import tcod


class Entity:
    """
    A generic object to represent players, enemies, items, etc.
    """
    def __init__(self, ident, x, y, char, color, name, soul=0, blocks=False,
                 fov_map=None, fighter=None, ai=None):
        self.x = x
        self.y = y
        self.char = char
        self.color = color
        self.ident = ident
        self.name = name
        self.soul = soul
        self.blocks = blocks
        self.fov_recompute = False
        self.fov_map = fov_map
        self.fighter = fighter
        self.ai = ai

        if self.fighter:
            self.fighter.owner = self

        if self.ai:
            self.ai.owner = self

    def move(self, dx, dy):
        '''Change Entity location by dx, dy.'''
        self.x += dx
        self.y += dy
        self.fov_recompute = True

    def move_towards(self, target_x, target_y, game_map, entities):
        '''Move Entity in the direction of target_x, target_y.'''
        dx = target_x - self.x
        dy = target_y - self.y
        distance = math.sqrt(dx ** 2 + dy ** 2)

        dx = int(round(dx / distance))
        dy = int(round(dy / distance))

        print(f"dx: {dx}, dy: {dy}, dist: {distance}")

        if not (game_map.is_blocked(self.x + dx, self.y + dy)
                or get_blocking_entities_at_location(entities, self.x + dx,
                                                     self.y + dy)):
            self.move(dx, dy)

    def distance_to(self, other):
        '''Return the distance between Entity and other Entity.'''
        dx = other.x - self.x
        dy = other.y - self.y
        return (math.sqrt(dx ** 2 + dy ** 2))


def get_blocking_entities_at_location(entities, dest_x, dest_y):
    '''Return the first Entity in entities list on map at dest_x, dest_y.'''
    for entity in entities:
        if entity.blocks and entity.x == dest_x and entity.y == dest_y:
            return entity
    return None
