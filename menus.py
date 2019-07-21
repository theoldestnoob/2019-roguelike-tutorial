# -*- coding: utf-8 -*-
"""
Created on Sat Jul 20 19:15:14 2019

@author: theoldestnoob
"""

import tcod


def menu(con, header, options, width, screen_width, screen_height):
    if len(options) > 26:
        raise ValueError("Cannot have a menu with more than 26 options.")

    # total height for the header (after auto-wrap) and one line per option
    header_height = tcod.console.get_height_rect(width - 2, header)
    height = len(options) + header_height + 2

    # console for menu's window
    window = tcod.console.Console(width, height)

    # print header and frame
    # window.draw_rect(0, 0, width, height, 0, fg=tcod.white, bg=tcod.black)
    window.draw_frame(0, header_height, width, height - header_height,
                      fg=tcod.white, bg=tcod.black)
    window.print_box(1, 0, width - 2, header_height, header,
                     fg=tcod.white, bg=tcod.black)

    # print options in frame
    y = header_height + 1
    letter_index = ord("a")
    for option_text in options:
        window.print(1, y, f"({chr(letter_index)}) {option_text}",
                     fg=tcod.white, bg=tcod.black)
        y += 1
        letter_index += 1

    # blit window to root console
    x = screen_width // 2 - width // 2
    y = screen_height // 2 - height // 2
    window.blit(con, dest_x=x, dest_y=y, width=width, height=height)


def inventory_menu(con, header, inventory, inventory_width,
                   screen_width, screen_height):
    # show a menu with each item of the inventory as an option
    if len(inventory.items) == 0:
        options = ["Inventory is empty."]
    else:
        options = [item.name for item in inventory.items]

    menu(con, header, options, inventory_width, screen_width, screen_height)
