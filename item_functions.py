# -*- coding: utf-8 -*-
"""
Created on Sat Jul 20 20:52:50 2019

@author: theoldestnoob
"""

import tcod

from game_messages import Message


def heal(*args, **kwargs):
    entity = args[0]
    amount = kwargs.get("amount")

    results = []

    if entity.fighter.hp == entity.fighter.max_hp:
        msg = Message("You are already at full health", tcod.yellow)
        results.append({"consumed": False, "message": msg})
    else:
        msg = Message("Your wounds start to feel better!", tcod.green)
        entity.fighter.heal(amount)
        results.append({"consumed": True, "message": msg})

    return results
