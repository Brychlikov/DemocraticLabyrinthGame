import pygame
from dataclasses import dataclass
from queue import Queue

import group
import labgen
import tiles
import server


@dataclass
class Settings:
    tile_size: int
    width: int
    height: int
    background_color: pygame.Color = pygame.Color(0, 0, 0, 0)


class Board:
    def __init__(self, settings):
        self.board = []

        for i in range(settings.width):
            for j in range(settings.height):
                self.board.append(tiles.Tile(settings, i, j))

    def get_surface(self):
        pass


class Game:
    def __init__(self, settings: Settings):
        self.settings = settings
        self.board = Board(settings)
        self.turns = 0
        self.labyrinth_finished = False

        self.frames_until_move = 0

        self.running = False
        self.display: pygame.Surface = None
        self.clock = pygame.time.Clock()
        self.server = None
        self.server_queue = None
        self.new_player_queue = None

        self.squad = group.Squad(settings)

        self.all_sprites = pygame.sprite.Group()
        self.all_sprites.add(self.squad)

    def init(self):
        pygame.init()
        resolution = (self.settings.width * self.settings.tile_size, self.settings.height * self.settings.tile_size)
        self.display = pygame.display.set_mode(resolution)
        self.running = True

        self.server_queue = Queue()
        self.new_player_queue = Queue()
        self.squad.server_queue = self.server_queue
        self.server = server.Server("0.0.0.0", 6666, 6665, self.server_queue, self.new_player_queue)
        self.server.start()

    def draw_frame(self):
        self.display.fill(self.settings.background_color)
        self.all_sprites.draw(self.display)
        pygame.display.flip()

    def handle_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False

    def update_logic(self):

        if not self.new_player_queue.empty():
            new_player = self.new_player_queue.get()
            self.squad.player_list.append(new_player)

        self.all_sprites.update()
        if self.frames_until_move == 0:
            self.squad.pos_x += self.squad.direction.x
            self.squad.pos_y += self.squad.direction.y
            self.frames_until_move = 120

        self.frames_until_move -= 1

    def loop(self):
        while self.running:
            self.handle_events()
            self.update_logic()
            self.draw_frame()
            self.clock.tick(60)

        pygame.quit()
