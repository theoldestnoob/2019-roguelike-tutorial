# -*- coding: utf-8 -*-
"""
Created on Tue Jun 18 21:35:02 2019

@author: theoldestnoob
"""

import tcod.event


class InputHandler(tcod.event.EventDispatch):

    def __init__(self):
        self._user_in_q = []

    def ev_quit(self, event):
        raise SystemExit()

    def ev_keydown(self, event):
        # first check for mapped modified keys
        if (event.mod & tcod.event.KMOD_LALT
                and event.sym in in_keymap_lalt.keys()):
            self._user_in_q.append(in_keymap_lalt[event.sym])
        # if no mapped modified keys, push the nomod mapped action to our queue
        elif event.sym in in_keymap_nomod.keys():
            self._user_in_q.append(in_keymap_nomod[event.sym])

    def ev_mousemotion(self, event):
        x, y = event.tile
        self._user_in_q.append({"mousemotion": (x, y)})

    def get_user_input(self):
        if self._user_in_q:
            return self._user_in_q.pop(0)
        else:
            return {}

    def clear_user_input_q(self):
        self._user_in_q.clear()


in_keymap_nomod = {
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
        tcod.event.K_q: {"msg_up": True},
        tcod.event.K_a: {"msg_down": True},
        tcod.event.K_ESCAPE: {"exit": True},
        tcod.event.K_BACKSPACE: {"test": True}
        }

in_keymap_lalt = {
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
