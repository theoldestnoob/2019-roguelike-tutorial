# -*- coding: utf-8 -*-
"""
Created on Mon Aug 12 19:19:55 2019

@author: theoldestnoob
"""

import tcod


class Gnosis():
    def __init__(self, char="@", color=tcod.white, speed=25, fov_range=10,
                 move_range=10, duration=500):
        self.char = char
        self.color = color
        self.speed = speed
        self.fov_range = fov_range
        self.move_range = move_range
        self.duration = duration
