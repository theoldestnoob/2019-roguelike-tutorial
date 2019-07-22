# -*- coding: utf-8 -*-
"""
Created on Tue Jun 25 22:11:50 2019

@author: theoldestnoob
"""


class Coord:
    '''Coordinate pair. Used as a hack for some pathfinding functions.'''
    def __init__(self, x, y):
        self.x = x
        self.y = y


class Space:
    '''Collection of coordinates with some helpful methods that allow testing
    for intersection, adjacency, etc. Inherited by all other geometric spaces.
    Used as GameMap rooms, MapGraph Vertices and Edges, etc.
    '''
    def __init__(self, coords):
        self.coords = coords

    def __iter__(self):
        return (c for c in self.coords)

    def __getitem__(self, index):
        return self.coords[index]

    def __len__(self):
        return len(self.coords)

    def __repr__(self):
        return f"Space({self.coords})"

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
        if not self.intersect(other):
            for coord in self.coords:
                for other_c in other:
                    (x1, y1) = coord
                    (x2, y2) = other_c
                    if coords_ortho_adjacent(x1, y1, x2, y2):
                        return True
        return False


class Rect(Space):
    '''Rectangular Space, some methods are faster than the generics.'''
    def __init__(self, x, y, w, h):
        self.x1 = x
        self.y1 = y
        self.x2 = x + w
        self.y2 = y + h
        self.w = w
        self.h = h
        self.coords = self.gen_coords()

    def __iter__(self):
        return (c for c in self.coords)

    def __repr__(self):
        return f"Rect({self.x1}, {self.y1}, {self.w}, {self.h})"

    def contains(self, x, y):
        return (self.x1 <= x and self.x2 >= x
                and self.y1 <= y and self.y2 >= y)

    def intersect(self, other):
        # if other is also a Rect, we can do this pretty fast
        if isinstance(other, Rect):
            return (self.x1 <= other.x2 and self.x2 >= other.x1 and
                    self.y1 <= other.y2 and self.y2 >= other.y1)
        # fall back to checking intersection of all coordinate pairs
        else:
            return super().intersect(other)

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
            adjacent = super().adjacent_ortho(other)

        return adjacent

    def gen_coords(self):
        coords = []
        for x in range(self.x1, self.x2 + 1):
            for y in range(self.y1, self.y2 + 1):
                coords.append((x, y))
        return coords

    def center(self):
        center_x = int((self.x1 + self.x2) / 2)
        center_y = int((self.y1 + self.y2) / 2)
        return (center_x, center_y)


# TODO: holy crap this is slow, find a better way
class Circle(Space):
    '''Circular Space. Generates a list of coordinates based on center x, y
    coordinates and radius values passed into class initialization method.'''
    def __init__(self, x, y, r):
        # print("Circle.__init__()")
        self.x = x
        self.y = y
        self.r = r
        z_coords = []
        r_sq = r ** 2
        # print(f"x: {x}, y: {y}, {r}")
        for c_x in range(-r, r + 1):
            c_x_sq = c_x ** 2
            # print(f"c_x: {c_x}, c_x_sq: {c_x_sq}")
            for c_y in range(-r, r + 1):
                c_y_sq = c_y ** 2
                # print(f"c_y: {c_y}, c_y_sq: {c_y_sq}")
                if c_x_sq + c_y_sq < r_sq:
                    z_coords.append((c_x, c_y))
        coords = []
        for (k_x, k_y) in z_coords:
            f_x = k_x + self.x
            f_y = k_y + self.y
            coords.append((f_x, f_y))
        # print(coords)
        self.coords = coords

    def __repr__(self):
        return f"Circle({self.x}, {self.y}, {self.r})"

    def center(self):
        return (self.x, self.y)


def line_lerp_orthogonal(x1, y1, x2, y2):
    '''
    Return a generator that generates a series of (x, y) tuples along a line
    from (x1, y1) to (x2, y2) using orthogonal steps.
    Algorithm from redblobgames.com/grids/line-drawing.html.

    >>> g = line_lerp_orthogonal(0, 0, 0, 3)
    >>> list(g)
    [(0, 1), (0, 2), (0, 3)]

    >>> g = line_lerp_orthogonal(-1, 0, 3, -2)
    >>> list(g)
    [(0, 0), (0, -1), (1, -1), (2, -1), (2, -2), (3, -2)]
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
    '''Return True if (x1, y1) is orthogonally adjacent to (x2, y2).

    >>> coords_ortho_adjacent(0, 0, 1, 0)
    True
    >>> coords_ortho_adjacent(0, 0, -1, 0)
    True
    >>> coords_ortho_adjacent(0, 0, 0, 1)
    True
    >>> coords_ortho_adjacent(0, 0, 0, -1)
    True
    >>> coords_ortho_adjacent(0, 0, 0, 0)
    False
    >>> coords_ortho_adjacent(0, 0, 1, 1)
    False
    '''
    if (x1 + 1, y1) == (x2, y2):
        return True
    if (x1 - 1, y1) == (x2, y2):
        return True
    if (x1, y1 + 1) == (x2, y2):
        return True
    if (x1, y1 - 1) == (x2, y2):
        return True
    return False


if __name__ == "__main__":
    import doctest
    doctest.testmod()
