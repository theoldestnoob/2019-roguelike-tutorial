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


def main_menu(console, background_image, screen_width, screen_height):
    background_image.blit_2x(console, 0, 0)
    console.print(screen_width // 2, screen_height // 2 - 4,
                  "GAME TITLE TO GO HERE",
                  fg=tcod.light_yellow, alignment=tcod.CENTER)
    console.print(screen_width // 2, screen_height // 2 - 2,
                  "by theoldestnoob",
                  fg=tcod.light_yellow, alignment=tcod.CENTER)
    options = ["Play a new game", "Continue last game", "Quit"]

    menu(console, "", options, 24, screen_width, screen_height)


def level_up_menu(console, header, entity, menu_width,
                  screen_width, screen_height):
    options = [f"Constitution (+20 HP, from {entity.fighter.max_hp})",
               f"Strength (+1 attack, from {entity.fighter.power})",
               f"Agility (+1 defense, from {entity.fighter.defense})"]
    menu(console, header, options, menu_width, screen_width, screen_height)


def character_screen(console, entity, ch_width, ch_height,
                     screen_width, screen_height):
    window = tcod.console.Console(ch_width, ch_height)
    window.draw_frame(0, 0, ch_width, ch_height, fg=tcod.white, bg=tcod.black)
    if entity.level:
        ch_level = entity.level.current_level
        ch_xp = entity.level.current_xp
        ch_xp_to_next = entity.level.xp_to_next_level
    else:
        ch_level = "N/A"
        ch_xp = "N/A"
        ch_xp_to_next = "N/A"
    if entity.fighter:
        ch_maxhp = entity.fighter.max_hp
        ch_atk = entity.fighter.power
        ch_def = entity.fighter.defense
    else:
        ch_maxhp = "N/A"
        ch_atk = "N/A"
        ch_def = "N/A"
    window.print(1, 1, "Character Information")
    window.print(1, 2, f"Level: {ch_level}")
    window.print(1, 3, f"Experience: {ch_xp}")
    window.print(1, 4, f"XP to Level: {ch_xp_to_next}")
    window.print(1, 6, f"Maximum HP: {ch_maxhp}")
    window.print(1, 7, f"Attack: {ch_atk}")
    window.print(1, 8, f"Defense: {ch_def}")
    x = screen_width // 2 - ch_width // 2
    y = screen_height // 2 - ch_height // 2
    window.blit(console, dest_x=x, dest_y=y)


def message_box(con, message, width, screen_width, screen_height,
                msg_fg=tcod.white, msg_bg=tcod.black,
                frame_fg=tcod.white, frame_bg=tcod.black):
    height = con.get_height_rect(0, 0, width, screen_height, message)
    rect_x = screen_width // 2 - width // 2
    rect_y = screen_height // 2 - height // 2
    con.draw_frame(rect_x - 1, rect_y - 1, width + 2, height + 2,
                   fg=frame_fg, bg=frame_bg)
    con.print_box(rect_x, rect_y, width, height, message,
                  fg=msg_fg, bg=msg_bg)
