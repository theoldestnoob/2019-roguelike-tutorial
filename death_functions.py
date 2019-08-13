# -*- coding: utf-8 -*-
"""
Created on Wed Jul 10 22:31:29 2019

@author: theoldestnoob
"""


import tcod

from render_functions import RenderOrder
from game_messages import Message


def kill_entity(entity):
    death_message = Message(f"{entity.name} is dead!", tcod.orange)

    entity.char = '%'
    entity.color = tcod.dark_red
    entity.blocks = False
    entity.fighter = None
    entity.ai = None
    entity.soul = None
    entity.name = f"remains of {entity.name}"
    entity.render_order = RenderOrder.CORPSE
    entity.speed = 0

    return death_message
