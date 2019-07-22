# -*- coding: utf-8 -*-
"""
Created on Tue Jun 25 20:47:16 2019

@author: theoldestnoob
"""

from random import uniform
from random import choice
from random import randint
import tcod
import numpy as np

from map_objects.geometry import Rect
from map_objects.geometry import line_lerp_orthogonal
from map_objects.tile import Tile
from map_objects.map_graph import MapGraph
from entity import Entity
from components.fighter import Fighter
from components.ai import BasicMonster
from components.inventory import Inventory
from render_functions import RenderOrder
from components.item import Item
from item_functions import heal, cast_lightning, cast_fireball, cast_confuse
from game_messages import Message


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

    def make_map(self, player, entities, *args, max_monsters_per_room=0,
                 max_items_per_room=0, **kwargs):
        '''Make a big empty map with a wall around the edge. Expected to be
        overloaded by any child classes.
        '''
        # create a big empty map with a wall around the edges
        room = Rect(1, 1, self.width - 3, self.height - 3)
        print(room)
        self.create_room(room)
        self.rooms.append(room)
        self.place_player_vip(player, entities[1])
        self.place_entities(room, entities, max_monsters_per_room,
                            max_items_per_room)

    def make_graph(self):
        '''Generate graph data about the map and store it in self.graph.'''
        tiles = self.game_map_to_walkable_array()
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

    def make_halls(self, player, ratio_vh, ratio_hv, ratio_d):
        '''Add halls to the map betwen rooms in order of room creation.'''
        old_room = None
        for room in self.rooms:
            if old_room is None:
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

    def make_halls_random(self, player, ratio_vh, ratio_hv, ratio_d):
        '''Add halls to the map between rooms in random order.'''
        old_room = None
        rooms = list(self.rooms)
        while rooms:
            room = choice(rooms)
            rooms.remove(room)
            if old_room is None:
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

    def place_player_vip(self, player, vip):
        (x, y) = self.rooms[0].center()
        player.x = x
        player.y = y
        vip.x = x + 1
        vip.y = y

    def place_entities(self, room, entities, max_monsters_per_room,
                       max_items_per_room):
        '''Place entities randomly into a room on the map.'''
        number_of_monsters = randint(0, max_monsters_per_room)
        number_of_items = randint(0, max_items_per_room)

        for i in range(number_of_monsters):
            x, y = choice(room.coords)
            if not any([e for e in entities if e.x == x and e.y == y]):
                if randint(0, 100) < 80:
                    fighter_component = Fighter(hp=10, defense=0, power=3)
                    ai_component = BasicMonster()
                    inv_component = Inventory(5)
                    m_soul = randint(1, 80)
                    monster = Entity(len(entities), x, y, 'o',
                                     tcod.desaturated_green, "Orc",
                                     blocks=True, soul=m_soul,
                                     fighter=fighter_component,
                                     ai=ai_component, inventory=inv_component,
                                     render_order=RenderOrder.ACTOR)
                else:
                    fighter_component = Fighter(hp=16, defense=1, power=4)
                    ai_component = BasicMonster()
                    inv_component = Inventory(10)
                    m_soul = randint(60, 120)
                    monster = Entity(len(entities), x, y, 'T',
                                     tcod.darker_green, "Troll", blocks=True,
                                     soul=m_soul, fighter=fighter_component,
                                     ai=ai_component, inventory=inv_component,
                                     render_order=RenderOrder.ACTOR)

                entities.append(monster)

        for i in range(number_of_items):
            x, y = choice(room.coords)
            if not any([e for e in entities if e.x == x and e.y == y]):
                item_chance = randint(0, 100)
                if item_chance < 70:
                    item_component = Item(use_function=heal, amount=4)
                    item = Entity(len(entities), x, y, '!', tcod.violet,
                                  "Healing Potion",
                                  render_order=RenderOrder.ITEM,
                                  item=item_component)
                elif item_chance < 80:
                    msg_str = (f"Left-click a target tile for the fireball, "
                               f"or right-click to cancel.")
                    msg = Message(msg_str, tcod.light_cyan)
                    item_component = Item(use_function=cast_fireball,
                                          targeting=True,
                                          targeting_message=msg,
                                          damage=12, radius=3)
                    item = Entity(len(entities), x, y, "#", tcod.red,
                                  "Fireball Scroll",
                                  render_order=RenderOrder.ITEM,
                                  item=item_component)
                elif item_chance < 90:
                    msg_str = (f"Left-click an enemy to confuse it, "
                               f"or right-click to cancel")
                    msg = Message(msg_str, tcod.light_cyan)
                    item_component = Item(use_function=cast_confuse,
                                          targeting=True,
                                          targeting_message=msg)
                    item = Entity(len(entities), x, y, "#", tcod.light_pink,
                                  "Confusion Scroll",
                                  render_order=RenderOrder.ITEM,
                                  item=item_component)
                else:
                    item_component = Item(use_function=cast_lightning,
                                          damage=20, max_range=5)
                    item = Entity(len(entities), x, y, "#", tcod.yellow,
                                  "Lightning Scroll",
                                  render_order=RenderOrder.ITEM,
                                  item=item_component)
                entities.append(item)

    def game_map_to_walkable_array(self):
        '''Return a multidimensional array of bools describing map walkability.
        Passed into MapGraph to decouple the MapGraph class from specific
        GameMap implementation detail.
        '''
        return [[not self.tiles[x][y].blocked for y in range(self.height)]
                for x in range(self.width)]

    def game_map_to_transparent_array(self):
        '''Return a multidimensional array of bools describing map
        transparency. Passed into tcod map for fov calculations.
        '''
        return [[not self.tiles[x][y].block_sight for y in range(self.height)]
                for x in range(self.width)]

    def game_map_to_numpy_array(self):
        numpy_array = np.empty([self.height, self.width], dtype=np.int8)
        for y in range(self.height):
            for x in range(self.width):
                if self.tiles[x][y].blocked:
                    numpy_array[y][x] = 0
                else:
                    numpy_array[y][x] = 1

        return numpy_array
