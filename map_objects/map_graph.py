# -*- coding: utf-8 -*-
"""
Created on Thu Jun 27 21:00:50 2019

@author: theoldestnoob
"""

from itertools import product
from itertools import combinations
from collections import deque
from time import sleep
import tcod

from render_functions import draw_map
from map_objects.geometry import coords_ortho_adjacent
from map_objects.geometry import Rect


class MapGraph():
    def __init__(self, tiles, rooms=[], con=None, debug=False):
        self.tiles = tiles
        self.hyperedges = []
        self.edges = []
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
        outstr += "===Edges===:\n"
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
            vlist = []
            nlist = []
            for edge in self.hyperedges:
                for v, c in edge.vertices:
                    if vertex == v:
                        vlist.extend(edge.vertices)
            for v, c in vlist:
                if v is not vertex:
                    nlist.append(v)
            vertex.neighbors = list(set(nlist))

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
            print("Finding Vertex Hyperdges...")
        for vertex in self.vertices:
            elist = []
            for edge in self.hyperedges:
                for v, c in edge.vertices:
                    if v == vertex:
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
            edge.ident = "#"
            edge.ident += "".join(idtuple)

        self.hyperedges = elist

    def find_hyperedge_iter(self, x0, y0, captured, width, height):
        if captured[x0][y0]:
            return []
        searched = [[False for y in range(height)]
                    for x in range(width)]
        neighbors = []
        n_coords = []
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
                    n_coords.append((x, y))
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
        # hyperedges store their vertices as (vertex, coord) tuples
        #  where coord is the coordinates of one tile in the vertex adjacent
        #  to the hyperedge
        ndict = {}
        for n, c in zip(neighbors, n_coords):
            ndict[n] = c
        nlist = ndict.items()
        edge = MapEdge(tiles, nlist)
        return edge

    def show_hyperedges(self):
        for edge in self.hyperedges:
            for x, y in edge.space:
                tcod.console_set_char_background(self.con, x, y,
                                                 tcod.green,
                                                 tcod.BKGND_SET)
        tcod.console_flush()
        sleep(1)

# TODO:  rewrite to use arbitrary shaped vertices instead of just Rects
    def find_edges_from_hyperedges(self):
        if self.debug:
            print("Finding Edges from Hyperedges...\n")
        elist = []
        for hyperedge in self.hyperedges:
            print(f"\nhyper: {hyperedge.ident}")
            vids = []
            for vertex in hyperedge.vertices:
                vids.append(vertex[0].ident)
            print(f"vertices: {vids}")
            for pair in combinations(hyperedge.vertices, 2):
                v0, v1 = pair
                print(f"pair: {v0[0].ident}, {v1[0].ident}")
                # MapEdge(space, vertices, ident)
                # find shortest path between v1[1] and v2[1] in vertex.space
                # new Edge is MapEdge(space, [v0, v1], ident)
                x1, y1 = v0[1]
                x2, y2 = v1[1]
                s = self.find_spath_in_coords(hyperedge.space, v0[0], v1[0])
                elist.append(MapEdge(s, [v0, v1]))
        self.edges = elist

# TODO:  rewrite to use arbitrary shaped vertices instead of just Rects
    def find_spath_in_coords(self, coord_list, v0, v1):
        print(f"start: {v0.ident}, end: {v1.ident}")
        print(f"coord_list:   {coord_list}")
        # build a list of coordinates with distance from v0
        # list of tuples (x, y, distance)
        distance = []
        searched = []
        stack = deque()
        for x, y in coord_list:
            if v0.space.adjacent(Rect(x, y, 0, 0)):
                distance.append((x, y, 1))
                stack.append((x, y, 1))
        count = 0
        print(f"v0: {v0.space}")
        print(f"start stack: {stack}")
        while stack:
            x, y, z = stack.popleft()
            #print(f"current: {x}, {y}, {z}")
            if (x + 1, y) in coord_list and (x + 1, y) not in searched:
                distance.append((x + 1, y, z + 1))
                stack.append((x + 1, y, z + 1))
                searched.append((x + 1, y))
            if (x - 1, y) in coord_list and (x - 1, y) not in searched:
                distance.append((x - 1, y, z + 1))
                stack.append((x - 1, y, z + 1))
                searched.append((x - 1, y))
            if (x, y + 1) in coord_list and (x, y + 1) not in searched:
                distance.append((x, y + 1, z + 1))
                stack.append((x, y + 1, z + 1))
                searched.append((x, y + 1))
            if (x, y - 1) in coord_list and (x, y - 1) not in searched:
                distance.append((x, y - 1, z + 1))
                stack.append((x, y - 1, z + 1))
                searched.append((x, y - 1))
            print(f"stack: {stack}")
            # exit if we've searched 5000 spaces
            # because we're probably in an infinite loop
            count += 1
            if count > 5000:
                break
        #print(f"distance: {distance}")
        print(f"searched: {searched}")
        # find the shortest path from v1 back to v0
        # start at v1 and always pick the tile with the lowest distance
        distance.sort(key=lambda z: z[2], reverse=True)
        print(f"sorted distance: {distance}")
        x_end, y_end, z_end = distance[0]
        for x, y, z in distance:
            if v1.space.adjacent(Rect(x, y, 0, 0)):
                if z < z_end:
                    x_end = x
                    y_end = y
                    z_end = z
        spath = [(x_end, y_end)]
        for (x, y, z) in distance:
            if z < z_end and coords_ortho_adjacent(x, y, x_end, y_end):
                spath.append((x, y))
                x_end, y_end, z_end = x, y, z
        print(f"shortest path: {spath}")
        return spath

    def show_edge(self, edge):
        print(f"***Edge: {edge}")
        for x, y in edge.space:
            tcod.console_set_char_background(self.con, x, y,
                                             tcod.green,
                                             tcod.BKGND_SET)
            tcod.console_flush()

    def show_edges(self):
        width = len(self.tiles)
        height = len(self.tiles[0])
        for edge in self.edges:
            for x, y in edge.space:
                tcod.console_set_char_background(self.con, x, y,
                                                 tcod.green,
                                                 tcod.BKGND_SET)
                tcod.console_flush()
            sleep(0.3)
            draw_map(self.con, self.tiles, width, height,
                     {"dark_wall": tcod.Color(0, 0, 100),
                      "dark_ground": tcod.Color(50, 50, 150)})
            tcod.console_flush()


class MapVertex():
    def __init__(self, space=None, ident=None, hyperedges=[], neighbors=[]):
        self.space = space
        self.ident = ident
        self.hyperedges = hyperedges
        self.neighbors = neighbors

    def __repr__(self):
        return f"MapVertex({self.space}, {self.ident}, {self.hyperedges}, {self.neighbors})"

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


class MapEdge():
    def __init__(self, space, vertices, ident=None):
        self.space = space
        self.vertices = vertices
        if ident is None:
            vlist = []
            for vertex, coord in vertices:
                vlist.append(vertex.ident)
            self.ident = ""
            self.ident += "".join(sorted(list(set(vlist))))
        else:
            ident = ident

    def __repr__(self):
        return f"MapEdge({self.space}, {self.ident}, {self.vertices})"

    def __str__(self):
        outstr = f"Edge '{self.ident}'\n"
        outstr += f"Space: {self.space}\n"
        outstr += f"Vertices: "
        vids = []
        for vertex, coord in self.vertices:
            vids.append(f"{vertex.ident} {coord}")
        outstr += ", ".join(vids)
        return outstr
