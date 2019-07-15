# -*- coding: utf-8 -*-
"""
Created on Fri Jul 12 22:46:03 2019

@author: theoldestnoob
"""

import tcod
import tcod.event
from random import randint
from collections import deque

from render_functions import blank_map, gray_map, RenderOrder, display_space
from render_functions import render_all
from fov_functions import initialize_fov, init_fov_entity0, recompute_fov
from entity import Entity
from components.fighter import Fighter
from components.ai import IdleMonster
from game_messages import Message
from death_functions import kill_entity


# TODO: man I have to pass a lot of stuff in and out of these guys
#       there must be a better way?
def handle_entity_actions(actions, in_handle, entities, game_map, console,
                          message_log, controlled_entity, debug_f):
    action_cost = 0
    next_turn = True
    controlled_entity = controlled_entity
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
        dead = action.get("dead")

        if message:  # {"message": message_string}
            render_update = True
            message_log.add_message(message)

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
            actions.extend(melee_results)

        if wait:  # {"wait": int_time}
            action_cost = wait
            next_turn = True

        if possess:  # {"possess": target}
            action_cost = 100
            next_turn = True
            render_update = True
            target = possess
            result_str = f"You possess the {target.name}!"
            message_log.add_message(Message(result_str, tcod.light_gray))
            controlled_entity = target

        if unpossess:  # {"unpossess": (dest_x, dest_y)}
            action_cost = 100
            next_turn = True
            render_update = True
            dest_x, dest_y = unpossess
            result_str = f"You stop possessing the {controlled_entity.name}!"
            message_log.add_message(Message(result_str, tcod.light_gray))
            controlled_entity = entities[0]
            controlled_entity.x = dest_x
            controlled_entity.y = dest_y
            controlled_entity.fov_recompute = True

        if dead:  # {"dead": entity}
            render_update = True
            if dead == controlled_entity:
                controlled_entity = entities[0]
                controlled_entity.x = dead.x
                controlled_entity.y = dead.y
                controlled_entity.fov_recompute = True
            message = kill_entity(dead)
            message_log.add_message(message)

    return (action_cost, next_turn, controlled_entity, render_update)


def handle_player_actions(actions, in_handle, entities, game_map, console,
                          panel_ui, panel_map, curr_entity, controlled_entity,
                          player, vip, omnivision, mapset, message_log,
                          fov_radius, fov_light_walls, fov_algorithm,
                          screen_width, screen_height, colors,
                          timeq, bar_width, panel_ui_width, panel_ui_height,
                          panel_ui_y, panel_map_width, panel_map_height,
                          mouse_x, mouse_y, debug_f):
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
        mousemotion = action.get("mousemotion")

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

        # TODO: I'm not super happy about how this works
        #       but not sure how to elegantly tag render_update when the list
        #       of entities being moused over changes
        if mousemotion:  # {"mousemotion": (x, y)}
            render_update = True

        if omnivis:  # {"omnivis": True}
            next_turn = False
            render_update = True
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
            player_fighter = Fighter(hp=1, defense=0, power=0)
            vip_fighter = Fighter(hp=30, defense=2, power=5)
            player_ai = IdleMonster()
            vip_ai = IdleMonster()
            player = Entity(0, 0, 0, "@", tcod.white, "Player", blocks=False,
                            ai=player_ai, render_order=RenderOrder.ACTOR,
                            fighter=player_fighter, speed=25, soul=1)
            vip = Entity(1, 0, 0, "&", tcod.yellow, "VIP", blocks=True,
                         fighter=vip_fighter, ai=vip_ai, soul=10,
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
            for vertex in game_map.graph.vertices:
                display_space(console, vertex.space, tcod.green)
                tcod.console_flush()
                if debug_f:
                    print(f"***Vertex: {vertex}")
                while True:
                    for event in tcod.event.get():
                        in_handle.dispatch(event)
                    action = in_handle.get_user_input()
                    show_vertices = action.get("show_vertices")
                    want_exit = action.get("exit")
                    if show_vertices or want_exit:
                        break
                if want_exit:
                    break
                render_all(console, panel_ui, panel_map, entities, game_map,
                           controlled_entity, screen_width, screen_height,
                           bar_width, panel_ui_width, panel_ui_height,
                           panel_ui_y, panel_map_width, panel_map_height,
                           colors, message_log, mouse_x, mouse_y,
                           omnivision)
                tcod.console_flush()
            render_update = True

        if show_hyperedges:  # {"show_hyperedges": True}
            for edge in game_map.graph.hyperedges:
                display_space(console, edge.space, tcod.green)
                tcod.console_flush()
                if debug_f:
                    print(f"***Hyperedge: {edge}")
                while True:
                    for event in tcod.event.get():
                        in_handle.dispatch(event)
                    action = in_handle.get_user_input()
                    show_hyperedges = action.get("show_hyperedges")
                    want_exit = action.get("exit")
                    if show_hyperedges or want_exit:
                        break
                if want_exit:
                    break
                render_all(console, panel_ui, panel_map, entities, game_map,
                           controlled_entity, screen_width, screen_height,
                           bar_width, panel_ui_width, panel_ui_height,
                           panel_ui_y, panel_map_width, panel_map_height,
                           colors, message_log, mouse_x, mouse_y,
                           omnivision)
                tcod.console_flush()
            render_update = True

        if show_edges:  # {"show_edges": True}
            for edge in game_map.graph.edges:
                display_space(console, edge.space, tcod.green)
                tcod.console_flush()
                if debug_f:
                    print(f"***Edge: {edge}")
                while True:
                    for event in tcod.event.get():
                        in_handle.dispatch(event)
                    action = in_handle.get_user_input()
                    show_edges = action.get("show_edges")
                    want_exit = action.get("exit")
                    if show_edges or want_exit:
                        break
                if want_exit:
                    break
                render_all(console, panel_ui, panel_map, entities, game_map,
                           controlled_entity, screen_width, screen_height,
                           bar_width, panel_ui_width, panel_ui_height,
                           panel_ui_y, panel_map_width, panel_map_height,
                           colors, message_log, mouse_x, mouse_y,
                           omnivision)
                tcod.console_flush()
            render_update = True

        if test:  # {"test": True}
            pass

    return (next_turn, curr_entity, controlled_entity, entities, player, vip,
            timeq, omnivision, render_update, want_exit)
