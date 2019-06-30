# -*- coding: utf-8 -*-
"""
Created on Tue Jun 18 20:28:25 2019

@author: theoldestnoob
"""

import tcod
import tcod.event
from random import randint

from entity import Entity
from input_handlers import InputHandler
from render_functions import clear_all, render_all, display_space
from map_objects.game_map import GameMap
from map_objects.game_map_bsp import GameMapBSP
from map_objects.game_map_randomrooms import GameMapRandomRooms


def main():
    screen_width = 80
    screen_height = 50
    map_width = 80
    map_height = 45
    seed = "testseed"
    debug_f = False

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
            "bsp_depth": 4
    }

    mapset_bspcirc = {
            "room_max_size": 28,
            "room_min_size": 12,
            "min_rooms": 6,
            "max_rooms": 30,
            "ratio_vh": 0,
            "ratio_hv": 0,
            "ratio_d": 1,
            "hall_rand": True,
            "circ_rooms": 1,
            "rect_rooms": 0,
            "unused": True,
            "bsp_range": 0.15,
            "bsp_depth": 4
    }

    mapset_bsprand = {
            "room_max_size": 15,
            "room_min_size": 8,
            "min_rooms": 8,
            "max_rooms": 30,
            "ratio_vh": 1,
            "ratio_hv": 1,
            "ratio_d": 1,
            "hall_rand": True,
            "circ_rooms": 1,
            "rect_rooms": 1,
            "unused": True,
            "bsp_range": 0.15,
            "bsp_depth": 4
    }

    mapset = mapset_bsprect

    colors = {
            "dark_wall": tcod.Color(0, 0, 100),
            "dark_ground": tcod.Color(50, 50, 150)
    }

    player = Entity(int(map_width / 2), int(map_height / 2), "@",
                    tcod.white)
    npc = Entity(int(map_width / 2 - 5), int(map_height / 2), "@",
                 tcod.yellow)
    entities = [player, npc]

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
        game_map.make_map(player, **mapset)

        while True:

            render_all(con, entities, game_map, screen_width, screen_height,
                       colors)

            tcod.console_flush()

            clear_all(con, entities)

            for event in tcod.event.get():
                in_handle.dispatch(event)

            action = in_handle.get_action()

            # debug output
            if(action):
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

            if move:
                dx, dy = move
                if not game_map.is_blocked(player.x + dx, player.y + dy):
                    player.move(dx, dy)

            if want_exit:
                return True
                raise SystemExit()

            if fullscreen:
                tcod.console_set_fullscreen(not tcod.console_is_fullscreen())

            if map_gen:
                game_map.seed = randint(0, 99999)
                game_map.tiles = game_map.initialize_tiles()
                game_map.make_map(player, **mapset)

            if graph_gen:
                game_map.make_graph()

            if show_hyperedges and game_map.graph is not None:
                for edge in game_map.graph.hyperedges:
                    display_space(con, edge.space, tcod.green)
                    tcod.console_flush()
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
                    render_all(con, entities, game_map, screen_width,
                               screen_height, colors)
                    tcod.console_flush()

            if show_edges and game_map.graph is not None:
                for edge in game_map.graph.edges:
                    display_space(con, edge.space, tcod.green)
                    tcod.console_flush()
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
                    render_all(con, entities, game_map, screen_width,
                               screen_height, colors)
                    tcod.console_flush()

            if show_vertices and game_map.graph is not None:
                for vertex in game_map.graph.vertices:
                    display_space(con, vertex.space, tcod.green)
                    tcod.console_flush()
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
                    render_all(con, entities, game_map, screen_width,
                               screen_height, colors)
                    tcod.console_flush()

            if test:
                tiles = game_map.game_map_to_bool_array()
                print(f"MapGraph({tiles}, {game_map.rooms})")
                pass


if __name__ == "__main__":
    main()
