# -*- coding: utf-8 -*-
"""
Created on Tue Jun 18 20:28:25 2019

@author: theoldestnoob
"""

import tcod
import tcod.event

from loader_functions.initialize_new_game import get_constants
from loader_functions.initialize_new_game import get_game_variables
from loader_functions.data_loaders import save_game, load_game
from input_handlers import InputHandler
from input_parsers import parse_input
from render_functions import render_all
from game_states import GameStates
from fov_functions import recompute_fov
from action_handlers import handle_entity_actions, handle_player_actions
from game_messages import Message
from menus import main_menu, message_box


def main():
    # game "constants" / "globals" setup
    debug_f = True
    omnivision = False
    constants = get_constants()

    # initial game state
    game_state = GameStates.MAIN_MENU
    show_load_error_message = False

    # input handling setup
    in_handle = InputHandler()
    mouse_x = 0
    mouse_y = 0

    # set tcod font
    tcod.console_set_custom_font(
            "arial10x10.png",
            tcod.FONT_TYPE_GREYSCALE | tcod.FONT_LAYOUT_TCOD
            )

    # set up ui elements
    panel_ui = tcod.console.Console(constants["panel_ui_width"],
                                    constants["panel_ui_height"])
    panel_map = tcod.console.Console(constants["panel_map_width"],
                                     constants["panel_map_height"])
    main_menu_bg = tcod.image_load("menu_background1.png")

    # open tcod console context
    with tcod.console_init_root(
            constants["screen_width"], constants["screen_height"],
            constants["window_title"], fullscreen=False,
            renderer=tcod.RENDERER_SDL2, vsync=False) as root_console:

        while True:
            if game_state == GameStates.MAIN_MENU:
                in_handle.set_game_state(game_state)
                main_menu(root_console, main_menu_bg,
                          constants["screen_width"],
                          constants["screen_height"])

                if show_load_error_message:
                    message_box(root_console, "No save game to load", 50,
                                constants["screen_width"],
                                constants["screen_height"])

                tcod.console_flush()

                for event in tcod.event.get():
                    in_handle.dispatch(event)

                user_in = in_handle.get_user_input()

                want_exit = user_in.get("exit")
                new_game = user_in.get("new_game")
                load_save = user_in.get("load_game")

                if (show_load_error_message
                        and (new_game or load_save or want_exit)):
                    show_load_error_message = False
                elif want_exit:
                    return
                elif new_game:
                    # set up game "runtime global" variables from scratch
                    g_var = get_game_variables(constants, root_console,
                                               panel_map, debug_f)
                    (player, entities, controlled_entity, curr_entity,
                     game_state, prev_state, message_log, game_map, timeq,
                     next_turn, render_update, targeting_item) = g_var
                elif load_save:
                    # load game "runtime global" variables from save file
                    try:
                        g_var = load_game(constants)
                    except FileNotFoundError:
                        show_load_error_message = True

                    if not show_load_error_message:
                        (player, entities, controlled_entity, curr_entity,
                         game_state, prev_state, message_log, game_map, timeq,
                         next_turn, render_update, targeting_item) = g_var
                    else:
                        game_state = GameStates.MAIN_MENU

            else:
                play_game(constants, root_console, panel_ui, panel_map, debug_f,
                          omnivision, in_handle, mouse_x, mouse_y,
                          player, entities, controlled_entity, curr_entity,
                          game_state, prev_state, message_log, game_map, timeq,
                          next_turn, render_update, targeting_item)
                game_state = GameStates.MAIN_MENU


def play_game(constants, root_console, panel_ui, panel_map, debug_f,
              omnivision, in_handle, mouse_x, mouse_y,
              player, entities, controlled_entity, curr_entity,
              game_state, prev_state, message_log, game_map, timeq,
              next_turn, render_update, targeting_item):
    # always update rendering upon entry
    render_update = True
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
                                          player, omnivision,
                                          message_log, mouse_x, mouse_y,
                                          timeq, game_state, prev_state,
                                          constants, debug_f)
            (next_turn, curr_entity, controlled_entity, entities, player,
             timeq, omnivision, render_update_p, want_exit,
             game_state, prev_state) = act_r

        # if it's not the controlled entity's turn
        elif curr_entity.ai:
            # get the actions the entity wants to take
            actions = curr_entity.ai.take_turn(player, game_map, entities)

        if debug_f and actions:
            print(f"{curr_entity.name} - {curr_entity}: {actions}")

        # process turn actions, modify game state, and get results
        act_r = handle_entity_actions(actions, in_handle, entities, timeq,
                                      game_map, root_console, message_log,
                                      controlled_entity, player, game_state,
                                      prev_state, targeting_item, debug_f)

        (action_cost, next_turn, controlled_entity, render_update_e,
         game_state, prev_state, targeting_item) = act_r

        render_update = render_update_p or render_update_e

        # process turn results
        if want_exit:
            save_game(player, entities, controlled_entity, curr_entity,
                      game_state, prev_state, message_log, game_map, timeq,
                      next_turn, render_update, targeting_item)
            return True

        if debug_f and results:
            print(results)

        # TODO: check for and handle failure states
        if ((not player.fighter or player.fighter.hp <= 0)
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
