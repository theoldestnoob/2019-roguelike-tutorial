# -*- coding: utf-8 -*-
"""
Created on Thu Jul  4 20:54:23 2019

@author: theoldestnoob
"""

from enum import Enum


class GameStates(Enum):
    NORMAL_TURN = 1
    FAIL_STATE = 3
    SHOW_INVENTORY = 4
