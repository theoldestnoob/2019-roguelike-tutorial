# -*- coding: utf-8 -*-
"""
Created on Tue Jun 18 20:28:25 2019

@author: theoldestnoob
"""

import tcod
import tcod.event
from input_handlers import InputHandler


def main():
    screen_width = 80
    screen_height = 50

    player_x = int(screen_width / 2)
    player_y = int(screen_height / 2)

    tcod.console_set_custom_font(
            "arial10x10.png",
            tcod.FONT_TYPE_GREYSCALE | tcod.FONT_LAYOUT_TCOD
            )

    action = {}

    in_handle = InputHandler()

    with tcod.console_init_root(
            screen_width, screen_height,
            "libtcod tutorial revised",
            fullscreen=False,
            renderer=tcod.RENDERER_SDL2,
            vsync=False) as con:

        while True:

            tcod.console_put_char(con, player_x, player_y,
                                  "@", tcod.BKGND_NONE)
            con.blit(con)
            tcod.console_flush()

            tcod.console_put_char(con, player_x, player_y,
                                  " ", tcod.BKGND_NONE)

            for event in tcod.event.get():
                in_handle.dispatch(event)

            action = in_handle.get_action()

            # debug output
            if(action):
                print(action)

            move = action.get("move")
            want_exit = action.get("exit")
            fullscreen = action.get("fullscreen")

            if move:
                dx, dy = move
                player_x += dx
                player_y += dy

            if want_exit:
                return True
                raise SystemExit()

            if fullscreen:
                tcod.console_set_fullscreen(not tcod.console_is_fullscreen())


if __name__ == "__main__":
    main()
