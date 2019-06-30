# -*- coding: utf-8 -*-
"""
Created on Tue Jun 25 20:47:16 2019

@author: theoldestnoob
"""

from random import uniform
from random import choice

from map_objects.geometry import Rect
from map_objects.geometry import line_lerp_orthogonal
from map_objects.tile import Tile
from map_objects.map_graph import MapGraph


class GameMap:
    '''Basic GameMap object, provides attributes and a handful of functions
    used by all GameMap subclasses. By itself just creates one room that fills
    the map with a 1-width wall around the edge.
    '''
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
        '''Set all tiles' blocked and block_view attributes to True.'''
        tiles = [[Tile(True) for y in range(self.height)]
                 for x in range(self.width)]

        return tiles

    def is_blocked(self, x, y):
        '''Is the tile at (x, y) blocked?'''
        if self.tiles[x][y].blocked:
            return True

        return False

    def make_map(self, player, *args, **kwargs):
        '''Make a big empty map with a wall around the edge. Expected to be
        overloaded by any child classes.
        '''
        # create a big empty map with a wall around the edges
        room = Rect(1, 1, self.width - 3, self.height - 3)
        print(room)
        self.create_room(room)
        self.rooms.append(room)
        player.x, player.y = room.center()

    def make_graph(self):
        '''Generate graph data about the map and store it in self.graph.'''
        tiles = self.game_map_to_bool_array()
        self.graph = MapGraph(tiles, self.rooms, debug=self.debug)
        if self.debug:
            print(self.graph)

    def create_room(self, room):
        '''Carve out a room using a list of (x, y) coordinate pairs.'''
        for (x, y) in room.coords:
            self.tiles[x][y].blocked = False
            self.tiles[x][y].block_sight = False

    def create_room_rect(self, room):
        '''Carve out a room based on a Rect, leaving a 1-tile wide border
        around the edges.
        '''
        for x in range(room.x1, room.x2 + 1):
            for y in range(room.y1, room.y2 + 1):
                self.tiles[x][y].blocked = False
                self.tiles[x][y].block_sight = False

    def create_h_tunnel(self, x1, x2, y):
        '''Carve out a horizontal tunnel between (x1, y) and (x2, y).'''
        for x in range(min(x1, x2), max(x1, x2) + 1):
            self.tiles[x][y].blocked = False
            self.tiles[x][y].block_sight = False

    def create_v_tunnel(self, y1, y2, x):
        '''Carve out a vertical tunnel between (x, y1) and (x, y2)'''
        for y in range(min(y1, y2), max(y1, y2) + 1):
            self.tiles[x][y].blocked = False
            self.tiles[x][y].block_sight = False

    def create_d_tunnel(self, x1, y1, x2, y2):
        '''Carve out a tunnel between (x1, y1) and (x2, y2).'''
        points = line_lerp_orthogonal(x1, y1, x2, y2)
        for x, y in points:
            self.tiles[x][y].blocked = False
            self.tiles[x][y].block_sight = False

    def make_halls(self, space, player, ratio_vh, ratio_hv, ratio_d):
        '''Add halls to the map betwen rooms in order of room creation.'''
        old_room = None
        for room in self.rooms:
            if old_room is None:
                (x, y) = room.center()
                player.x = x
                player.y = y
                old_room = room
            else:
                # generate corridors depending on proportions passed into
                #   make_map function
                (new_x, new_y) = room.center()
                (prev_x, prev_y) = old_room.center()
                randpool = ratio_hv + ratio_vh + ratio_d
                hv = ratio_hv
                vh = ratio_hv + ratio_vh
                roll = uniform(0, randpool)
                if roll < hv:
                    # first move horizontally, then vertically
                    self.create_h_tunnel(prev_x, new_x, prev_y)
                    self.create_v_tunnel(prev_y, new_y, new_x)
                elif roll < vh:
                    # first move vertically, then horizontally
                    self.create_v_tunnel(prev_y, new_y, prev_x)
                    self.create_h_tunnel(prev_x, new_x, new_y)
                else:
                    # draw diagonal hallways
                    self.create_d_tunnel(prev_x, prev_y, new_x, new_y)
                old_room = room

    def make_halls_random(self, space, player, ratio_vh, ratio_hv, ratio_d):
        '''Add halls to the map between rooms in random order.'''
        old_room = None
        rooms = list(self.rooms)
        while rooms:
            room = choice(rooms)
            rooms.remove(room)
            if old_room is None:
                (x, y) = room.center()
                player.x = x
                player.y = y
                old_room = room
            else:
                # generate corridors depending on proportions passed into
                #   make_map function
                (new_x, new_y) = room.center()
                (prev_x, prev_y) = old_room.center()
                randpool = ratio_hv + ratio_vh + ratio_d
                hv = ratio_hv
                vh = ratio_hv + ratio_vh
                roll = uniform(0, randpool)
                if roll < hv:
                    # first move horizontally, then vertically
                    self.create_h_tunnel(prev_x, new_x, prev_y)
                    self.create_v_tunnel(prev_y, new_y, new_x)
                elif roll < vh:
                    # first move vertically, then horizontally
                    self.create_v_tunnel(prev_y, new_y, prev_x)
                    self.create_h_tunnel(prev_x, new_x, new_y)
                else:
                    # draw diagonal hallways
                    self.create_d_tunnel(prev_x, prev_y, new_x, new_y)
                old_room = room

    def game_map_to_bool_array(self):
        '''Get a multidimensional array of bools describing map walkability.
        Passed into MapGraph to decouple the MapGraph class from specific
        GameMap implementation detail.
        '''
        return [[self.tiles[x][y].blocked for y in range(self.height)]
                for x in range(self.width)]
