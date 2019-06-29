# -*- coding: utf-8 -*-
"""
Created on Tue Jun 25 22:11:50 2019

@author: theoldestnoob
"""


# TODO: add generic "space" class that's a collection of coordinates with
#       intersect, contains, adjacent functions, that other shapes inherit
#       to allow me to deal with arbitrary shaped vertices in map_graph
class Space:
    def __init__(self, coords):
        self.coords = coords

    def intersect(self, other):
        for coord in self.coords:
            if coord in other:
                return True
        return False

    def contains(self, x, y):
        if (x, y) in self.coords:
            return True
        return False

    # check for orthogonal adjacency
    def adjacent_ortho(self, other):
        # return true if any of Space's coordinates
        # is adjacent to any of other's coordinates
        pass

    def __iter__(self):
        return (c for c in self.coords)

    def __len__(self):
        return len(self.coords)

    def __repr__(self):
        return f"Space({self.coords})"


class Rect(Space):
    def __init__(self, x, y, w, h):
        self.x1 = x
        self.y1 = y
        self.x2 = x + w
        self.y2 = y + h
        self.w = w
        self.h = h

    def center(self):
        center_x = int((self.x1 + self.x2) / 2)
        center_y = int((self.y1 + self.y2) / 2)
        return (center_x, center_y)

    def intersect(self, other):
        return (self.x1 <= other.x2 and self.x2 >= other.x1 and
                self.y1 <= other.y2 and self.y2 >= other.y1)

    def contains(self, x, y):
        return (self.x1 <= x and self.x2 >= x
                and self.y1 <= y and self.y2 >= y)

# TODO: rewrite to check adjacency against arbitrary Spaces
    # check for orthogonal adjacency
    def adjacent_ortho(self, other):
        # if other is also a Rect, we can do this pretty fast
        if isinstance(other, Rect):
            # left adjacency
            if (self.x1 == other.x2 + 1
                    and self.y1 <= other.y2 and self.y2 >= other.y1):
                adjacent = True
            # right adjacency
            elif (self.x2 == other.x1 - 1
                    and self.y1 <= other.y2 and self.y2 >= other.y1):
                adjacent = True
            # top adjacency
            elif (self.y1 == other.y2 + 1
                    and self.x1 <= other.x2 and self.x2 >= other.x1):
                adjacent = True
            # bottom adjacency
            elif (self.y2 == other.y1 - 1
                    and self.x1 <= other.x2 and self.x2 >= other.x1):
                adjacent = True
            else:
                adjacent = False
        # fall back to checking adjacency of all coordinate pairs
        else:
            for (other_x, other_y) in other:
                for x in range(self.x1, self.x2 + 1):
                    for y in range(self.y1, self.y2 + 1):
                        if coords_ortho_adjacent(x, y, other_x, other_y):
                            return True
            return False

        return adjacent

    def __iter__(self):
        # iterate by returning a list of coorinates contained in Rect
        for x in range(self.x1, self.x2 + 1):
            for y in range(self.y1, self.y2 + 1):
                yield (x, y)

    def __len__(self):
        # "length" of Rect is the number of coordinates in it
        return self.h * self.w

    def __repr__(self):
        return f"Rect({self.x1}, {self.y1}, {self.w}, {self.h})"


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


def coords_ortho_adjacent(x1, y1, x2, y2):
    if (x1 + 1, y1) == (x2, y2):
        return True
    if (x1 - 1, y1) == (x2, y2):
        return True
    if (x1, y1 + 1) == (x2, y2):
        return True
    if (x1, y1 - 1) == (x2, y2):
        return True
    return False
