# -*- coding: utf-8 -*-
"""
Created on Tue Jun 25 20:45:41 2019

@author: theoldestnoob
"""


class Tile:
    """A tile on a map. It may or may not be blocked, and may or may not block
    sight.
    """
    def __init__(self, blocked, block_sight=None):
        self.blocked = blocked
        # By default, if a tile is blocked, it also blocks sight
        if block_sight is None:
            block_sight = blocked
        self.block_sight = block_sight
        self.explored = []

    def __repr__(self):
        return f"Tile({self.blocked})"
