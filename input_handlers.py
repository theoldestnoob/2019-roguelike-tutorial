# -*- coding: utf-8 -*-
"""
Created on Tue Jun 18 21:35:02 2019

@author: willh
"""

import tcod.event


class InputHandler(tcod.event.EventDispatch):

    def __init__(self):
        self._actionq = []

    def ev_quit(self, event):
        self._actionq.append({"exit": True})

    def ev_keydown(self, event):
        # first check for combination keys
        if (event.sym == tcod.event.K_RETURN
                and event.mod & tcod.event.KMOD_LALT):
            self._actionq.append({"fullscreen": True})
        # if not combination, push the keymapped action to our action queue
        elif event.sym in input_keymap.keys():
            self._actionq.append(input_keymap[event.sym])

    def get_action(self):
        if self._actionq:
            return self._actionq.pop(0)
        else:
            return {}

    def clear_actionq(self):
        self._actionq.clear()


input_keymap = {
        tcod.event.K_UP: {"move": (0, -1)},
        tcod.event.K_DOWN: {"move": (0, 1)},
        tcod.event.K_LEFT: {"move": (-1, 0)},
        tcod.event.K_RIGHT: {"move": (1, 0)},
        tcod.event.K_ESCAPE: {"exit": True}
        }
