# -*- coding: utf-8 -*-
"""
Created on Thu Jul  4 20:54:23 2019

@author: theoldestnoob
"""

from enum import Enum


class GameStates(Enum):
    PLAYERS_TURN = 1
    ENEMY_TURN = 2
    FAIL_STATE = 3
