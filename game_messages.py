# -*- coding: utf-8 -*-
"""
Created on Sat Jul 13 21:02:53 2019

@author: theoldestnoob
"""

import tcod
import textwrap


class Message:
    def __init__(self, text, color=tcod.white):
        self.text = text
        self.color = color

    def __repr__(self):
        return f"Message('{self.text}', color={self.color})"


# TODO: rewrite using bounded deque object instead of list
class MessageLog:
    def __init__(self, x, width, height):
        self.messages = []
        self.x = x
        self.width = width
        self.height = height

    def add_message(self, message):
        new_msg_lines = textwrap.wrap(message.text, self.width)
        for line in new_msg_lines:
            if len(self.messages) == self.height:
                del self.messages[0]
            self.messages.append(Message(line, message.color))

    def __repr__(self):
        return f"MessageLog({self.x}, {self.width}, {self.height})"
