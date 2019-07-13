# -*- coding: utf-8 -*-
"""
Created on Fri Jul 12 22:46:03 2019

@author: theoldestnoob
"""

import tcod

from render_functions import blank_map, gray_map


# TODO: maybe break this up into one function to handle entity actions
#       and one to handle other non-entity actions (exit, omnivis, etc)?
def handle_actions(actions, in_handle, entities, game_map, console,
                   curr_entity, controlled_entity, omnivision, debug_f):
    action_cost = 0
    results = []
    next_turn = True
    curr_entity = curr_entity
    controlled_entity = controlled_entity
    omnivision = omnivision
    want_exit = False
    render_update = False

    for action in actions:
        # turn actions
        message = action.get("message")
        move = action.get("move")
        move_astar = action.get("move_astar")
        melee = action.get("melee")
        wait = action.get("wait")
        possess = action.get("possess")
        unpossess = action.get("unpossess")

        # out of turn actions
        want_exit = action.get("exit")
        fullscreen = action.get("fullscreen")

        # debug actions
        omnivis = action.get("omnivis")
        switch_char = action.get("switch_char")
        map_gen = action.get("map_gen")
        graph_gen = action.get("graph_gen")
        show_vertices = action.get("show_vertices")
        show_hyperedges = action.get("show_hyperedges")
        show_edges = action.get("show_edges")
        test = action.get("test")

        if message:  # {"message": message_string}
            results.append({"message": message})

        if move:  # {"move": (entity, dx, dy)}
            action_cost = 100
            next_turn = True
            entity, dx, dy = move
            entity.move(dx, dy)

        if move_astar:  # {"move_astar": (entity, target)}
            action_cost = 100
            next_turn = True
            entity, target = move_astar
            entity.move_astar(target, entities, game_map)

        if melee:  # {"melee": (entity, target)}
            action_cost = 100
            next_turn = True
            entity, target = melee
            melee_results = entity.fighter.attack(target)
            results.extend(melee_results)

        if wait:  # {"wait": int_time}
            action_cost = wait
            next_turn = True

        if possess:  # {"possess": target}
            action_cost = 100
            next_turn = True
            render_update = True
            target = possess
            results.append({"message": f"You possess the {target.name}!"})
            controlled_entity = target
            blank_map(console, game_map)

        if unpossess:  # {"unpossess": (dest_x, dest_y)}
            action_cost = 100
            next_turn = True
            render_update = True
            dest_x, dest_y = unpossess
            result_msg = f"You stop possessing the {controlled_entity.name}!"
            results.append({"message": result_msg})
            controlled_entity = entities[0]
            controlled_entity.x = dest_x
            controlled_entity.y = dest_y
            gray_map(console, game_map)
            controlled_entity.fov_recompute = True

        if want_exit:  # {"exit": True}
            want_exit = True

        if fullscreen:  # {"fullscreen": True}
            next_turn = False
            tcod.console_set_fullscreen(not tcod.console_is_fullscreen())

        if omnivis:  # {"omnivis": True}
            next_turn = False
            render_update = True
            if omnivision is True:
                if controlled_entity is entities[0]:
                    gray_map(console, game_map)
                else:
                    blank_map(console, game_map)
            omnivision = not omnivision

        if switch_char:  # {"switch_char": True}
            next_turn = False
            render_update = True
            index = controlled_entity.ident + 1
            if index >= len(entities):
                controlled_entity = entities[0]
            else:
                controlled_entity = entities[index]
            if controlled_entity is entities[0]:
                gray_map(console, game_map)
            else:
                blank_map(console, game_map)

        if map_gen:  # {"map_gen": True}
            pass

        if graph_gen:  # {"graph_gen": True}
            pass

        if show_vertices:  # {"show_vertices": True}
            pass

        if show_hyperedges:  # {"show_hyperedges": True}
            pass

        if show_edges:  # {"show_edges": True}
            pass

        if test:  # {"test": True}
            pass

    return (action_cost, results, next_turn, curr_entity, controlled_entity,
            omnivision, render_update, want_exit)
