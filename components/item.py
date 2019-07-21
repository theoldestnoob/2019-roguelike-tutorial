# -*- coding: utf-8 -*-
"""
Created on Sat Jul 20 15:29:13 2019

@author: theoldestnoob
"""


class Item:
    def __init__(self, use_function=None, **kwargs):
        self.use_function = use_function
        self.function_kwargs = kwargs
