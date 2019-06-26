# -*- coding: utf-8 -*-
"""
Created on Tue Jun 18 20:28:25 2019

@author: theoldestnoob
"""

import tcod
import tcod.event

from entity import Entity
from input_handlers import InputHandler
from render_functions import clear_all, render_all
from map_objects.game_map import GameMap


def main():
    screen_width = 80
    screen_height = 50
    map_width = 80
    map_height = 45

    room_max_size = 10
    room_min_size = 6
    max_rooms = 30

    colors = {
            "dark_wall": tcod.Color(0, 0, 100),
            "dark_ground": tcod.Color(50, 50, 150)
    }

    player = Entity(int(screen_width / 2), int(screen_height / 2), "@",
                    tcod.white)
    npc = Entity(int(screen_width / 2 - 5), int(screen_height / 2), "@",
                 tcod.yellow)
    entities = [player, npc]

    tcod.console_set_custom_font(
            "arial10x10.png",
            tcod.FONT_TYPE_GREYSCALE | tcod.FONT_LAYOUT_TCOD
            )

    game_map = GameMap(map_width, map_height)
    game_map.make_map(max_rooms, room_min_size, room_max_size, map_width,
                      map_height, player)

    action = {}

    in_handle = InputHandler()

    with tcod.console_init_root(
            screen_width, screen_height,
            "libtcod tutorial revised",
            fullscreen=False,
            renderer=tcod.RENDERER_SDL2,
            vsync=False) as con:

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

            if move:
                dx, dy = move
                if not game_map.is_blocked(player.x + dx, player.y + dy):
                    player.move(dx, dy)

            if want_exit:
                return True
                raise SystemExit()

            if fullscreen:
                tcod.console_set_fullscreen(not tcod.console_is_fullscreen())


if __name__ == "__main__":
    main()
