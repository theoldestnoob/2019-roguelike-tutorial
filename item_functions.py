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


def cast_lightning(*args, **kwargs):
    caster = args[0]
    entities = kwargs.get("entities")
    fov_map = caster.fov_map
    damage = kwargs.get("damage")
    max_range = kwargs.get("max_range")

    results = []

    target = None
    closest_distance = max_range + 1

    # find closest entity that isn't the caster and isn't entity 0
    for entity in entities:
        if (entity.fighter and entity is not caster and entity.ident != 0
                and fov_map.fov[entity.y][entity.x]):
            distance = caster.distance_to(entity)
            if distance < closest_distance:
                target = entity
                closest_distance = distance
    # if a valid target is found, damage them; otherwise report failure
    if target:
        msg_str = (f"A lightning bolt strikes the {target.name} "
                   f"with a loud thunder! The damage is {damage}.")
        msg = Message(msg_str, tcod.white)
        results.append({"consumed": True, "message": msg})
        results.extend(target.fighter.take_damage(damage))
    else:
        msg = Message("No enemy is close enough to strike.", tcod.red)
        results.append({"consumed": False, "message": msg})

    return results
