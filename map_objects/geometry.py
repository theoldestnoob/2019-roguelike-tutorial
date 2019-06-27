# -*- coding: utf-8 -*-
"""
Created on Tue Jun 25 22:11:50 2019

@author: theoldestnoob
"""


class Rect:
    def __init__(self, x, y, w, h):
        self.x1 = x
        self.y1 = y
        self.x2 = x + w
        self.y2 = y + h

    def center(self):
        center_x = int((self.x1 + self.x2) / 2)
        center_y = int((self.y1 + self.y2) / 2)
        return (center_x, center_y)

    def intersect(self, other):
        return (self.x1 <= other.x2 and self.x2 >= other.x1 and
                self.y1 <= other.y2 and self.y2 >= other.y1)


def line_lerp_orthogonal(x1, y1, x2, y2):
    '''
    Generate a series of (x, y) tuples along a line from (x1, y1) to (x2, y2)
    using orthogonal steps.
    Algorithm from redblobgames.com/grids/line-drawing.html.
    '''
    dx = x2 - x1
    dy = y2 - y1
    nx = abs(dx) + 1
    ny = abs(dy) + 1
    ix = 1
    iy = 1
    if dx > 0:
        sign_x = 1
    else:
        sign_x = -1
    if dy > 0:
        sign_y = 1
    else:
        sign_y = -1
    px, py = x1, y1
    while ix < nx or iy < ny:
        if (0.5 + ix) / nx < (0.5 + iy) / ny:
            # horizontal step
            px += sign_x
            ix += 1
        else:
            # vertical step
            py += sign_y
            iy += 1
        yield (px, py)
