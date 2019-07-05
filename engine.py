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
from game_states import GameStates
from map_objects.game_map import GameMap
from map_objects.game_map_bsp import GameMapBSP
from map_objects.game_map_randomrooms import GameMapRandomRooms
from fov_functions import initialize_fov, recompute_fov


def main():
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

    player = Entity(0, 0, 0, "@", tcod.white, "Player", blocks=False)
    vip = Entity(1, 0, 0, "&", tcod.yellow, "VIP", blocks=True)
    entities = [player, vip]
    controlled_entity = player
    controlled_entity_index = 0
    game_state = GameStates.PLAYERS_TURN

    tcod.console_set_custom_font(
            "arial10x10.png",
            tcod.FONT_TYPE_GREYSCALE | tcod.FONT_LAYOUT_TCOD
            )

    # game_map = GameMapRandomRooms(map_width, map_height, seed, con)
    # game_map.make_map(player, **mapset)

    action = {}

    in_handle = InputHandler()

    with tcod.console_init_root(
            screen_width, screen_height,
            "libtcod tutorial revised",
            fullscreen=False,
            renderer=tcod.RENDERER_SDL2,
            vsync=False) as con:

        # game_map = GameMap(map_width, map_height, seed, con=con, debug=debug_f)
        # game_map = GameMapRandomRooms(map_width, map_height, seed, con=con, debug=debug_f)
        game_map = GameMapBSP(map_width, map_height, seed, con=con, debug=debug_f)
        game_map.make_map(player, entities, **mapset)

        fov_recompute = True

        for entity in entities:
            entity.fov_map = initialize_fov(game_map)

        while True:

            if fov_recompute:
                recompute_fov(controlled_entity, fov_radius,
                              fov_light_walls, fov_algorithm)

            render_all(con, entities, game_map, controlled_entity,
                       fov_recompute, screen_width, screen_height, colors,
                       omnivision)

            tcod.console_flush()

            clear_all(con, entities)

            for event in tcod.event.get():
                in_handle.dispatch(event)

            action = in_handle.get_action()

            if debug_f and action:
                print(action)

            move = action.get("move")
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

            if move:
                dx, dy = move
                dest_x = controlled_entity.x + dx
                dest_y = controlled_entity.y + dy
                if not game_map.is_blocked(dest_x, dest_y):
                    target = get_blocking_entities_at_location(entities,
                                                               dest_x, dest_y)
                    if target:
                        print(f"You kick the {target.name} in the shins, much to its annoyance!")
                    else:
                        controlled_entity.move(dx, dy)
                        fov_recompute = True

                    game_state = GameStates.ENEMY_TURN

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
                    entity.fov_map = initialize_fov(game_map)
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
                               controlled_entity, fov_recompute,
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
                               controlled_entity, fov_recompute,
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
                               controlled_entity, fov_recompute,
                               screen_width, screen_height, colors, omnivision)
                    tcod.console_flush()

            if test:
                game_map.make_graph()
                print(game_map.graph.get_metrics())

            if game_state == GameStates.ENEMY_TURN:
                for entity in entities:
                    if entity is not controlled_entity:
                        print(f"The {entity.name} ponders the meaning of its existence.")
                game_state = GameStates.PLAYERS_TURN


if __name__ == "__main__":
    main()
