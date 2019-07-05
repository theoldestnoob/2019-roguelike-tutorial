# -*- coding: utf-8 -*-
"""
Created on Tue Jun 25 19:29:03 2019

@author: theoldestnoob
"""


class Entity:
    """
    A generic object to represent players, enemies, items, etc.
    """
    def __init__(self, ident, x, y, char, color, name, blocks=False,
                 fov_map=None):
        self.x = x
        self.y = y
        self.char = char
        self.color = color
        self.ident = ident
        self.fov_map = fov_map
        self.name = name
        self.blocks = blocks

    def move(self, dx, dy):
        # move the entity by a given amount
        self.x += dx
        self.y += dy


def get_blocking_entities_at_location(entities, dest_x, dest_y):
    for entity in entities:
        if entity.blocks and entity.x == dest_x and entity.y == dest_y:
            return entity
    return None
