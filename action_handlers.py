# -*- coding: utf-8 -*-
"""
Created on Fri Jul 12 22:46:03 2019

@author: theoldestnoob
"""

import tcod
import tcod.event
from random import randint
from collections import deque

from render_functions import RenderOrder, display_space, render_all
from fov_functions import initialize_fov, init_fov_entity0, recompute_fov
from entity import Entity
from components.fighter import Fighter
from components.ai import IdleMonster
from components.inventory import Inventory
from game_messages import Message
from death_functions import kill_entity
from game_states import GameStates


# TODO: man I have to pass a lot of stuff in and out of these guys
#       there must be a better way?
def handle_entity_actions(actions, in_handle, entities, game_map, console,
                          message_log, controlled_entity, player, game_state,
                          prev_state, targeting_item, debug_f):
    action_cost = 0
    next_turn = True
    controlled_entity = controlled_entity
    render_update = False
    game_state = game_state
    prev_state = prev_state
    targeting_item = targeting_item

    # TODO: rewrite to use object features: while len(action) > 0: action = action.popleft()
    for action in actions:
        # turn actions
        message = action.get("message")
        move = action.get("move")
        move_astar = action.get("move_astar")
        melee = action.get("melee")
        wait = action.get("wait")
        possess = action.get("possess")
        unpossess = action.get("unpossess")
        pickup = action.get("pickup")
        item_added = action.get("item_added")
        use_item = action.get("use_item")
        drop_item = action.get("drop_item")
        item_dropped = action.get("item_dropped")
        targeting = action.get("targeting")
        cancel_target = action.get("cancel_target")
        dead = action.get("dead")
        xp = action.get("xp")

        if message:  # {"message": message_string}
            render_update = True
            message_log.add_message(message)

        if move:  # {"move": (entity, dx, dy)}
            action_cost = 100
            next_turn = True
            entity, dx, dy = move
            # don't let entities move out of the map's boundaries
            if not (entity.x + dx < 0 or entity.y + dy < 0
                    or entity.x + dx >= game_map.width
                    or entity.y + dy >= game_map.height):
                entity.move(dx, dy)

        if move_astar:  # {"move_astar": (entity, target)}
            action_cost = 100
            next_turn = True
            entity, target = move_astar
            entity.move_astar(target, entities, game_map)

        if melee:  # {"melee": (entity, target)}
            action_cost = 100
            next_turn = True
            entity, target = melee
            melee_results = entity.fighter.attack(target)
            for action in melee_results:
                xp = action.get("xp")
                if xp:
                    action["xp"] = [entity, xp[1]]
            actions.extend(melee_results)

        if wait:  # {"wait": int_time}
            action_cost = wait
            next_turn = True

        if possess:  # {"possess": target}
            action_cost = 100
            next_turn = True
            render_update = True
            target = possess
            result_str = f"You possess the {target.name}!"
            message_log.add_message(Message(result_str, tcod.light_gray))
            controlled_entity = target

        if unpossess:  # {"unpossess": (dest_x, dest_y)}
            action_cost = 100
            next_turn = True
            render_update = True
            dest_x, dest_y = unpossess
            result_str = f"You stop possessing the {controlled_entity.name}!"
            message_log.add_message(Message(result_str, tcod.light_gray))
            # controlled_entity = entities[0]
            controlled_entity = player
            controlled_entity.x = dest_x
            controlled_entity.y = dest_y
            controlled_entity.fov_recompute = True

        if pickup and controlled_entity.inventory:
            next_turn = True
            render_update = True
            for entity in entities:
                if (entity.item
                        and entity.x == controlled_entity.x
                        and entity.y == controlled_entity.y):
                    results = controlled_entity.inventory.add_item(entity)
                    actions.extend(results)
                    break
            else:
                msg_str = "There is nothing here to pick up."
                message_log.add_message(Message(msg_str, tcod.yellow))

        if item_added:
            entities.remove(item_added)

        if use_item:
            render_update = True
            use_results = controlled_entity.inventory.use(use_item,
                                                          entities=entities)
            if any([u_r for u_r in use_results if u_r.get("consumed")]):
                action_cost = 50
                next_turn = True
                # TODO: hack to clear targeting after item use, don't like it
                if use_item is targeting_item:
                    targeting_item = None
                    game_state = prev_state
            # TODO: hack to clear targeting after item use, don't like it
            else:
                use_item.item.target_x = None
                use_item.item.target_y = None
            actions.extend(use_results)

        if drop_item:
            render_update = True
            drop_results = controlled_entity.inventory.drop(drop_item)
            if any([d_r for d_r in drop_results if d_r.get("item_dropped")]):
                action_cost = 50
                next_turn = True
            actions.extend(drop_results)

        if item_dropped:
            entities.append(item_dropped)

        # TODO: There has to be a better way to handle targeting than this
        if targeting:
            render_update = True
            next_turn = False
            prev_state = GameStates.NORMAL_TURN
            game_state = GameStates.TARGETING
            targeting_item = targeting
            message_log.add_message(targeting_item.item.targeting_message)

        if cancel_target:
            game_state = prev_state
            render_update = True
            next_turn = False
            message_log.add_message(Message("Targeting cancelled",
                                            tcod.light_cyan))

        if dead:  # {"dead": entity}
            render_update = True
            if dead == controlled_entity:
                controlled_entity = entities[0]
                controlled_entity.x = dead.x
                controlled_entity.y = dead.y
                controlled_entity.fov_recompute = True
            message = kill_entity(dead)
            message_log.add_message(message)

        if xp:  # {"xp": [entity, xp]}
            print(xp)
            entity, xp_gain = xp
            print(entity)
            print(xp_gain)
            if entity is not None and entity.level:
                level_up = entity.level.add_xp(xp_gain)
                msg_str = f"{entity.name} gains {xp_gain} experience points."
                msg = Message(msg_str, tcod.white)
                message_log.add_message(msg)
                if level_up:
                    msg_str = (f"{entity.name} grows stronger!  They have "
                               f"reached level {entity.level.current_level}!")
                    message_log.add_message(Message(msg_str, tcod.yellow))

    return (action_cost, next_turn, controlled_entity, render_update,
            game_state, prev_state, targeting_item)


