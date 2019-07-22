# -*- coding: utf-8 -*-
"""
Created on Sat Jul 20 15:29:13 2019

@author: theoldestnoob
"""


class Item:
    def __init__(self, use_function=None, targeting=False,
                 targeting_message=None, **kwargs):
        self.use_function = use_function
        self.targeting = targeting
        self.targeting_message = targeting_message
        self.target_x = None
        self.target_y = None
        self.function_kwargs = kwargs
