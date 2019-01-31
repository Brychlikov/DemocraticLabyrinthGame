import json
import random
import math

import pygame

import tiles
import group
import goals
import game


class TreasureContentGen:

    def __init__(self, settings, game_obj):
        self.settings = settings

        treasulrelist = json.load(open('treasurelist.json'))
        # If the game currently has all the possible treasures it will freeze forever
        # TODO fix it
        while True:
            self.treasure = random.choice(treasulrelist)
            self.name = self.treasure["name"]
            if not(self.name in game_obj.squad.equipment.keys()):
                break
        game_obj.squad.equipment[self.name] = 0
        self.tiles_generated = 0

    def gen_tile(self):
        try:
            tile_obj = tiles.Treasure(self.settings, -1, -1, self.name)
        except ValueError as e:
            print(self.treasure["color"])
            raise e
        self.tiles_generated += 1
        return tile_obj

    def gen_goal(self, player, game_obj):
        aim = random.randint(math.ceil(self.tiles_generated * 2/3), self.tiles_generated)
        goal_obj = goals.GetTreasureGoal(player, game_obj, self.name, aim)
        return goal_obj
