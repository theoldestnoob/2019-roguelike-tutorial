# -*- coding: utf-8 -*-
"""
Created on Fri Jul 12 22:14:46 2019

@author: theoldestnoob
"""

import tcod

from entity import get_blocking_entities_at_location
from game_messages import Message
from game_states import GameStates


def parse_input(in_handle, user_in, curr_entity, entities, game_map,
                mouse_x, mouse_y, game_state, prev_state):
    # set up stuff
    actions = []
    mouse_x = mouse_x
    mouse_y = mouse_y

    # get user input details
    move = user_in.get("move")
    wait = user_in.get("wait")
    possess = user_in.get("possess")
    want_exit = user_in.get("exit")
    fullscreen = user_in.get("fullscreen")
    map_gen = user_in.get("map_gen")
    graph_gen = user_in.get("graph_gen")
    show_vertices = user_in.get("show_vertices")
    show_hyperedges = user_in.get("show_hyperedges")
    show_edges = user_in.get("show_edges")
    test = user_in.get("test")
    omnivis = user_in.get("omnivis")
    switch_char = user_in.get("switch_char")
    mouse_motion = user_in.get("mousemotion")
    msg_up = user_in.get("msg_up")
    msg_down = user_in.get("msg_down")
    pickup = user_in.get("pickup")
    show_inventory = user_in.get("show_inventory")
    drop_inventory = user_in.get("drop_inventory")
    inventory_index = user_in.get("inventory_index")

    # put together actions based on user input
    if move:
        dx, dy = move
        dest_x = curr_entity.x + dx
        dest_y = curr_entity.y + dy
        # entity 0 can move through walls
        if curr_entity.ident == 0:
            target = get_blocking_entities_at_location(entities,
                                                       dest_x, dest_y)
            if target:
                act_msg = (f"A shudder runs through {target.name} "
                           f"as you press against its soul!")
                actions.append({"message": Message(act_msg, tcod.light_gray)})
            else:
                actions.append({"move": (curr_entity, dx, dy)})
        else:
            if not game_map.is_blocked(dest_x, dest_y):
                target = get_blocking_entities_at_location(entities,
                                                           dest_x,
                                                           dest_y)
                if target:
                    if curr_entity.fighter:
                        actions.append({"melee": (curr_entity, target)})
                else:
                    actions.append({"move": (curr_entity, dx, dy)})

    if wait:
        actions.append({"message":
                        Message(f"{curr_entity.name} waits.", tcod.white)})
        actions.append({"wait": 100})
        # TODO: potential future waits of variable length
        #       or normalized to entity speed

    if possess:
        # get a direction to try to possess/leave
        while not move:
            for event in tcod.event.get():
                in_handle.dispatch(event)
            user_in = in_handle.get_user_input()
            move = user_in.get("move")
        dx, dy = move
        dest_x = curr_entity.x + dx
        dest_y = curr_entity.y + dy
        target = get_blocking_entities_at_location(entities,
                                                   dest_x, dest_y)
        # if currently entity 0, we're not possessing anyone
        if curr_entity.ident == 0:
            if target and target.soul > 0:
                actions.append({"possess": target})
            else:
                actions.append({"message":
                                Message(f"Nothing there to possess!",
                                        tcod.light_gray)})
        # otherwise, we are possessing someone and want to leave
        else:
            if target:
                actions.append({"message":
                                Message(f"That space is already occupied!",
                                        tcod.light_gray)})
            else:
                actions.append({"unpossess": (dest_x, dest_y)})

    if (inventory_index is not None
            and game_state == GameStates.SHOW_INVENTORY
            and prev_state != GameStates.FAIL_STATE):
        if inventory_index < len(curr_entity.inventory.items):
            item = curr_entity.inventory.items[inventory_index]
            actions.append({"use_item": item})

    if (inventory_index is not None
            and game_state == GameStates.DROP_INVENTORY
            and prev_state != GameStates.FAIL_STATE):
        if inventory_index < len(curr_entity.inventory.items):
            item = curr_entity.inventory.items[inventory_index]
            actions.append({"drop_item": item})

    if curr_entity.ident != 0 and show_inventory:
        actions.append(user_in)

    if curr_entity.ident != 0 and drop_inventory:
        actions.append(user_in)

    # TODO: I don't like having to pass actions through like this
    if (want_exit or fullscreen or omnivis or switch_char or map_gen
            or graph_gen or test or msg_up or msg_down or pickup
            or inventory_index is not None):
        actions.append(user_in)

    if ((show_hyperedges or show_edges or show_vertices)
            and game_map.graph is not None):
        actions.append(user_in)

    if mouse_motion:
        x, y = mouse_motion
        if x != mouse_x or y != mouse_y:
            mouse_x = x
            mouse_y = y
        actions.append({"mousemotion": (x, y)})

    return actions, mouse_x, mouse_y
