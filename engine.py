# -*- coding: utf-8 -*-
"""
Created on Tue Jun 18 20:28:25 2019

@author: theoldestnoob
"""

import tcod
import tcod.event
from collections import deque

from loader_functions.initialize_new_game import get_constants
from entity import Entity
from input_handlers import InputHandler
from input_parsers import parse_input
from render_functions import render_all, RenderOrder
from game_states import GameStates
from map_objects.game_map import GameMap
from map_objects.game_map_bsp import GameMapBSP
from map_objects.game_map_randomrooms import GameMapRandomRooms
from fov_functions import initialize_fov, init_fov_entity0, recompute_fov
from components.fighter import Fighter
from components.ai import IdleMonster
from action_handlers import handle_entity_actions, handle_player_actions
from game_messages import MessageLog, Message
from components.inventory import Inventory


def main():
    debug_f = True
    omnivision = False
    # get our big dict of settings
    constants = get_constants()

    # setup object instantiation
    player_fighter = Fighter(hp=1, defense=0, power=0)
    vip_fighter = Fighter(hp=30, defense=2, power=5)
    player_ai = IdleMonster()
    vip_ai = IdleMonster()
    vip_inventory = Inventory(26)
    player = Entity(0, 0, 0, "@", tcod.white, "Player", blocks=False, soul=1,
                    fighter=player_fighter, ai=player_ai,
                    render_order=RenderOrder.ACTOR, speed=25)
    vip = Entity(1, 0, 0, "&", tcod.yellow, "VIP", blocks=True, soul=10,
                 fighter=vip_fighter, ai=vip_ai, inventory=vip_inventory,
                 render_order=RenderOrder.ACTOR)
    entities = [player, vip]
    controlled_entity = player
    game_state = GameStates.NORMAL_TURN
    prev_state = GameStates.NORMAL_TURN

    tcod.console_set_custom_font(
            "arial10x10.png",
            tcod.FONT_TYPE_GREYSCALE | tcod.FONT_LAYOUT_TCOD
            )

    in_handle = InputHandler()

    message_log = MessageLog(constants["message_x"],
                             constants["message_width"],
                             constants["message_height"], 100)
    mouse_x = 0
    mouse_y = 0

    # open tcod console context
    with tcod.console_init_root(
            constants["screen_width"], constants["screen_height"],
            constants["window_title"], fullscreen=False,
            renderer=tcod.RENDERER_SDL2, vsync=False) as root_console:

        # set up ui
        panel_ui = tcod.console.Console(constants["panel_ui_width"],
                                        constants["panel_ui_height"])
        panel_map = tcod.console.Console(constants["panel_map_width"],
                                         constants["panel_map_height"])

        # create initial game map
        # game_map = GameMap(map_width, map_height, seed, con=con, debug=debug_f)
        # game_map = GameMapRandomRooms(map_width, map_height, seed, con=con, debug=debug_f)
        game_map = GameMapBSP(constants["map_width"], constants["map_height"],
                              constants["seed"], con=root_console,
                              debug=debug_f)
        game_map.make_map(player, entities, **constants["mapset"])

        # set up time system
        actors = [e for e in entities if e.ai]
        timeq = deque(sorted(actors, key=lambda entity: entity.time_to_act))
        curr_entity = timeq.popleft()
        next_turn = True

        # FOV calculation setup
        render_update = True

        for entity in actors:
            if entity.ident == 0:
                entity.fov_map = init_fov_entity0(game_map)
            else:
                entity.fov_map = initialize_fov(game_map)
            recompute_fov(game_map, entity, constants["fov_radius"],
                          constants["fov_light_walls"],
                          constants["fov_algorithm"])

        # TODO: there has to be a better way to handle targeting than this
        targeting_item = None

        # main game loop
        while True:

            # refresh graphics
            for entity in entities:
                if entity.fov_map and entity.fov_recompute:
                    render_update = True
                    recompute_fov(game_map, entity, constants["fov_radius"],
                                  constants["fov_light_walls"],
                                  constants["fov_algorithm"])
                    entity.fov_recompute = False
            if render_update:
                if debug_f:
                    print("RENDER UPDATE")
                render_all(root_console, panel_ui, panel_map, entities,
                           game_map, controlled_entity, constants, omnivision,
                           message_log, mouse_x, mouse_y, game_state)
                tcod.console_flush()
                render_update = False

            # run an entity's turn
            actions = {}
            results = []

            # if it's the controlled entity's turn
            if curr_entity is controlled_entity:
                # get the actions the player wants to take
                next_turn = False
                # get user input
                in_handle.set_game_state(game_state)
                for event in tcod.event.get():
                    in_handle.dispatch(event)

                user_in = in_handle.get_user_input()

                if debug_f and user_in:
                    print(user_in)

                input_r = parse_input(panel_map, in_handle, user_in,
                                      curr_entity,
                                      entities, game_map, mouse_x, mouse_y,
                                      game_state, prev_state, targeting_item)
                actions, mouse_x, mouse_y = input_r

                # process any player-only actions
                act_r = handle_player_actions(actions, in_handle, entities,
                                              game_map, root_console,
                                              panel_ui, panel_map,
                                              curr_entity, controlled_entity,
                                              player, vip, omnivision,
                                              message_log, mouse_x, mouse_y,
                                              timeq, game_state, prev_state,
                                              constants, debug_f)
                (next_turn, curr_entity, controlled_entity, entities, player,
                 vip, timeq, omnivision, render_update_p, want_exit,
                 game_state, prev_state) = act_r

            # if it's not the controlled entity's turn
            elif curr_entity.ai:
                # get the actions the entity wants to take
                actions = curr_entity.ai.take_turn(vip, game_map, entities)

            if debug_f and actions:
                print(f"{curr_entity}: {actions}")

            # process turn actions, modify game state, and get results
            act_r = handle_entity_actions(actions, in_handle, entities,
                                          game_map, root_console, message_log,
                                          controlled_entity, game_state,
                                          prev_state, targeting_item, debug_f)

            (action_cost, next_turn, controlled_entity, render_update_e,
             game_state, prev_state, targeting_item) = act_r

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
