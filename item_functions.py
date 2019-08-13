# -*- coding: utf-8 -*-
"""
Created on Sat Jul 20 20:52:50 2019

@author: theoldestnoob
"""

import tcod

from game_messages import Message
from components.ai import ConfusedMonster


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
    damage = kwargs.get("damage")
    max_range = kwargs.get("max_range")

    results = []

    target = None
    closest_distance = max_range + 1

    # find closest entity that isn't the caster and isn't etheric
    for entity in entities:
        if (entity.fighter and entity is not caster and not entity.etheric
                and caster.fov_map.fov[entity.y][entity.x]):
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


def cast_fireball(*args, **kwargs):
    caster = args[0]
    entities = kwargs.get("entities")
    damage = kwargs.get("damage")
    radius = kwargs.get("radius")
    target_x = kwargs.get("target_x")
    target_y = kwargs.get("target_y")

    results = []

    if not caster.fov_map.fov[target_y][target_x]:
        msg_str = f"You cannot target a tile outside of your field of view."
        msg = Message(msg_str, tcod.yellow)
        results.append({"consumed": False, "message": msg})
    else:
        msg_str = (f"The fireball explodes, "
                   f"burning everything within {radius} tiles!")
        msg = Message(msg_str, tcod.orange)
        results.append({"consumed": True, "message": msg})
        for entity in entities:
            if (entity.fighter and not entity.etheric
                    and entity.distance(target_x, target_y) <= radius):
                msg_str = (f"The {entity.name} gets burned "
                           f"for {damage} hit points.")
                msg = Message(msg_str, tcod.orange)
                results.append({"message": msg})
                results.extend(entity.fighter.take_damage(damage))

    return results


def cast_confuse(*args, **kwargs):
    caster = args[0]
    entities = kwargs.get("entities")
    target_x = kwargs.get("target_x")
    target_y = kwargs.get("target_y")

    results = []

    if not caster.fov_map.fov[target_y][target_x]:
        msg_str = f"You cannot target a tile outside of your field of view."
        msg = Message(msg_str, tcod.yellow)
        results.append({"consumed": False, "message": msg})

    for entity in entities:
        if entity.ai and entity.x == target_x and entity.y == target_y:
            confused_ai = ConfusedMonster(entity.ai, 10)
            confused_ai.owner = entity
            entity.ai = confused_ai
            msg_str = (f"The eyes of the {entity.name} look vacant, "
                       f"as he starts to stumble around!")
            msg = Message(msg_str, tcod.light_green)
            results.append({"consumed": True, "message": msg})
            break
    else:
        msg_str = "There is no targetable enemy at that location."
        msg = Message(msg_str, tcod.yellow)
        results.append({"consumed": False, "message": msg})

    return results
