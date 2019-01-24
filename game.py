import random
import threading
import time

import pygame
from dataclasses import dataclass
from queue import Queue

import group
import labgen
import tiles
import server
import contentGen


def wall_graph(wall_list):
    result = {}

    for wall in wall_list:
        if wall.x1 - wall.x2 == 0:  # vertical
            coord1 = (wall.x1 - 1, wall.y1)
            coord2 = wall.x1, wall.y1
        else:  # horizontal
            coord1 = (wall.x1, wall.y1 - 1)
            coord2 = (wall.x1, wall.y1)
        if result.get(coord1):
            result[coord1].append(coord2)
        else:
            result[coord1] = [coord2]
        if result.get(coord2):
            result[coord2].append(coord1)
        else:
            result[coord2] = [coord1]

    return result


@dataclass
class Settings:
    tile_size: int
    width: int
    height: int
    background_color: pygame.Color = pygame.Color(0, 0, 0, 0)
    wall_color: pygame.Color = pygame.Color(0, 0, 255)


class Game:
    def __init__(self, settings: Settings):
        self.settings = settings

        self.board = []
        for i in range(settings.width):
            row = []
            for j in range(settings.height):
                row.append(tiles.Tile(settings, i, j))
            self.board.append(row)

        self.turns = 0
        self.labyrinth_finished = False

        self.frames_until_move = 0

        self.running = False
        self.display: pygame.Surface = None
        self.clock = pygame.time.Clock()
        self.server = None
        self.server_queue = None
        self.new_player_queue = None
        self.goal_queue = None

        self.squad = group.Squad(settings)

        self.all_sprites = pygame.sprite.Group()
        self.all_sprites.add(self.squad)

        self.content_gens = [contentGen.TreasureContentGen(settings,  self) for i in range(6)]
        tiles.Tile.groups.append(self.all_sprites)

        for i in range(40):
            self.add_special_tile()

        self.wall_list = labgen.actually_gen_lab(settings.height)
        self.wall_graph = wall_graph(self.wall_list)

    def init(self):
        pygame.init()
        resolution = (self.settings.width * self.settings.tile_size, self.settings.height * self.settings.tile_size)
        self.display = pygame.display.set_mode(resolution)
        self.running = True

        self.server_queue = Queue()
        self.new_player_queue = Queue()
        self.goal_queue = Queue()
        self.squad.server_queue = self.server_queue
        self.server = server.Server("0.0.0.0", 6666, 6665, self.server_queue, self.new_player_queue, self.goal_queue)
        self.server.start()

    def add_special_tile(self):
        for gen in self.content_gens:
            if gen.tiles_generated == 0:
                t = gen.gen_tile()
                t.pos = random.randrange(0, self.settings.width), random.randrange(0, self.settings.height)
                self.board[t.pos_y][t.pos_x] = t
                return

        gen = random.choice(self.content_gens)
        t = gen.gen_tile()
        t.pos = random.randrange(0, self.settings.width), random.randrange(0, self.settings.height)
        self.board[t.pos_y][t.pos_x] = t

    def draw_frame(self):
        self.display.fill(self.settings.background_color)
        # wall drawing

        for wall in self.wall_list:
            point1 = (wall.x1 * self.settings.tile_size, wall.y1 * self.settings.tile_size)
            point2 = (wall.x2 * self.settings.tile_size, wall.y2 * self.settings.tile_size)
            pygame.draw.line(self.display, self.settings.wall_color, point1, point2, 3)
        self.all_sprites.draw(self.display)
        pygame.display.flip()

    def handle_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False

    def update_logic(self):

        if not self.new_player_queue.empty():
            new_player: group.Player = self.new_player_queue.get()
            goal_str_list = []
            gen_list = random.sample(self.content_gens, 3)
            for gen in gen_list:
                goal = gen.gen_goal(new_player, self)
                goal_str_list.append(goal.description)
                new_player.goals.append(goal)
            self.goal_queue.put(goal_str_list)
            self.squad.player_list.append(new_player)
            while not self.goal_queue.empty():
                time.sleep(0.001)

        self.all_sprites.update()
        if self.frames_until_move == 0:

            self.turns += 1

            dest = (self.squad.pos_x + self.squad.direction.x, self.squad.pos_y + self.squad.direction.y)
            collision = bool(self.wall_graph.get(self.squad.pos)) and dest in self.wall_graph.get(self.squad.pos)
            if not collision:
                self.squad.pos_x += self.squad.direction.x
                self.squad.pos_y += self.squad.direction.y

                consumed = self.board[self.squad.pos_y][self.squad.pos_x].on_step(self.squad)
                if consumed:
                    self.board[self.squad.pos_y][self.squad.pos_x].kill()
                    self.board[self.squad.pos_y][self.squad.pos_x] = tiles.Tile(self.settings,
                                                                                self.squad.pos_x, self.squad.pos_y)
            self.frames_until_move = 60

        self.frames_until_move -= 1

    def loop(self):
        while self.running:
            self.handle_events()
            self.update_logic()
            self.draw_frame()
            self.clock.tick(60)

        pygame.quit()
