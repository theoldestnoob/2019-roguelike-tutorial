# -*- coding: utf-8 -*-
"""
Created on Tue Jun 25 20:47:16 2019

@author: theoldestnoob
"""

from map_objects.geometry import Rect
from map_objects.geometry import line_lerp_orthogonal
from map_objects.tile import Tile
from map_objects.map_graph import MapGraph


class GameMap:
    def __init__(self, width, height, seed, con=None, debug=False):
        self.width = width
        self.height = height
        self.tiles = self.initialize_tiles()
        self.seed = seed
        self.con = con
        self.debug = debug
        self.rooms = []
        self.nodes = []
        self.graph = None

    def initialize_tiles(self):
        tiles = [[Tile(True) for y in range(self.height)]
                 for x in range(self.width)]

        return tiles

    def is_blocked(self, x, y):
        if self.tiles[x][y].blocked:
            return True

        return False

    def make_map(self, player, *args, **kwargs):
        # create a big empty map with a wall around the edges
        room = Rect(1, 1, self.width - 3, self.height - 3)
        print(room)
        self.create_room(room)
        self.rooms.append(room)
        player.x, player.y = room.center()

    def make_graph(self):
        self.graph = MapGraph(self.tiles, self.rooms,
                              con=self.con, debug=self.debug)
        # self.graph.find_vertex_neighbors()
        self.graph.find_hyperedges()
        print(self.graph.hyperedges)
        self.graph.vertex_neighbors_from_hyperedges()
        self.graph.find_vertex_hyperedges()
        if self.debug:
            print(self.graph)

    def create_room(self, room):
        # go through the tiles in the rectangle and make them passable
        #   leaving a 1-tile wide border around the edge
        for x in range(room.x1, room.x2 + 1):
            for y in range(room.y1, room.y2 + 1):
                self.tiles[x][y].blocked = False
                self.tiles[x][y].block_sight = False

    def create_h_tunnel(self, x1, x2, y):
        for x in range(min(x1, x2), max(x1, x2) + 1):
            self.tiles[x][y].blocked = False
            self.tiles[x][y].block_sight = False

    def create_v_tunnel(self, y1, y2, x):
        for y in range(min(y1, y2), max(y1, y2) + 1):
            self.tiles[x][y].blocked = False
            self.tiles[x][y].block_sight = False

    def create_d_tunnel(self, x1, y1, x2, y2):
        points = line_lerp_orthogonal(x1, y1, x2, y2)
        for x, y in points:
            self.tiles[x][y].blocked = False
            self.tiles[x][y].block_sight = False
