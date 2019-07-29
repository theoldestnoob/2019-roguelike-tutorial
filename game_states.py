# -*- coding: utf-8 -*-
"""
Created on Thu Jul  4 20:54:23 2019

@author: theoldestnoob
"""

from enum import Enum


class GameStates(Enum):
    MAIN_MENU = 1
    NORMAL_TURN = 2
    FAIL_STATE = 3
    SHOW_INVENTORY = 4
    DROP_INVENTORY = 5
    TARGETING = 6
    LEVEL_UP = 7
    CHARACTER_SCREEN = 8
