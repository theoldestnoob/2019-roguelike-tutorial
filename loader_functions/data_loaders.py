# -*- coding: utf-8 -*-
"""
Created on Sat Jul 27 19:36:29 2019

@author: theoldestnoob
"""

import shelve
import os
from collections import deque


def save_game(player, vip, entities, controlled_entity, curr_entity,
              game_state, prev_state, message_log, game_map, timeq,
              next_turn, render_update, targeting_item):
    # build a list of entity indices from timeq to store
    timeq_indices = []
    for entity in timeq:
        timeq_indices.append(entities.index(entity))
    # store all of our game data
    with shelve.open("savegame", "n") as data_file:
        data_file["player_index"] = entities.index(player)
        data_file["vip_index"] = entities.index(vip)
        data_file["controlled_entity_index"] = entities.index(controlled_entity)
        data_file["current_entity_index"] = entities.index(curr_entity)
        data_file["entities"] = entities
        data_file["game_map"] = game_map
        data_file["message_log"] = message_log
        data_file["timeq_indices"] = timeq_indices
        data_file["game_state"] = game_state
        data_file["prev_state"] = prev_state
        data_file["next_turn"] = next_turn
        data_file["render_update"] = render_update
        data_file["targeting_item"] = targeting_item


def load_game(constants):
    # check if the file exists before loading it
    if not os.path.isfile("savegame.dat"):
        raise FileNotFoundError

    # get all of our game data from the shelf
    with shelve.open("savegame", "r") as data_file:
        player_index = data_file["player_index"]
        vip_index = data_file["vip_index"]
        controlled_entity_index = data_file["controlled_entity_index"]
        current_entity_index = data_file["current_entity_index"]
        entities = data_file["entities"]
        game_map = data_file["game_map"]
        message_log = data_file["message_log"]
        timeq_indices = data_file["timeq_indices"]
        game_state = data_file["game_state"]
        prev_state = data_file["prev_state"]
        next_turn = data_file["next_turn"]
        render_update = data_file["render_update"]
        targeting_item = data_file["targeting_item"]

    # assign entities from indices
    player = entities[player_index]
    vip = entities[vip_index]
    controlled_entity = entities[controlled_entity_index]
    current_entity = entities[current_entity_index]

    # rebuild time queue
    timeq = deque()
    for index in timeq_indices:
        timeq.append(entities[index])

    return (player, vip, entities, controlled_entity, current_entity,
            game_state, prev_state, message_log, game_map, timeq,
            next_turn, render_update, targeting_item)
