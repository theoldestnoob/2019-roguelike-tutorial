# -*- coding: utf-8 -*-
"""
Created on Tue Jun 18 20:28:25 2019

@author: theoldestnoob
"""

import tcod
import tcod.event
from random import randint
from collections import deque

from entity import Entity, get_blocking_entities_at_location
from input_handlers import InputHandler
from input_parsers import parse_input
from render_functions import clear_all, render_all, display_space, blank_map
from render_functions import RenderOrder, gray_map
from game_states import GameStates
from map_objects.game_map import GameMap
from map_objects.game_map_bsp import GameMapBSP
from map_objects.game_map_randomrooms import GameMapRandomRooms
from fov_functions import initialize_fov, init_fov_entity0, recompute_fov
from components.fighter import Fighter
from components.ai import IdleMonster
from death_functions import kill_entity
from action_handlers import handle_entity_actions, handle_player_actions


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
    player_ai = IdleMonster()
    vip_ai = IdleMonster()
    player = Entity(0, 0, 0, "@", tcod.white, "Player", blocks=False, soul=1,
                    ai=player_ai, render_order=RenderOrder.ACTOR, speed=25)
    vip = Entity(1, 0, 0, "&", tcod.yellow, "VIP", blocks=True, soul=10,
                 fighter=fighter_component, ai=vip_ai,
                 render_order=RenderOrder.ACTOR)
    entities = [player, vip]
    controlled_entity = player
    game_state = GameStates.PLAYERS_TURN

    tcod.console_set_custom_font(
            "arial10x10.png",
            tcod.FONT_TYPE_GREYSCALE | tcod.FONT_LAYOUT_TCOD
            )

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

        # gray out initial map view
        gray_map(con, game_map)

        # FOV calculation setup
        render_update = True

        for entity in entities:
            if entity.ident == 0:
                entity.fov_map = init_fov_entity0(game_map)
            else:
                entity.fov_map = initialize_fov(game_map)
            recompute_fov(game_map, entity, fov_radius, fov_light_walls,
                          fov_algorithm)

        # set up time system
        timeq = deque(sorted(entities, key=lambda entity: entity.time_to_act))
        curr_entity = timeq.popleft()
        next_turn = True

        # main game loop
        while True:

            # refresh graphics
            for entity in entities:
                if entity.fov_recompute:
                    render_update = True
                    recompute_fov(game_map, entity, fov_radius,
                                  fov_light_walls, fov_algorithm)
                    entity.fov_recompute = False
            if render_update:
                if debug_f:
                    print("RENDER UPDATE")
                render_all(con, entities, game_map, controlled_entity,
                           screen_width, screen_height, colors, omnivision)
                tcod.console_flush()
                clear_all(con, entities)
                render_update = False

            # run an entity's turn
            actions = {}
            results = []

            # if it's the controlled entity's turn
            if curr_entity is controlled_entity:
                # get the actions the player wants to take
                next_turn = False
                # get user input
                for event in tcod.event.get():
                    in_handle.dispatch(event)

                user_in = in_handle.get_user_input()

                if debug_f and user_in:
                    print(user_in)

                actions = parse_input(in_handle, user_in, curr_entity,
                                      entities, game_map)

                # process any player-only actions
                act_r = handle_player_actions(actions, in_handle, entities,
                                              game_map, con, curr_entity,
                                              controlled_entity, player, vip,
                                              omnivision, mapset, fov_radius,
                                              fov_light_walls, fov_algorithm,
                                              timeq, debug_f)
                (next_turn, curr_entity, controlled_entity, entities, player,
                 vip, timeq, omnivision, render_update_p, want_exit) = act_r

            # if it's not the controlled entity's turn
            elif curr_entity.ai:
                # get the actions the entity wants to take
                actions = curr_entity.ai.take_turn(vip, game_map, entities)

            if debug_f and actions:
                print(f"{curr_entity}: {actions}")

            # process turn actions, modify game state, and get results
            act_r = handle_entity_actions(actions, in_handle, entities,
                                          game_map, con, curr_entity,
                                          controlled_entity, omnivision,
                                          debug_f)
            (action_cost, results, next_turn, curr_entity, controlled_entity,
             omnivision, render_update_e) = act_r

            render_update = render_update_p or render_update_e

            # process turn results
            if want_exit:
                return True

            if debug_f and results:
                print(results)

            # TODO: do I even really need this? should I just handle it all in
            #       handle_actions?
            for result in results:
                message = result.get("message")
                dead_entity = result.get("dead")

                if message:
                    print(message)
                if dead_entity:
                    render_update = True
                    if dead_entity == vip:
                        game_state = GameStates.FAIL_STATE
                    if dead_entity == controlled_entity:
                        controlled_entity = entities[0]
                        controlled_entity.x = dead_entity.x
                        controlled_entity.y = dead_entity.y
                        gray_map(con, game_map)
                        controlled_entity.fov_recompute = True
                    message = kill_entity(dead_entity)
                    print(message)

            # put current entity back in time queue and get the next one
            if next_turn:
                # we do not reinsert entities with 0 speed
                if curr_entity.speed != 0:
                    curr_entity.time_to_act = int(action_cost / curr_entity.speed)
                    # future: action_cost / curr_entity.speed
                    for index, entity in enumerate(timeq):
                        if entity.time_to_act > curr_entity.time_to_act:
                            timeq.insert(index, curr_entity)
                            break
                    else:
                        timeq.append(curr_entity)
                # get our next entity
                curr_entity = timeq.popleft()
                # count down everyone's time to act
                time_tick = curr_entity.time_to_act
                for entity in timeq:
                    entity.time_to_act -= time_tick
                    if entity.time_to_act < 0:
                        entity.time_to_act = 0


if __name__ == "__main__":
    main()
