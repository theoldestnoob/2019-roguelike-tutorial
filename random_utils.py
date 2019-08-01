# -*- coding: utf-8 -*-
"""
Created on Wed Jul 31 20:32:35 2019

@author: theoldestnoob
"""

from random import randint


def random_choice_index(chances):
    random_chance = randint(1, sum(chances))

    running_sum = 0
    choice = 0
    for w in chances:
        running_sum += w
        if random_chance <= running_sum:
            return choice
        choice += 1


def random_choice_from_dict(choice_dict):
    choices = list(choice_dict.keys())
    chances = list(choice_dict.values())
    return choices[random_choice_index(chances)]
