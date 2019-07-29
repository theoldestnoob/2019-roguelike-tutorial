# -*- coding: utf-8 -*-
"""
Created on Tue Jun 25 19:29:03 2019

@author: theoldestnoob
"""

import math
import tcod

from render_functions import RenderOrder


class Entity:
    """
    A generic object to represent players, enemies, items, etc.
    """
    def __init__(self, ident, x, y, char, color, name, soul=0, blocks=False,
                 fov_map=None, fighter=None, ai=None, speed=10,
                 render_order=RenderOrder.CORPSE, item=None, inventory=None,
                 stairs=None):
        # every entity has an ident and a name
        # TODO: add component for insubstantiality, or just test on blocks
        #       for if we can walk into stuff or not, or add a variable for
        #       the "plane" an entity exists in (material, astral, etc)
        self.ident = ident
        self.name = name
        # TODO: switch to "render_ascii" or "render_tcod" component
        self.x = x
        self.y = y
        self.char = char
        self.color = color
        self.render_order = render_order
        # TODO: move to "soul" component with other soul-related attributes
        self.soul = soul
        self.blocks = blocks
        # TODO: move to "fov" component?
        self.fov_recompute = False
        self.fov_map = fov_map
        # TODO: move to "actor" component? bundle in "ai" component?
        self.speed = speed
        self.time_to_act = int(100 / speed)
        # Entity components
        self.fighter = fighter
        if self.fighter:
            self.fighter.owner = self
        self.ai = ai
        if self.ai:
            self.ai.owner = self
        self.item = item
        if self.item:
            self.item.owner = self
        self.inventory = inventory
        if self.inventory:
            self.inventory.owner = self
        self.stairs = stairs
        if self.stairs:
            self.stairs.owner = self

    def move(self, dx, dy):
        '''Change Entity location by dx, dy.'''
        self.x += dx
        self.y += dy
        self.fov_recompute = True

    def move_towards(self, target_x, target_y, game_map, entities):
        '''Move Entity in the direction of target_x, target_y.'''
        dx = target_x - self.x
        dy = target_y - self.y
        distance = math.sqrt(dx ** 2 + dy ** 2)

        dx = int(round(dx / distance))
        dy = int(round(dy / distance))

        print(f"dx: {dx}, dy: {dy}, dist: {distance}")

        if not (game_map.is_blocked(self.x + dx, self.y + dy)
                or get_blocking_entities_at_location(entities, self.x + dx,
                                                     self.y + dy)):
            self.move(dx, dy)

    def distance_to(self, other):
        '''Return the distance between Entity and other Entity.'''
        dx = other.x - self.x
        dy = other.y - self.y
        return (math.sqrt(dx ** 2 + dy ** 2))

    def distance(self, x, y):
        '''Return the distance between Entity and (x, y).'''
        return (math.sqrt((x - self.x) ** 2 + (y - self.y) ** 2))

    def move_astar(self, target, entities, game_map):
        '''Calculate the A* path toward a target Entity and take the first
        move along the path towards it.'''
        # set up numpy array for use in tcod astar path calculation
        map_array = game_map.game_map_to_numpy_array()

        # add blocking entities to numpy array
        for entity in entities:
            if entity.blocks and entity is not self and entity is not target:
                map_array[entity.y][entity.x] = 0

        # create astar pathfinder and get a path
        astar = tcod.path.AStar(map_array)
        path = astar.get_path(self.y, self.x, target.y, target.x)

        # check if the path exists and is < 25 steps, if so move there
        if path and len(path) < 25:
            y, x = path[0]
            dx = x - self.x
            dy = y - self.y
            self.move(dx, dy)
        # otherwise, fall back to dumb move_towards method
        else:
            self.move_towards(target.x, target.y, game_map, entities)


def get_blocking_entities_at_location(entities, dest_x, dest_y):
    '''Return the first Entity in entities list on map at dest_x, dest_y.'''
    for entity in entities:
        if entity.blocks and entity.x == dest_x and entity.y == dest_y:
            return entity
    return None
