# -*- coding: utf-8 -*-
"""
Created on Tue Jun 18 21:35:02 2019

@author: willh
"""

import tcod.event


def handle_input(event):
    if event.type == "KEYDOWN":
        return handle_keys(event)
    elif event.type == "QUIT":
        return handle_quit(event)

    return {}


def handle_keys(event):
    # debug output
    # print(event)

    # movement keys
    if event.sym == tcod.event.K_UP:
        return {"move": (0, -1)}
    elif event.sym == tcod.event.K_DOWN:
        return {"move": (0, 1)}
    elif event.sym == tcod.event.K_LEFT:
        return {"move": (-1, 0)}
    elif event.sym == tcod.event.K_RIGHT:
        return {"move": (1, 0)}

    # fullscreen
    if event.sym == tcod.event.K_RETURN and event.mod & tcod.event.KMOD_LALT:
        return {"fullscreen": True}

    # exit the game
    if event.sym == tcod.event.K_ESCAPE:
        return {"exit": True}

    return {}


def handle_quit(event):
    return {"exit": True}


class InputHandler(tcod.event.EventDispatch):

    def __init__(self):
        self._actionq = []

    def ev_quit(self, event):
        self._actionq.append({"exit": True})

    def ev_keydown(self, event):
        # movement keys
        if event.sym == tcod.event.K_UP:
            self._actionq.append({"move": (0, -1)})
        elif event.sym == tcod.event.K_DOWN:
            self._actionq.append({"move": (0, 1)})
        elif event.sym == tcod.event.K_LEFT:
            self._actionq.append({"move": (-1, 0)})
        elif event.sym == tcod.event.K_RIGHT:
            self._actionq.append({"move": (1, 0)})

        # fullscreen
        if (event.sym == tcod.event.K_RETURN
                and event.mod & tcod.event.KMOD_LALT):
            self._actionq.append({"fullscreen": True})

        # exit the game
        if event.sym == tcod.event.K_ESCAPE:
            self._actionq.append({"exit": True})

    def get_action(self):
        if self._actionq:
            return self._actionq.pop(0)
        else:
            return {}

    def clear_actionq(self):
        self._actionq.clear()
