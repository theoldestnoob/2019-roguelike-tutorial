# -*- coding: utf-8 -*-
"""
Created on Wed Jun 26 23:04:23 2019

@author: theoldestnoob
"""

from random import seed as randseed
from random import randint
from random import uniform

from map_objects.geometry import Rect
from map_objects.geometry import Circle
from map_objects.game_map import GameMap


# TODO: store BSP tree structure for later use when generating halls
class GameMapBSP(GameMap):
    '''GameMap that places rooms based on Binary Space Partitioning.'''
    def make_map(self, player, entities, *args,
                 room_min_size=8, room_max_size=15, min_rooms=8, max_rooms=30,
                 bsp_depth=4, bsp_range=0.15,
                 ratio_vh=1, ratio_hv=1, ratio_d=0, hall_rand=False,
                 circ_rooms=0, rect_rooms=1,
                 max_monsters_per_room=0, **kwargs):
        map_width = self.width - 1
        map_height = self.height - 1
        randseed(self.seed)
        self.rect_rooms = rect_rooms
        self.circ_rooms = circ_rooms

        while True:
            self.rooms = []
            self.tiles = self.initialize_tiles()
            parts = []
            space = Rect(0, 0, map_width, map_height)

            self.partition(space, parts, bsp_depth, bsp_range,
                           room_min_size, room_max_size)
            # for part in parts:
            #    self.rooms.append(part)
            self.place_rooms(parts, room_min_size, room_max_size)
            numrooms = len(self.rooms)
            if min_rooms < numrooms < max_rooms:
                break
        if hall_rand:
            self.make_halls_random(space, player, ratio_vh, ratio_hv, ratio_d)
        else:
            self.make_halls(space, player, ratio_vh, ratio_hv, ratio_d)
        for room in self.rooms:
            self.place_entities(room, entities, max_monsters_per_room)

    def partition(self, space, parts, bsp_depth, bsp_range,
                  room_min_size, room_max_size):
        '''Divide space up into Rects that cover the entire space, that are all
        adjacent but do not intersect.
        '''
        if (bsp_depth == 0 or
                (space.h < room_max_size + 2 and space.w < room_max_size + 2)):
            part = Rect(space.x1, space.y1, space.w, space.h)
            parts.append(part)
            return True
        bsp_depth -= 1
        xy = randint(0, 1)
        if space.w >= room_min_size + 2 and space.w <= room_max_size - 2:
            xy = 0
        elif space.h >= room_min_size + 2 and space.h <= room_max_size - 2:
            xy = 1
        part_ratio = uniform(0.5 - bsp_range, 0.5 + bsp_range)
        if xy == 0:
            # horizontal split
            part_height = int(part_ratio * space.h) - 1
            part_a_h = part_height
            part_b_h = space.h - part_height - 1
            part_a = Rect(space.x1, space.y1, space.w, part_a_h)
            part_b = Rect(space.x1, space.y1 + part_a_h + 1, space.w, part_b_h)
        else:
            # vertical split
            part_width = int(part_ratio * space.w) - 1
            part_a_w = part_width
            part_b_w = space.w - part_width - 1
            part_a = Rect(space.x1, space.y1, part_a_w, space.h)
            part_b = Rect(space.x1 + part_a_w + 1, space.y1, part_b_w, space.h)

        # recurse
        self.partition(part_a, parts, bsp_depth, bsp_range,
                       room_min_size, room_max_size)
        self.partition(part_b, parts, bsp_depth, bsp_range,
                       room_min_size, room_max_size)

    def place_rooms(self, parts, room_min_size, room_max_size):
        '''Randomly put rooms into each partitioned space that's big enough.'''
        for part in parts:
            bounds = Rect(part.x1 + 1, part.y1 + 1, part.w - 2, part.h - 2)
            if bounds.h < room_min_size or bounds.w < room_min_size:
                continue
            roomw = randint(room_min_size, room_max_size)
            roomh = randint(room_min_size, room_max_size)
            if roomw > bounds.w:
                roomw = bounds.w
            if roomh > bounds.h:
                roomh = bounds.h
            # print(f"Bounds: {bounds}, Roomw: {roomw}, Roomh: {roomh}")
            if bounds.x1 == bounds.x1 + bounds.w - roomw:
                roomx = bounds.x1
            else:
                roomx = randint(bounds.x1, bounds.x1 + (bounds.w - roomw))
            if bounds.y1 == bounds.y1 + bounds.h - roomh:
                roomy = bounds.y1
            else:
                roomy = randint(bounds.y1, bounds.y1 + (bounds.h - roomh))
            room = Rect(roomx, roomy, roomw, roomh)

            randpool = self.circ_rooms + self.rect_rooms
            roll = uniform(0, randpool)
            if roll < self.circ_rooms:
                (c_x, c_y) = room.center()
                r = min(room.w, room.h) // 2
                circ = Circle(c_x, c_y, r)
                # print(f"{circ}")
                self.create_room(circ)
                self.rooms.append(circ)
            else:
                # print(f"{room}")
                self.create_room(room)
                self.rooms.append(room)
