# -*- coding: utf-8 -*-
"""
Created on Tue Jun 18 20:28:25 2019

@author: theoldestnoob
"""

import tcod
import tcod.event
from collections import deque

from entity import Entity
from input_handlers import InputHandler
from input_parsers import parse_input
from render_functions import clear_all, render_all, RenderOrder
from game_states import GameStates
from map_objects.game_map import GameMap
from map_objects.game_map_bsp import GameMapBSP
from map_objects.game_map_randomrooms import GameMapRandomRooms
from fov_functions import initialize_fov, init_fov_entity0, recompute_fov
from components.fighter import Fighter
from components.ai import IdleMonster
from action_handlers import handle_entity_actions, handle_player_actions
from game_messages import MessageLog, Message


def main():
    # "global" variables
    debug_f = True
    seed = "testseed"
    screen_width = 80
    screen_height = 50

    bar_width = 20
    panel_ui_width = screen_width
    panel_ui_height = 7
    panel_ui_y = screen_height - panel_ui_height

    message_x = bar_width + 2
    message_width = screen_width - bar_width - 2
    message_height = panel_ui_height - 1

    panel_map_width = 80
    panel_map_height = 43

    map_width = 80
    map_height = 43

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
    player_fighter = Fighter(hp=1, defense=0, power=0)
    vip_fighter = Fighter(hp=30, defense=2, power=5)
    player_ai = IdleMonster()
    vip_ai = IdleMonster()
    player = Entity(0, 0, 0, "@", tcod.white, "Player", blocks=False, soul=1,
                    fighter=player_fighter, ai=player_ai,
                    render_order=RenderOrder.ACTOR, speed=25)
    vip = Entity(1, 0, 0, "&", tcod.yellow, "VIP", blocks=True, soul=10,
                 fighter=vip_fighter, ai=vip_ai,
                 render_order=RenderOrder.ACTOR)
    entities = [player, vip]
    controlled_entity = player
    game_state = GameStates.PLAYERS_TURN

    tcod.console_set_custom_font(
            "arial10x10.png",
            tcod.FONT_TYPE_GREYSCALE | tcod.FONT_LAYOUT_TCOD
            )

    in_handle = InputHandler()

    message_log = MessageLog(message_x, message_width, message_height)
    mouse_x = 0
    mouse_y = 0

    # open tcod console context
    with tcod.console_init_root(
            screen_width, screen_height,
            "libtcod tutorial revised",
            fullscreen=False,
            renderer=tcod.RENDERER_SDL2,
            vsync=False) as con:

        # set up ui
        panel_ui = tcod.console.Console(panel_ui_width, panel_ui_height)
        panel_map = tcod.console.Console(panel_map_width, panel_map_height)

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
                render_all(con, panel_ui, panel_map, entities, game_map,
                           controlled_entity,
                           screen_width, screen_height, bar_width,
                           panel_ui_width, panel_ui_height, panel_ui_y,
                           panel_map_width, panel_map_height,
                           colors, message_log,
                           mouse_x, mouse_y, omnivision)
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

                input_r = parse_input(in_handle, user_in, curr_entity,
                                      entities, game_map, mouse_x, mouse_y)
                actions, mouse_x, mouse_y = input_r

                # process any player-only actions
                act_r = handle_player_actions(actions, in_handle, entities,
                                              game_map, con, panel_ui,
                                              panel_map,
                                              curr_entity, controlled_entity,
                                              player, vip, omnivision, mapset,
                                              message_log,
                                              fov_radius, fov_light_walls,
                                              fov_algorithm, screen_width,
                                              screen_height, colors, timeq,
                                              bar_width, panel_ui_width,
                                              panel_ui_height, panel_ui_y,
                                              panel_map_width,
                                              panel_map_height,
                                              mouse_x, mouse_y,
                                              debug_f)
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
                                          game_map, con, message_log,
                                          controlled_entity, debug_f)

            action_cost, next_turn, controlled_entity, render_update_e = act_r

            render_update = render_update_p or render_update_e

            # process turn results
            if want_exit:
                return True

            if debug_f and results:
                print(results)

            # TODO: check for and handle failure states
            if ((not vip.fighter or vip.fighter.hp <= 0)
                    and game_state != GameStates.FAIL_STATE):
                message_log.add_message(Message("Oh no you lose!", tcod.red))
                game_state = GameStates.FAIL_STATE
                render_update = True

            # put current entity back in time queue and get the next one
            if next_turn:
                # we do not reinsert entities with 0 speed
                if curr_entity.speed != 0:
                    curr_entity.time_to_act = action_cost // curr_entity.speed
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
