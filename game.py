import pygame
from dataclasses import dataclass
from queue import Queue

import group
import goals
import labgen
import tiles
import server
import contentGen


@dataclass
class Settings:
    tile_size: int
    width: int
    height: int
    background_color: pygame.Color = pygame.Color(0, 0, 0, 0)




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

        self.squad = group.Squad(settings)

        self.all_sprites = pygame.sprite.Group()
        self.all_sprites.add(self.squad)

        self.content_gens = []
        self.content_gens.append(contentGen.TreasureContentGen(settings))
        tiles.Tile.groups = self.all_sprites
        for i in range(0, 30, 3):
            t = self.content_gens[0].gen_tile()
            t.pos_x = i
            t.pos_y = i
            self.board[i][i] = t

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
            new_player: group.Player = self.new_player_queue.get()
            new_player.goals.append(self.content_gens[0].gen_goal(new_player, self))
            self.squad.player_list.append(new_player)

        self.all_sprites.update()
        if self.frames_until_move == 0:

            self.turns += 1

            self.squad.pos_x += self.squad.direction.x
            self.squad.pos_y += self.squad.direction.y

            self.board[self.squad.pos_y][self.squad.pos_x].on_step(self.squad)
            self.frames_until_move = 120

        self.frames_until_move -= 1

    def loop(self):
        while self.running:
            self.handle_events()
            self.update_logic()
            self.draw_frame()
            self.clock.tick(60)

        pygame.quit()
