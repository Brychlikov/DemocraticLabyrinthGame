import random
import math

import tiles
import group
import goals
import game


class TreasureContentGen:

    def __init__(self, settings):
        self.settings = settings
        self.name = str([random.choice('qwertyuiopasdfghjklzxcvbnm') for i in range(8)])
        self.tiles_generated = 0

    def gen_tile(self):
        tile_obj = tiles.Treasure(self.settings, -1, -1, self.name)
        self.tiles_generated += 1
        return tile_obj

    def gen_goal(self, player, game_obj):
        aim = random.randint(math.ceil(self.tiles_generated * 2/3), self.tiles_generated)
        goal_obj = goals.GetTreasureGoal(player, game_obj, self.name, aim)
        return goal_obj
