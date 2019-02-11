import json
import random
import math

import pygame

import tiles
import group
import goals
import game


class ContentGen:
    def __init__(self, settings, game_obj):
        self.settings = settings
        self.game = game_obj
        self.tiles_generated = 0
        self.generates_tiles = False
        self.generates_goals = False

    def gen_tile(self):
        raise NotImplementedError

    def gen_goal(self, player):
        raise NotImplementedError


class TreasureContentGen(ContentGen):

    def __init__(self, settings, game_obj):
        super().__init__(settings, game_obj)
        self.generates_tiles = True
        self.generates_goals = True

        treasulrelist = json.load(open('treasurelist.json'))
        # If the game currently has all the possible treasures it will freeze forever
        # TODO fix it
        while True:
            self.treasure = random.choice(treasulrelist)
            self.name = self.treasure["name"]
            if not(self.name in game_obj.squad.equipment.keys()):
                break
        if self.treasure["special"]:
            self.generates_goals = False
        game_obj.squad.equipment[self.name] = 0

    def gen_tile(self):
        try:
            tile_obj = tiles.Treasure(self.settings, -1, -1, self.treasure)
        except ValueError as e:
            print(self.treasure["color"])
            raise e
        self.tiles_generated += 1
        return tile_obj

    def gen_goal(self, player):
        aim = random.randint(math.ceil(self.tiles_generated * 2/3), self.tiles_generated)
        goal_obj = goals.GetTreasureGoal(player, self.game, self.treasure, aim)
        return goal_obj


class TrapContentGen(ContentGen):
    possible_traps = [tiles.StunTrap, tiles.VisionTrap]

    def __init__(self, settings, game_obj):
        super().__init__(settings, game_obj)
        self.generates_tiles = True

        self.traps_generated = []

    def gen_tile(self):
        chosen_trap = random.choice(TrapContentGen.possible_traps)
        tile_obj = chosen_trap(self.settings, -1, -1)
        self.traps_generated.append(tile_obj)
        self.tiles_generated += 1
        return tile_obj


class OutOfLabirynthContentGen(ContentGen):
    def __init__(self, settings, game_obj):
        super(OutOfLabirynthContentGen, self).__init__(settings, game_obj)
        self.generates_goals = True

    def gen_goal(self, player):
        if random.randint(0, 1):
            goal_obj = goals.OutOfLabyrinthGoalLessThan(player, self.game, 100)
            return goal_obj
        else:
            goal_obj = goals.OutOfLabyrinthGoalMoreThan(player, self.game, 100)
            return goal_obj


class WeaponContentGen(ContentGen):
    def __init__(self, settings, game_obj):
        super(WeaponContentGen, self).__init__(settings, game_obj)
        self.generates_tiles = True

    def gen_tile(self):
        tile_obj = tiles.Weapon(self.settings, -1, -1)
        self.tiles_generated += 1
        return tile_obj


class MinotaurContectGen(ContentGen):
    def __init__(self, settings, game_obj):
        super(MinotaurContectGen, self).__init__(settings, game_obj)
        self.generates_goals = True

    def gen_goal(self, player):
        if random.randint(0, 1):
            goal_obj = goals.DieByMinotaurGoal(player, self.game)
        else:
            goal_obj = goals.KillMinotaurGoal(player, self.game)
        return goal_obj
