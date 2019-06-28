# -*- coding: utf-8 -*-
"""
Created on Thu Jun 27 21:00:50 2019

@author: theoldestnoob
"""

from itertools import product
from collections import deque
from time import sleep
import tcod

from render_functions import draw_map


class MapGraph():
    def __init__(self, tiles, rooms=[], edges=[], con=None, debug=False):
        self.tiles = tiles
        self.edges = edges
        self.con = con
        self.debug = debug
        self.vertices = self.create_vertices(rooms)

    def __repr__(self):
        return f"MapGraph({self.tiles}, {self.vertices}, {self.edges})"

    def __str__(self):
        outstr = "MapGraph\nVertices:\n"
        for vertex in self.vertices:
            outstr += f"{vertex}\n"
        outstr += "Edges:\n"
        for edge in self.edges:
            outstr += f"{edge}\n"
        return outstr

    def create_vertices(self, rooms):
        if self.debug:
            print("Creating Vertices...")
        alphabet = "ABCDEFGHIJKLMNOPQRSTUVWXYZ"
        rnum = len(rooms) // len(alphabet) + 1
        vertices = []
        for room, idtuple in zip(rooms, product(alphabet, repeat=rnum)):
            ident = "".join(idtuple)
            vertex = MapVertex(room, ident)
            vertices.append(vertex)
        return vertices

    def find_edges(self):
        pass

    def find_vertex_neighbors(self):
        # flood fill from each room to find its neighbors
        if self.debug:
            print("Finding Vertex Neighbors...")
        for vertex in self.vertices:
            room_x, room_y = vertex.space.center()
            others = [k for k in self.vertices if k is not vertex]
            width = len(self.tiles)
            height = len(self.tiles[0])
            if self.debug:
                draw_map(self.con, self.tiles, width, height,
                         {"dark_wall": tcod.Color(0, 0, 100),
                          "dark_ground": tcod.Color(50, 50, 150)})
                tcod.console_flush()
            neighbors = self.find_vertex_neigh_iter(vertex, others,
                                                    width, height)
            vertex.neighbors = list(set(neighbors))

    def find_vertex_neigh_iter(self, vertex, others, width, height):
        # vertex: vertex to find neighbors of
        # others: other vertices that may be neighbors
        # we assume no overlapping vertices on graph
        x0, y0 = vertex.space.center()
        searched = [[False for y in range(height)]
                    for x in range(width)]
        neighbors = []
        searchq = deque([(x0, y0)])

        while searchq:
            x, y = searchq.popleft()
            searched[x][y] = True
            if self.debug:
                tcod.console_set_char_background(self.con, x, y,
                                                 tcod.red,
                                                 tcod.BKGND_SET)
                tcod.console_blit(self.con, 0, 0, width, height,
                                  0, 0, 0)
                sleep(0.001)
                tcod.console_flush()

            for z in others:
                if z.space.contains(x, y):
                    neighbors.append(z)
                    break
            else:
                if (not searched[x + 1][y]
                        and not self.tiles[x + 1][y].blocked
                        and not (x + 1, y) in searchq):
                    searchq.append((x + 1, y))
                if (not searched[x - 1][y]
                        and not self.tiles[x - 1][y].blocked
                        and not (x - 1, y) in searchq):
                    searchq.append((x - 1, y))
                if (not searched[x][y + 1]
                        and not self.tiles[x][y + 1].blocked
                        and not (x, y + 1) in searchq):
                    searchq.append((x, y + 1))
                if (not searched[x][y - 1]
                        and not self.tiles[x][y - 1].blocked
                        and not (x, y - 1) in searchq):
                    searchq.append((x, y - 1))

        return neighbors


class MapVertex():
    def __init__(self, space=None, ident=None, edges=[], neighbors=[]):
        self.space = space
        self.ident = ident
        self.edges = edges
        self.neighbors = neighbors

    def __repr__(self):
        return f"MapVertex({self.space}, {self.ident}, {self.edges}, {self.neighbors})"

    def __str__(self):
        outstr = f"Vertex '{self.ident}': {self.space}\nNeighbors:"
        nids = []
        for neighbor in self.neighbors:
            nids.append(neighbor.ident)
        outstr += ", ".join(nids)
        return outstr


class MapEdge():
    def __init__(self, space=None, ident=None, vertices=[]):
        self.space = space
        self.ident = ident
        self.vertices = vertices

    def __repr__(self):
        return f"MapEdge({self.space}, {self.ident}, {self.vertices})"
