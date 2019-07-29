# -*- coding: utf-8 -*-
"""
Created on Tue Jun 18 21:35:02 2019

@author: theoldestnoob
"""

import tcod.event

from game_states import GameStates


class InputHandler(tcod.event.EventDispatch):

    def __init__(self):
        self._user_in_q = []
        self.state = GameStates.NORMAL_TURN

    def ev_quit(self, event):
        raise SystemExit()

    def ev_keydown(self, event):
        keymap_nomod = None
        keymap_lalt = None
        keymap_shift = None
        # get key mapping depending on game state
        if self.state == GameStates.NORMAL_TURN:
            keymap_nomod = normal_keymap_nomod
            keymap_lalt = normal_keymap_lalt
            keymap_shift = normal_keymap_shift

        elif self.state in (GameStates.SHOW_INVENTORY,
                            GameStates.DROP_INVENTORY):
            inv_index = event.sym - ord("a")
            if 0 <= inv_index < 26:
                self._user_in_q.append({"inventory_index": inv_index})

        elif self.state == GameStates.FAIL_STATE:
            keymap_nomod = fail_keymap_nomod
            keymap_lalt = fail_keymap_lalt

        elif self.state == GameStates.TARGETING:
            keymap_nomod = target_keymap_nomod

        elif self.state == GameStates.MAIN_MENU:
            keymap_nomod = menu_keymap_nomod

        elif self.state == GameStates.LEVEL_UP:
            keymap_nomod = level_up_keymap_nomod

        if keymap_nomod is None:
            keymap_nomod = default_keymap_nomod
        if keymap_lalt is None:
            keymap_lalt = default_keymap_lalt
        if keymap_shift is None:
            keymap_shift = default_keymap_shift

        # check and process any mapped modified keys
        if (event.mod & tcod.event.KMOD_LALT
                and event.sym in keymap_lalt.keys()):
            self._user_in_q.append(keymap_lalt[event.sym])
        elif (event.mod & tcod.event.KMOD_SHIFT
              and event.sym in keymap_shift.keys()):
            self._user_in_q.append(keymap_shift[event.sym])
        # if no mapped modified keys, push the nomod action to our queue
        elif event.sym in keymap_nomod.keys():
            self._user_in_q.append(keymap_nomod[event.sym])

    def ev_mousemotion(self, event):
        x, y = event.tile
        self._user_in_q.append({"mousemotion": (x, y)})

    def ev_mousebuttondown(self, event):
        if self.state == GameStates.TARGETING:
            x, y = event.tile
            if event.button == tcod.event.BUTTON_RIGHT:
                self._user_in_q.append({"cancel_target": True})
            elif event.button == tcod.event.BUTTON_LEFT:
                self._user_in_q.append({"in_target": (x, y)})

    def get_user_input(self):
        if self._user_in_q:
            return self._user_in_q.pop(0)
        else:
            return {}

    def clear_user_input_q(self):
        self._user_in_q.clear()

    def set_game_state(self, state):
        self.state = state


null_keymap = {}

default_keymap_nomod = {
        tcod.event.K_ESCAPE: {"exit": True}
        }

default_keymap_lalt = {
        tcod.event.K_RETURN: {"fullscreen": True}
        }

default_keymap_shift = null_keymap

normal_keymap_nomod = {
        tcod.event.K_UP: {"move": (0, -1)},
        tcod.event.K_DOWN: {"move": (0, 1)},
        tcod.event.K_LEFT: {"move": (-1, 0)},
        tcod.event.K_RIGHT: {"move": (1, 0)},
        tcod.event.K_k: {"move": (0, -1)},
        tcod.event.K_j: {"move": (0, 1)},
        tcod.event.K_h: {"move": (-1, 0)},
        tcod.event.K_l: {"move": (1, 0)},
        tcod.event.K_y: {"move": (-1, -1)},
        tcod.event.K_u: {"move": (1, -1)},
        tcod.event.K_b: {"move": (-1, 1)},
        tcod.event.K_n: {"move": (1, 1)},
        tcod.event.K_KP_8: {"move": (0, -1)},
        tcod.event.K_KP_2: {"move": (0, 1)},
        tcod.event.K_KP_4: {"move": (-1, 0)},
        tcod.event.K_KP_6: {"move": (1, 0)},
        tcod.event.K_KP_7: {"move": (-1, -1)},
        tcod.event.K_KP_9: {"move": (1, -1)},
        tcod.event.K_KP_1: {"move": (-1, 1)},
        tcod.event.K_KP_3: {"move": (1, 1)},
        tcod.event.K_KP_5: {"wait": True},
        tcod.event.K_PERIOD: {"wait": True},
        tcod.event.K_p: {"possess": True},
        tcod.event.K_g: {"pickup": True},
        tcod.event.K_i: {"show_inventory": True},
        tcod.event.K_d: {"drop_inventory": True},
        tcod.event.K_GREATER: {"take_stairs": True},
        tcod.event.K_c: {"show_character_screen": True},
        tcod.event.K_q: {"msg_up": True},
        tcod.event.K_a: {"msg_down": True},
        tcod.event.K_ESCAPE: {"exit": True},
        tcod.event.K_BACKSPACE: {"test": True}
        }

normal_keymap_lalt = {
        tcod.event.K_RETURN: {"fullscreen": True},
        tcod.event.K_v: {"omnivis": True},
        tcod.event.K_c: {"switch_char": True},
        tcod.event.K_m: {"map_gen": True},
        tcod.event.K_g: {"graph_gen": True},
        tcod.event.K_COMMA: {"flood_neigh": True},
        tcod.event.K_n: {"show_vertices": True},
        tcod.event.K_h: {"show_hyperedges": True},
        tcod.event.K_b: {"show_edges": True}
        }

normal_keymap_shift = {
        tcod.event.K_PERIOD: {"take_stairs": True}
        }

target_keymap_nomod = {
        tcod.event.K_ESCAPE: {"cancel_target": True}
        }

fail_keymap_nomod = {
        tcod.event.K_q: {"msg_up": True},
        tcod.event.K_a: {"msg_down": True},
        tcod.event.K_i: {"show_inventory": True},
        tcod.event.K_ESCAPE: {"exit": True}
        }

fail_keymap_lalt = {
        tcod.event.K_v: {"omnivis": True},
        tcod.event.K_c: {"switch_char": True},
        tcod.event.K_RETURN: {"fullscreen": True}
        }

menu_keymap_nomod = {
        tcod.event.K_ESCAPE: {"exit": True},
        tcod.event.K_a: {"new_game": True},
        tcod.event.K_b: {"load_game": True},
        tcod.event.K_c: {"exit": True}
        }

level_up_keymap_nomod = {
        tcod.event.K_ESCAPE: {"exit": True},
        tcod.event.K_a: {"level_up": "hp"},
        tcod.event.K_b: {"level_up": "str"},
        tcod.event.K_c: {"level_up": "def"}
        }
