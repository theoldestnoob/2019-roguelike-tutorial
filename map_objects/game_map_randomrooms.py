# -*- coding: utf-8 -*-
"""
Created on Thu Jun 27 00:43:14 2019

@author: theoldestnoob
"""

from random import seed as randseed
from random import randint
from random import uniform
from time import sleep
import tcod

from map_objects.geometry import Rect
from map_objects.geometry import line_lerp_orthogonal
from map_objects.tile import Tile
from render_functions import draw_map


class GameMapRandomRooms:
    def __init__(self, width, height, seed, con, debug=False):
        self.width = width
        self.height = height
        self.seed = seed
        self.tiles = self.initialize_tiles()
        self.rooms = []
        self.nodes = []
        self.con = con
        self.debug = debug

    def initialize_tiles(self):
        tiles = [[Tile(True) for y in range(self.height)] for x in range (self.width)]

        return tiles

    def is_blocked(self, x, y):
        if self.tiles[x][y].blocked:
            return True

        return False

    def make_map(self, player, *args,
                 max_rooms=30, room_min_size=6, room_max_size=10,
                 ratio_vh=1, ratio_hv=1, ratio_d=0, **kwargs):
        # setup
        map_width = self.width
        map_height = self.height
        randseed(self.seed)

        # create a map of randomly placed rooms
        rooms = []
        num_rooms = 0

        for r in range(max_rooms):
            # random width and height
            w = randint(room_min_size, room_max_size)
            h = randint(room_min_size, room_max_size)
            # random position inside map bounds
            x = randint(0, map_width - w - 1)
            y = randint(0, map_height - h - 1)

            # "Rect" class makes rectangles easier to work with
            new_room = Rect(x, y, w, h)

            # see if any other rooms intersect with this one
            for other_room in rooms:
                if new_room.intersect(other_room):
                    break
            else:
                # no intersections, so this room is valid

                # "paint" it to the map's tiles
                self.create_room(new_room)

                # center coordinates of new room, will be useful later
                (new_x, new_y) = new_room.center()

                if num_rooms == 0:
                    # this is the first room, player starts here
                    player.x = new_x
                    player.y = new_y
                else:
                    # all rooms after the first:
                    #  connect it to the previous room with a tunnel

                    # center coordinates of previous room
                    (prev_x, prev_y) = rooms[num_rooms - 1].center()

                    # generate corridors depending on proportions passed into
                    #   make_map function
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

                # finally, append the new room to the list
                rooms.append(new_room)
                num_rooms += 1

        # save our list of rooms for later
        self.rooms = rooms

    def make_graph(self):
        # flood fill from each room to find its neighbors
        for room in self.rooms:
            node = RoomNode(room)
            room_x, room_y = room.center()
            others = [k for k in self.rooms if k is not room]
            searched = [[False for y in range(self.height)]
                        for x in range(self.width)]
            if self.debug:
                draw_map(self.con, self, self.width, self.height,
                         {"dark_wall": tcod.Color(0, 0, 100),
                          "dark_ground": tcod.Color(50, 50, 150)})
                tcod.console_flush()
            self.flood_search(room, others, room_x, room_y,
                              node.neighbors, searched)
            if self.debug:
                print(f"node: {node}")
            self.nodes.append(node)

    def flood_search(self, room, others, x, y, neighbors, searched):
        if self.debug:
            tcod.console_set_char_background(self.con, x, y,
                                             tcod.red,
                                             tcod.BKGND_SET)
            tcod.console_flush()
            sleep(0.010)
        searched[x][y] = True
        for z in others:
            if z.contains(x, y):
                neighbors.append(z)
                return
        if not searched[x + 1][y] and not self.tiles[x + 1][y].blocked:
            self.flood_search(room, others, x + 1, y, neighbors, searched)
        if not searched[x - 1][y] and not self.tiles[x - 1][y].blocked:
            self.flood_search(room, others, x - 1, y, neighbors, searched)
        if not searched[x][y + 1] and not self.tiles[x][y + 1].blocked:
            self.flood_search(room, others, x, y + 1, neighbors, searched)
        if not searched[x][y - 1] and not self.tiles[x][y - 1].blocked:
            self.flood_search(room, others, x, y - 1, neighbors, searched)

    def create_room(self, room):
        # go through the tiles in the rectangle and make them passable
        for x in range(room.x1 + 1, room.x2):
            for y in range(room.y1 + 1, room.y2):
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


class RoomNode():
    def __init__(self, rect):
        self.rect = rect
        self.neighbors = []

    def __str__(self):
        return f"RoomNode({self.rect}, {self.neighbors})"