def handle_player_actions(actions, in_handle, entities, game_map, console,
                          panel_ui, panel_map, curr_entity, controlled_entity,
                          player, vip, omnivision, message_log,
                          mouse_x, mouse_y, timeq, game_state, prev_state,
                          constants, debug_f):
    # pull constants
    mapset = constants["mapset"]
    fov_radius = constants["fov_radius"]
    fov_light_walls = constants["fov_light_walls"]
    fov_algorithm = constants["fov_algorithm"]
    # setup stuff
    next_turn = False
    curr_entity = curr_entity
    controlled_entity = controlled_entity
    player = player
    vip = vip
    entities = entities
    omnivision = omnivision
    timeq = timeq
    want_exit = False
    render_update = False

    for action in actions:
        # out of turn actions
        want_exit = action.get("exit")
        fullscreen = action.get("fullscreen")
        mousemotion = action.get("mousemotion")
        msg_up = action.get("msg_up")
        msg_down = action.get("msg_down")
        show_inventory = action.get("show_inventory")
        drop_inventory = action.get("drop_inventory")
        take_stairs = action.get("take_stairs")

        # debug actions
        omnivis = action.get("omnivis")
        switch_char = action.get("switch_char")
        map_gen = action.get("map_gen")
        graph_gen = action.get("graph_gen")
        test = action.get("test")

        if want_exit:  # {"exit": True}
            if game_state in (GameStates.SHOW_INVENTORY,
                              GameStates.DROP_INVENTORY):
                game_state = prev_state
                want_exit = False
                render_update = True
            else:
                want_exit = True

        if fullscreen:  # {"fullscreen": True}
            next_turn = False
            render_update = True
            tcod.console_set_fullscreen(not tcod.console_is_fullscreen())

        # TODO: I'm not super happy about how this works
        #       but not sure how to elegantly tag render_update when the list
        #       of entities being moused over changes
        if mousemotion:  # {"mousemotion": (x, y)}
            render_update = True

        if msg_up:
            if message_log.bottom < message_log.length - message_log.height:
                message_log.scroll(1)
                render_update = True

        if msg_down:
            if message_log.bottom > 0:
                message_log.scroll(-1)
                render_update = True

        if show_inventory:
            render_update = True
            next_turn = False
            prev_state = game_state
            game_state = GameStates.SHOW_INVENTORY

        if drop_inventory:
            render_update = True
            next_turn = False
            prev_state = game_state
            game_state = GameStates.DROP_INVENTORY

        if take_stairs:
            for entity in entities:
                if (entity.stairs and entity.x == controlled_entity.x
                        and entity.y == controlled_entity.y):
                    game_map.dlevel += 1
                    game_map.tiles = game_map.initialize_tiles()
                    entities = [player, controlled_entity]
                    game_map.make_map(player, entities, **mapset)
                    # set up time system
                    actors = [e for e in entities if e.ai]
                    timeq = deque(sorted(actors, key=lambda e: e.time_to_act))
                    curr_entity = timeq.popleft()
                    next_turn = True
                    # FOV calculation setup
                    render_update = True
                    for entity in actors:
                        if entity.ident == 0:
                            entity.fov_map = init_fov_entity0(game_map)
                        else:
                            entity.fov_map = initialize_fov(game_map)
                        recompute_fov(game_map, entity, fov_radius,
                                      fov_light_walls, fov_algorithm)
                    break
            else:
                msg = Message("There are no stairs here.", tcod.yellow)
                message_log.add_message(msg)

        if omnivis:  # {"omnivis": True}
            next_turn = False
            render_update = True
            omnivision = not omnivision

        if switch_char:  # {"switch_char": True}
            next_turn = False
            render_update = True
            index = controlled_entity.ident + 1
            if index >= len(entities):
                controlled_entity = entities[0]
            else:
                controlled_entity = entities[index]
            # only switch to controllable entities
            while controlled_entity.soul <= 0:
                index = controlled_entity.ident + 1
                if index >= len(entities):
                    controlled_entity = entities[0]
                else:
                    controlled_entity = entities[index]

        if map_gen:  # {"map_gen": True}
            next_turn = True
            render_update = True
            game_map.seed = randint(0, 99999)
            game_map.tiles = game_map.initialize_tiles()
            player_fighter = Fighter(hp=1, defense=0, power=0)
            vip_fighter = Fighter(hp=30, defense=2, power=5)
            player_ai = IdleMonster()
            vip_ai = IdleMonster()
            vip_inventory = Inventory(26)
            player = Entity(0, 0, 0, "@", tcod.white, "Player", blocks=False,
                            ai=player_ai, render_order=RenderOrder.ACTOR,
                            fighter=player_fighter, speed=25, soul=1)
            vip = Entity(1, 0, 0, "&", tcod.yellow, "VIP", blocks=True,
                         fighter=vip_fighter, ai=vip_ai, soul=10,
                         inventory=vip_inventory,
                         render_order=RenderOrder.ACTOR)
            entities = [player, vip]
            controlled_entity = player
            game_map.make_map(player, entities, **mapset)
            # set up time system
            actors = [e for e in entities if e.ai]
            timeq = deque(sorted(actors, key=lambda e: e.time_to_act))
            curr_entity = timeq.popleft()
            next_turn = True
            # FOV calculation setup
            render_update = True
            for entity in actors:
                if entity.ident == 0:
                    entity.fov_map = init_fov_entity0(game_map)
                else:
                    entity.fov_map = initialize_fov(game_map)
                recompute_fov(game_map, entity, fov_radius, fov_light_walls,
                              fov_algorithm)

        if graph_gen:  # {"graph_gen": True}
            game_map.make_graph()

        if test:  # {"test": True}
            pass

    return (next_turn, curr_entity, controlled_entity, entities, player, vip,
            timeq, omnivision, render_update, want_exit, game_state,
            prev_state)


