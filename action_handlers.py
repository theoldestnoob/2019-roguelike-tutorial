# -*- coding: utf-8 -*-
"""
Created on Fri Jul 12 22:46:03 2019

@author: theoldestnoob
"""

import tcod
import tcod.event
from random import randint
from collections import deque

from render_functions import blank_map, gray_map, RenderOrder
from fov_functions import initialize_fov, init_fov_entity0, recompute_fov
from entity import Entity
from components.fighter import Fighter
from components.ai import IdleMonster


# TODO: maybe break this up into one function to handle entity actions
#       and one to handle other non-entity actions (exit, omnivis, etc)?
def handle_entity_actions(actions, in_handle, entities, game_map, console,
                          curr_entity, controlled_entity, omnivision, debug_f):
    action_cost = 0
    results = []
    next_turn = True
    curr_entity = curr_entity
    controlled_entity = controlled_entity
    omnivision = omnivision
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

    return (action_cost, results, next_turn, curr_entity, controlled_entity,
            omnivision, render_update)


def handle_player_actions(actions, in_handle, entities, game_map, console,
                          curr_entity, controlled_entity, player, vip,
                          omnivision, mapset, fov_radius, fov_light_walls,
                          fov_algorithm, timeq, debug_f):
    next_turn = False
    curr_entity = curr_entity
    controlled_entity = controlled_entity
    player = player
    vip = vip
    entities = entities
    omnivision = omnivision
    timeq = timeq
    want_exit = False
    render_update = False

    for action in actions:
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
            # only switch to controllable entities
            while controlled_entity.soul <= 0:
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
            next_turn = True
            render_update = True
            game_map.seed = randint(0, 99999)
            game_map.tiles = game_map.initialize_tiles()
            fighter_component = Fighter(hp=30, defense=2, power=5)
            player_ai = IdleMonster()
            vip_ai = IdleMonster()
            player = Entity(0, 0, 0, "@", tcod.white, "Player", blocks=False,
                            ai=player_ai, render_order=RenderOrder.ACTOR,
                            speed=25, soul=1)
            vip = Entity(1, 0, 0, "&", tcod.yellow, "VIP", blocks=True,
                         fighter=fighter_component, ai=vip_ai, soul=10,
                         render_order=RenderOrder.ACTOR)
            entities = [player, vip]
            controlled_entity = player
            game_map.make_map(player, entities, **mapset)
            for entity in entities:
                if entity.ident == 0:
                    entity.fov_map = init_fov_entity0(game_map)
                else:
                    entity.fov_map = initialize_fov(game_map)
                recompute_fov(game_map, entity, fov_radius,
                              fov_light_walls, fov_algorithm)
                print(f"{entity.name} AI: {entity.ai}")
            gray_map(console, game_map)
            timeq = deque(sorted(entities, key=lambda entity: entity.speed))
            curr_entity = timeq.popleft()

        if graph_gen:  # {"graph_gen": True}
            game_map.make_graph()

        if show_vertices:  # {"show_vertices": True}
            pass

        if show_hyperedges:  # {"show_hyperedges": True}
            pass

        if show_edges:  # {"show_edges": True}
            pass

        if test:  # {"test": True}
            pass

    return (next_turn, curr_entity, controlled_entity, entities, player, vip,
            timeq, omnivision, render_update, want_exit)
