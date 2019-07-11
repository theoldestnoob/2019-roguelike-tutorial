# -*- coding: utf-8 -*-
"""
Created on Wed Jul 10 22:31:29 2019

@author: theoldestnoob
"""


import tcod


def kill_entity(entity):
    death_message = f"{entity.name} is dead!"

    entity.char = '%'
    entity.color = tcod.dark_red
    entity.blocks = False
    entity.fighter = None
    entity.ai = None
    entity.soul = 0
    entity.name = f"remains of {entity.name}"

    return death_message
