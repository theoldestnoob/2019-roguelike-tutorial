# -*- coding: utf-8 -*-
"""
Created on Tue Jun 25 20:47:16 2019

@author: theoldestnoob
"""

from time import sleep
import tcod
from collections import deque

from map_objects.geometry import Rect
from map_objects.geometry import line_lerp_orthogonal
from map_objects.tile import Tile
from render_functions import draw_map


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

    def find_room_neighbors(self):
        # flood fill from each room to find its neighbors
        for room in self.rooms:
            node = RoomNode(room)
            room_x, room_y = room.center()
            others = [k for k in self.rooms if k is not room]
            # searched = [[False for y in range(self.height)]
            #             for x in range(self.width)]
            if self.debug:
                draw_map(self.con, self, self.width, self.height,
                         {"dark_wall": tcod.Color(0, 0, 100),
                          "dark_ground": tcod.Color(50, 50, 150)})
                tcod.console_flush()
            # self.find_room_neigh_recurse(room, others, room_x, room_y,
            #                             node.neighbors, searched)
            node.neighbors = self.find_room_neigh_iter(room, others)
            if self.debug:
                print(f"node: {node}")
            self.nodes.append(node)

    def find_room_neigh_recurse(self, room, others, x, y, neighbors, searched):
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
            self.find_room_neigh_recurse(room, others, x + 1, y,
                                         neighbors, searched)
        if not searched[x - 1][y] and not self.tiles[x - 1][y].blocked:
            self.find_room_neigh_recurse(room, others, x - 1, y,
                                         neighbors, searched)
        if not searched[x][y + 1] and not self.tiles[x][y + 1].blocked:
            self.find_room_neigh_recurse(room, others, x, y + 1,
                                         neighbors, searched)
        if not searched[x][y - 1] and not self.tiles[x][y - 1].blocked:
            self.find_room_neigh_recurse(room, others, x, y - 1,
                                         neighbors, searched)

    def find_room_neigh_iter(self, room, others):
        # room: room to find neighbors of
        # others: other rooms that may be neighbors
        # we assume no others overlap room
        x0, y0 = room.center()
        searched = [[False for y in range(self.height)]
                    for x in range(self.width)]
        neighbors = []
        searchq = deque([(x0, y0)])

        while searchq:
            x, y = searchq.popleft()
            searched[x][y] = True
            if self.debug:
                tcod.console_set_char_background(self.con, x, y,
                                                 tcod.red,
                                                 tcod.BKGND_SET)
                tcod.console_blit(self.con, 0, 0, self.width, self.height,
                                  0, 0, 0)
                sleep(0.001)
                tcod.console_flush()

            for z in others:
                if z.contains(x, y):
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


class RoomNode():
    def __init__(self, rect):
        self.rect = rect
        self.neighbors = []

    def __str__(self):
        return f"RoomNode({self.rect}, {self.neighbors})"
