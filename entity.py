# -*- coding: utf-8 -*-
"""
Created on Tue Jun 25 19:29:03 2019

@author: theoldestnoob
"""


class Entity:
    """
    A generic object to represent players, enemies, items, etc.
    """
    def __init__(self, x, y, char, color):
        self.x = x
        self.y = y
        self.char = char
        self.color = color

    def move(self, dx, dy):
        # move the entity by a given amount
        self.x += dx
        self.y += dy
