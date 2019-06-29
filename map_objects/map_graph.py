# -*- coding: utf-8 -*-
"""
Created on Thu Jun 27 21:00:50 2019

@author: theoldestnoob
"""

from itertools import product
from itertools import repeat
from collections import deque
from time import sleep
import tcod

from render_functions import draw_map


class MapGraph():
    def __init__(self, tiles, rooms=[], con=None, debug=False):
        self.tiles = tiles
        self.hyperedges = []
        self.con = con
        self.debug = debug
        self.vertices = self.create_vertices(rooms)

    def __repr__(self):
        return f"MapGraph({self.tiles}, {self.vertices}"

    def __str__(self):
        outstr = "=====MapGraph=====\n===Vertices===:\n"
        for vertex in self.vertices:
            outstr += f"{vertex}\n"
        outstr += "===Hyperedges===:\n"
        for h_edge in self.hyperedges:
            outstr += f"{h_edge}\n"
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

    def vertex_neighbors_from_hyperedges(self):
        if self.debug:
            print("Finding Vertex Neighbors from Hyperedges...")
        for vertex in self.vertices:
            nlist = []
            for edge in self.hyperedges:
                if vertex in edge.vertices:
                    nlist.extend(edge.vertices)
            nlist = list(set(nlist))
            nlist.remove(vertex)
            vertex.neighbors = nlist

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
                # tcod.console_blit(self.con, 0, 0, width, height,
                #                   0, 0, 0)
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

    def find_vertex_hyperedges(self):
        if self.debug:
            print("Finding Vertex Edges...")
        for vertex in self.vertices:
            elist = []
            for edge in self.hyperedges:
                if vertex in edge.vertices:
                    elist.append(edge)
            vertex.hyperedges = elist

    def show_vertices(self):
        for vertex in self.vertices:
            for x in range(vertex.space.x1, vertex.space.x2 + 1):
                for y in range(vertex.space.y1, vertex.space.y2 + 1):
                    tcod.console_set_char_background(self.con, x, y,
                                                     tcod.red,
                                                     tcod.BKGND_SET)
        tcod.console_flush()
        sleep(1)

    def find_hyperedges(self):
        if self.debug:
            print("Finding Hyperedges...")
        # find tiles that aren't walls and aren't in a vertex
        width = len(self.tiles)
        height = len(self.tiles[0])
        edgetiles = [[True for y in range(height)]
                     for x in range(width)]
        for y in range(height):
            for x in range(width):
                if self.tiles[x][y].blocked:
                    edgetiles[x][y] = False
                for vertex in self.vertices:
                    if vertex.space.contains(x, y):
                        edgetiles[x][y] = False
                        break
        if self.debug:
            draw_map(self.con, self.tiles, width, height,
                     {"dark_wall": tcod.Color(0, 0, 100),
                      "dark_ground": tcod.Color(50, 50, 150)})
            tcod.console_flush()
            for y in range(height):
                for x in range(width):
                    if edgetiles[x][y]:
                        tcod.console_set_char_background(self.con, x, y,
                                                         tcod.red,
                                                         tcod.BKGND_SET)
            tcod.console_flush()
            sleep(0.5)
        # flood fill all edge tiles to find vertices they connect
        captured = [[False for y in range(height)]
                    for x in range(width)]
        elist = []
        for y in range(height):
            for x in range(width):
                if edgetiles[x][y]:
                    edge = self.find_hyperedge_iter(x, y, captured, 
                                                    width, height)
                    if edge:
                        for ex, ey in edge.space:
                            captured[ex][ey] = True
                        elist.append(edge)
        # assign identifiers to all edges
        alphabet = "abcdefghijklmnopqrstuvwxyz"
        rnum = len(elist) // len(alphabet) + 1
        for edge, idtuple in zip(elist, product(alphabet, repeat=rnum)):
            edge.ident = "".join(idtuple)

        self.hyperedges = elist

    def find_hyperedge_iter(self, x0, y0, captured, width, height):
        if captured[x0][y0]:
            return []
        searched = [[False for y in range(height)]
                    for x in range(width)]
        neighbors = []
        tiles = []
        searchq = deque([(x0, y0)])

        while searchq:
            x, y = searchq.popleft()
            searched[x][y] = True
            if self.debug:
                tcod.console_set_char_background(self.con, x, y,
                                                 tcod.green,
                                                 tcod.BKGND_SET)
                sleep(0.010)
                tcod.console_flush()

            for z in self.vertices:
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
                tiles.append((x, y))

        nlist = list(set(neighbors))
        edge = MapHyperedge(tiles, nlist)
        return edge

    def show_hyperedges(self):
        for edge in self.hyperedges:
            for x, y in edge.space:
                tcod.console_set_char_background(self.con, x, y,
                                                 tcod.green,
                                                 tcod.BKGND_SET)
        tcod.console_flush()
        sleep(1)


class MapVertex():
    def __init__(self, space=None, ident=None, hyperedges=[], neighbors=[]):
        self.space = space
        self.ident = ident
        self.hyperedges = hyperedges
        self.neighbors = neighbors

    def __repr__(self):
        return f"MapVertex({self.space}, {self.ident}, {self.edges}, {self.neighbors})"

    def __str__(self):
        outstr = f"Vertex '{self.ident}': {self.space}\nNeighbors: "
        nids = []
        for neighbor in self.neighbors:
            nids.append(neighbor.ident)
        outstr += ", ".join(nids)
        outstr += "\nHyperedges: "
        eids = []
        for edge in self.hyperedges:
            eids.append(edge.ident)
        outstr += ", ".join(eids)
        return outstr


class MapHyperedge():
    def __init__(self, space, vertices, ident=None):
        self.space = space
        self.vertices = vertices
        if ident is None:
            vlist = []
            for vertex in vertices:
                vlist.append(vertex.ident)
            self.ident = ".".join(sorted(list(set(vlist))))
        else:
            ident = ident

    def __repr__(self):
        return f"MapHyperedge({self.space}, {self.ident}, {self.vertices})"

    def __str__(self):
        outstr = f"Hyperedge '{self.ident}'\n"
        outstr += f"Space: {self.space}\n"
        outstr += f"Vertices: "
        vids = []
        for vertex in self.vertices:
            vids.append(vertex.ident)
        outstr += ", ".join(vids)
        return outstr
