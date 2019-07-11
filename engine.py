# -*- coding: utf-8 -*-
"""
Created on Tue Jun 18 20:28:25 2019

@author: theoldestnoob
"""

import tcod
import tcod.event
from random import randint

from entity import Entity, get_blocking_entities_at_location
from input_handlers import InputHandler
from render_functions import clear_all, render_all, display_space, blank_map
from render_functions import RenderOrder
from game_states import GameStates
from map_objects.game_map import GameMap
from map_objects.game_map_bsp import GameMapBSP
from map_objects.game_map_randomrooms import GameMapRandomRooms
from fov_functions import initialize_fov, init_fov_entity0, recompute_fov
from components.fighter import Fighter
from components.ai import IdleMonster
from death_functions import kill_entity


def main():
    # "global" variables
    debug_f = True
    seed = "testseed"
    screen_width = 80
    screen_height = 50
    map_width = 80
    map_height = 45

    fov_algorithm = 0
    fov_light_walls = True
    fov_radius = 10
    omnivision = False

    # various map settings - TODO: move to other module
    mapset_bsprect = {
            "room_max_size": 15,
            "room_min_size": 8,
            "min_rooms": 8,
            "max_rooms": 30,
            "ratio_vh": 1,
            "ratio_hv": 1,
            "ratio_d": 0,
            "hall_rand": False,
            "circ_rooms": 0,
            "rect_rooms": 1,
            "unused": True,
            "bsp_range": 0.15,
            "bsp_depth": 4,
            "max_monsters_per_room": 3
    }

    mapset_bspcirc = {
            "room_max_size": 26,
            "room_min_size": 8,
            "min_rooms": 8,
            "max_rooms": 30,
            "ratio_vh": 0,
            "ratio_hv": 0,
            "ratio_d": 1,
            "hall_rand": True,
            "circ_rooms": 1,
            "rect_rooms": 0,
            "unused": True,
            "bsp_range": 0.25,
            "bsp_depth": 4,
            "max_monsters_per_room": 3
    }

    mapset_bsprand = {
            "room_max_size": 20,
            "room_min_size": 6,
            "min_rooms": 5,
            "max_rooms": 30,
            "ratio_vh": 1,
            "ratio_hv": 1,
            "ratio_d": 1,
            "hall_rand": True,
            "circ_rooms": 1,
            "rect_rooms": 1,
            "unused": True,
            "bsp_range": 0.4,
            "bsp_depth": 4,
            "max_monsters_per_room": 3
    }

    mapset = mapset_bsprand

    colors = {
            "dark_wall": tcod.Color(0, 0, 100),
            "dark_ground": tcod.Color(50, 50, 150),
            "light_wall": tcod.Color(130, 110, 50),
            "light_ground": tcod.Color(200, 180, 50)
    }

    # setup object instantiation
    fighter_component = Fighter(hp=30, defense=2, power=5)
    ai_component = IdleMonster()
    player = Entity(0, 0, 0, "@", tcod.white, "Player", blocks=False,
                    render_order=RenderOrder.ACTOR)
    vip = Entity(1, 0, 0, "&", tcod.yellow, "VIP", blocks=True, soul=10,
                 fighter=fighter_component, ai=ai_component,
                 render_order=RenderOrder.ACTOR)
    entities = [player, vip]
    controlled_entity = player
    controlled_entity_index = 0
    game_state = GameStates.PLAYERS_TURN

    tcod.console_set_custom_font(
            "arial10x10.png",
            tcod.FONT_TYPE_GREYSCALE | tcod.FONT_LAYOUT_TCOD
            )

    action = {}

    in_handle = InputHandler()

    # open tcod console context
    with tcod.console_init_root(
            screen_width, screen_height,
            "libtcod tutorial revised",
            fullscreen=False,
            renderer=tcod.RENDERER_SDL2,
            vsync=False) as con:

        # create initial game map
        # game_map = GameMap(map_width, map_height, seed, con=con, debug=debug_f)
        # game_map = GameMapRandomRooms(map_width, map_height, seed, con=con, debug=debug_f)
        game_map = GameMapBSP(map_width, map_height, seed, con=con, debug=debug_f)
        game_map.make_map(player, entities, **mapset)

        # FOV calculation setup
        render_update = True

        for entity in entities:
            if entity.ident == 0:
                entity.fov_map = init_fov_entity0(game_map)
            else:
                entity.fov_map = initialize_fov(game_map)
            recompute_fov(game_map, entity, fov_radius, fov_light_walls,
                          fov_algorithm)

        # main game loop
        while True:

            # refresh graphics
            for entity in entities:
                if entity.fov_recompute:
                    render_update = True
                    recompute_fov(game_map, entity, fov_radius,
                                  fov_light_walls, fov_algorithm)
                    entity.fov_recompute = False

            render_all(con, entities, game_map, controlled_entity,
                       render_update, screen_width, screen_height, colors,
                       omnivision)

            tcod.console_flush()

            clear_all(con, entities)

            # get user input
            for event in tcod.event.get():
                in_handle.dispatch(event)

            action = in_handle.get_action()

            if debug_f and action:
                print(action)

            move = action.get("move")
            wait = action.get("wait")
            want_exit = action.get("exit")
            fullscreen = action.get("fullscreen")
            map_gen = action.get("map_gen")
            graph_gen = action.get("graph_gen")
            show_vertices = action.get("show_vertices")
            show_hyperedges = action.get("show_hyperedges")
            show_edges = action.get("show_edges")
            test = action.get("test")
            omnivis = action.get("omnivis")
            switch_char = action.get("switch_char")
            possess = action.get("possess")

            # handle user input
            turn_results = []

            if move:
                dx, dy = move
                dest_x = controlled_entity.x + dx
                dest_y = controlled_entity.y + dy
                # entity 0 can move through walls
                if controlled_entity.ident == 0:
                    target = get_blocking_entities_at_location(entities,
                                                               dest_x, dest_y)
                    if target:
                        turn_results.append({"message": f"A shudder runs through {target.name} as you press against its soul!"})
                    else:
                        controlled_entity.move(dx, dy)
                        game_state = GameStates.ENEMY_TURN
                else:
                    if not game_map.is_blocked(dest_x, dest_y):
                        target = get_blocking_entities_at_location(entities,
                                                                   dest_x,
                                                                   dest_y)
                        if target:
                            if controlled_entity.fighter:
                                attack_results = controlled_entity.fighter.attack(target)
                                turn_results.extend(attack_results)
                        else:
                            controlled_entity.move(dx, dy)

                        game_state = GameStates.ENEMY_TURN

            if wait:
                game_state = GameStates.ENEMY_TURN

            if possess:
                # get a direction to try to possess/leave
                while not move:
                    for event in tcod.event.get():
                        in_handle.dispatch(event)
                    action = in_handle.get_action()
                    move = action.get("move")
                dx, dy = move
                dest_x = controlled_entity.x + dx
                dest_y = controlled_entity.y + dy
                target = get_blocking_entities_at_location(entities,
                                                           dest_x, dest_y)
                # if currently entity 0, we're not possessing anyone
                if controlled_entity.ident == 0:
                    if target and target.soul > 0:
                        turn_results.append({"message": f"You possess the {target.name}!"})
                        controlled_entity = target
                        blank_map(con, game_map)
                    else:
                        turn_results.append({"message": f"Nothing there to possess!"})
                # otherwise, we are possessing someone and want to leave
                else:
                    if target:
                        turn_results.append({"message": f"That space is already occupied!"})
                    else:
                        turn_results.append({"message": f"You stop possessing the {controlled_entity.name}!"})
                        controlled_entity = entities[0]
                        controlled_entity.x = dest_x
                        controlled_entity.y = dest_y
                        controlled_entity.fov_recompute = True

            if game_state == GameStates.ENEMY_TURN:
                for entity in entities:
                    if entity.ai and entity is not controlled_entity:
                        enemy_results = entity.ai.take_turn(vip, game_map, entities)
                        turn_results.extend(enemy_results)
                game_state = GameStates.PLAYERS_TURN

            if turn_results:
                print(turn_results)
            for result in turn_results:
                # print(result)
                message = result.get("message")
                dead_entity = result.get("dead")

                if message:
                    print(message)
                if dead_entity:
                    if dead_entity == vip:
                        game_state = GameStates.FAIL_STATE
                    if dead_entity == controlled_entity:
                        controlled_entity = entities[0]
                        controlled_entity.x = dead_entity.x
                        controlled_entity.y = dead_entity.y
                        controlled_entity.fov_recompute = True
                    message = kill_entity(dead_entity)
                    print(message)

            if want_exit:
                return True
                raise SystemExit()

            if fullscreen:
                tcod.console_set_fullscreen(not tcod.console_is_fullscreen())

            if omnivis:
                if omnivision is True:
                    blank_map(con, game_map)
                omnivision = not omnivision

            if switch_char:
                controlled_entity_index += 1
                if controlled_entity_index >= len(entities):
                    controlled_entity_index = 0
                controlled_entity = entities[controlled_entity_index]
                blank_map(con, game_map)

            if map_gen:
                game_map.seed = randint(0, 99999)
                game_map.tiles = game_map.initialize_tiles()
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
                blank_map(con, game_map)

            if graph_gen:
                game_map.make_graph()

            if show_hyperedges and game_map.graph is not None:
                for edge in game_map.graph.hyperedges:
                    display_space(con, edge.space, tcod.green)
                    tcod.console_flush()
                    if debug_f:
                        print(f"***Hyperedge: {edge}")
                    while True:
                        for event in tcod.event.get():
                            in_handle.dispatch(event)
                        action = in_handle.get_action()
                        show_hyperedges = action.get("show_hyperedges")
                        want_exit = action.get("exit")
                        if want_exit:
                            return True
                        if show_hyperedges:
                            break
                    blank_map(con, game_map)
                    render_all(con, entities, game_map,
                               controlled_entity, render_update,
                               screen_width, screen_height, colors, omnivision)
                    tcod.console_flush()

            if show_edges and game_map.graph is not None:
                for edge in game_map.graph.edges:
                    display_space(con, edge.space, tcod.green)
                    tcod.console_flush()
                    if debug_f:
                        print(f"***Edge: {edge}")
                    while True:
                        for event in tcod.event.get():
                            in_handle.dispatch(event)
                        action = in_handle.get_action()
                        show_edges = action.get("show_edges")
                        want_exit = action.get("exit")
                        if want_exit:
                            return True
                        if show_edges:
                            break
                    blank_map(con, game_map)
                    render_all(con, entities, game_map,
                               controlled_entity, render_update,
                               screen_width, screen_height, colors, omnivision)
                    tcod.console_flush()

            if show_vertices and game_map.graph is not None:
                for vertex in game_map.graph.vertices:
                    display_space(con, vertex.space, tcod.green)
                    tcod.console_flush()
                    if debug_f:
                        print(f"***Vertex: {vertex}")
                    while True:
                        for event in tcod.event.get():
                            in_handle.dispatch(event)
                        action = in_handle.get_action()
                        show_vertices = action.get("show_vertices")
                        want_exit = action.get("exit")
                        if want_exit:
                            return True
                        if show_vertices:
                            break
                    blank_map(con, game_map)
                    render_all(con, entities, game_map,
                               controlled_entity, render_update,
                               screen_width, screen_height, colors, omnivision)
                    tcod.console_flush()

            if test:
                game_map.make_graph()
                print(game_map.graph.get_metrics())


if __name__ == "__main__":
    main()
