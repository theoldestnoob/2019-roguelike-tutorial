# -*- coding: utf-8 -*-
"""
Created on Sat Jul 20 15:28:34 2019

@author: theoldestnoob
"""

import tcod

from game_messages import Message


class Inventory:
    def __init__(self, capacity):
        self.capacity = capacity
        self.items = []

    def add_item(self, item):
        results = []

        if len(self.items) >= self.capacity:
            msg_str = "You cannot carry any more, your inventory is full."
            results.append({
                    "item_added": None,
                    "message": Message(msg_str, tcod.yellow)
                     })
        else:
            msg_str = f"You pick up the {item.name}!"
            results.append({
                    "item_added": item,
                    "message": Message(msg_str, tcod.blue)
                    })
            self.items.append(item)

        return results