''' Bunch of stuff pulled out of handle_player_actions to make it less awful:

            if show_vertices:  # {"show_vertices": True}
            for vertex in game_map.graph.vertices:
                display_space(console, vertex.space, tcod.green)
                tcod.console_flush()
                if debug_f:
                    print(f"***Vertex: {vertex}")
                while True:
                    for event in tcod.event.get():
                        in_handle.dispatch(event)
                    action = in_handle.get_user_input()
                    show_vertices = action.get("show_vertices")
                    want_exit = action.get("exit")
                    if show_vertices or want_exit:
                        break
                if want_exit:
                    break
                render_all(console, panel_ui, panel_map, entities, game_map,
                           controlled_entity, screen_width, screen_height,
                           bar_width, panel_ui_width, panel_ui_height,
                           panel_ui_y, panel_map_width, panel_map_height,
                           colors, message_log, mouse_x, mouse_y,
                           omnivision)
                tcod.console_flush()
            render_update = True

        if show_hyperedges:  # {"show_hyperedges": True}
            for edge in game_map.graph.hyperedges:
                display_space(console, edge.space, tcod.green)
                tcod.console_flush()
                if debug_f:
                    print(f"***Hyperedge: {edge}")
                while True:
                    for event in tcod.event.get():
                        in_handle.dispatch(event)
                    action = in_handle.get_user_input()
                    show_hyperedges = action.get("show_hyperedges")
                    want_exit = action.get("exit")
                    if show_hyperedges or want_exit:
                        break
                if want_exit:
                    break
                render_all(console, panel_ui, panel_map, entities, game_map,
                           controlled_entity, screen_width, screen_height,
                           bar_width, panel_ui_width, panel_ui_height,
                           panel_ui_y, panel_map_width, panel_map_height,
                           colors, message_log, mouse_x, mouse_y,
                           omnivision)
                tcod.console_flush()
            render_update = True

        if show_edges:  # {"show_edges": True}
            for edge in game_map.graph.edges:
                display_space(console, edge.space, tcod.green)
                tcod.console_flush()
                if debug_f:
                    print(f"***Edge: {edge}")
                while True:
                    for event in tcod.event.get():
                        in_handle.dispatch(event)
                    action = in_handle.get_user_input()
                    show_edges = action.get("show_edges")
                    want_exit = action.get("exit")
                    if show_edges or want_exit:
                        break
                if want_exit:
                    break
                render_all(console, panel_ui, panel_map, entities, game_map,
                           controlled_entity, screen_width, screen_height,
                           bar_width, panel_ui_width, panel_ui_height,
                           panel_ui_y, panel_map_width, panel_map_height,
                           colors, message_log, mouse_x, mouse_y,
                           omnivision)
                tcod.console_flush()
            render_update = True
'''
