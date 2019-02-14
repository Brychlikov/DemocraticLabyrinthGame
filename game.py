import random
import numpy as np
import threading
import time
from loguru import logger
from typing import List

import pygame
from dataclasses import dataclass
from queue import Queue
from threading import Thread

import group
import minotaur
import labgen
import textDisplay
import tiles
import server
import contentGen
from imgutils import make_background

AMBIENT_CHANNEL = 0
TRAP_CHANNEL = 1
TREASURE_CHANNEL = 2
MINOTAUR_CHANNEL = 3



def wall_graph(wall_list):
    """returns a graph where keys are  coordinates and values are coordinates of FORBIDDEN movements"""
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
    """Class containing global settings for the game"""
    tile_size: int
    width: int
    height: int
    background_color: pygame.Color = pygame.Color(0, 0, 0)
    vision_radius: int = 150
    move_time: float = 1  # Time in seconds between ticks (moves)
    mute: bool = False

    @property
    def resolution(self):
        return self.width * self.tile_size, self.height * self.tile_size


class DelayedCall(Thread):
    def __init__(self, t, func, args=None, kwargs=None):
        """
        :param t: delay time in seconds
        :param func: function to call
        :param args: args to function
        :param kwargs: kwargs to function
        """
        super(DelayedCall, self).__init__()
        self.should_stop = False
        self.t = t
        self.func = func
        self.f_args = args if args is not None else []
        self.f_kwargs = kwargs if kwargs is not None else {}

        self._exit_early = False

    def run(self):
        start_time = time.time()
        while time.time() - start_time < self.t:
            if self._exit_early:
                logger.debug("Delayed call canceled early")
                break
            time.sleep(0.001)
        if not self._exit_early:
            self.func(*self.f_args, **self.f_kwargs)

    def cancel(self):
        """Send exit signal to thread"""
        logger.debug("Delayed call got cancellation signal")
        self._exit_early = True

class Game:
    """Main game object"""
    def __init__(self, settings: Settings):

        ### PYGAME INITS
        pygame.init()
        pygame.font.init()
        pygame.mixer.init()
        ###

        self.settings = settings

        self.main_surf = pygame.Surface(self.settings.resolution)
        self.background = make_background(pygame.image.load("assets/tile.png"), self.settings.resolution)
        self.display = pygame.display.set_mode((self.settings.resolution[0] + 300, self.settings.resolution[1]))
        self.display.set_colorkey(self.settings.background_color)

        self.board = []

        self.orphans = []  # Tile objects which for some reason are not in self.board

        # fill board with empty tiles
        for i in range(settings.width):
            row = []
            for j in range(settings.height):
                row.append(tiles.Tile(settings, i, j))
            self.board.append(row)

        self.ticks = 0.0  # game clock. Increments by 1 every turn. Player moves on 1, 2, 3.. etc. Minotaur on 1.5, 2.5, 3.5.. etc.
        # This should be OK in terms of floating point math

        self.last_tick_time = time.time()
        self.labyrinth_finished = False

        self.last_player_move = 0
        self.last_minotaur_move = -0.5

        self.running = False


        self.running = True

        ### SERVER INITS
        self.server_queue = Queue() # main queue to receive movements
        self.new_player_queue = Queue()  # queue to receive new player objects
        self.goal_queue = Queue()  # queue to send new goals
        self.info_queue = Queue()  # queue to send gametime info
        self.server = server.Server("0.0.0.0", 6666, 6665, self.server_queue, self.new_player_queue, self.goal_queue, self.info_queue)
        self.server.start()
        ###

        unscaled = pygame.image.load("assets/wall_horizontal.png").convert_alpha()
        self.wall_horizontal = pygame.transform.scale(unscaled, (self.settings.tile_size * 7 // 6, self.settings.tile_size))
        unscaled = pygame.image.load("assets/wall_vertical.png").convert_alpha()
        self.wall_vertical = pygame.transform.scale(unscaled, (self.settings.tile_size // 6, self.settings.tile_size))

        # prepare sound
        self.sound_bank = {}
        self.make_sound_bank()
        c = pygame.mixer.Channel(AMBIENT_CHANNEL)
        if not self.settings.mute:
            c.play(self.sound_bank["ambient"], loops=-1)
        self.unmute_thread: DelayedCall = None
        #



        self.clock = pygame.time.Clock()

        self.text_display = textDisplay.TextDisplay((300, 300), "dejavu", 24)
        self.text_display.print("Test")

        self.squad = group.Squad(settings, self)
        self.minotaur = minotaur.Minotaur(settings, self)
        self.minotaur.pos = (15, 15)

        self.all_sprites = pygame.sprite.Group()
        self.all_sprites.add(self.squad)
        self.all_sprites.add(self.minotaur)

        self.trap_gen = contentGen.TrapContentGen(settings, self)
        self.content_gens: List[contentGen.ContentGen] = [contentGen.TreasureContentGen(settings,  self) for i in range(3)]
        self.content_gens.append(self.trap_gen)
        self.content_gens.append(contentGen.OutOfLabirynthContentGen(settings, self))
        self.content_gens.append(contentGen.WeaponContentGen(settings, self))
        self.content_gens.append(contentGen.MinotaurContectGen(settings, self))

        for i in range(15):
            self.add_special_tile()

        self.wall_list, entrance_wall, exit_wall = labgen.actually_gen_lab(settings.height)
        self.squad.pos = entrance_wall.x1, entrance_wall.y1

        exit_tile = tiles.LabExit(self.settings, exit_wall.x1 - 1, exit_wall.y1)
        self.board[exit_wall.y1][exit_wall.x1 - 1] = exit_tile

        self.wall_graph = wall_graph(self.wall_list)  # Graph representing nodes blocked by walls
        self.nrwg = minotaur.non_retarded_wall_graph(self.wall_graph, settings)  # Graph representing nodes accessible

    @property
    def turns(self):
        """To keep compatibility after changing tick model"""
        return int(self.ticks)

    def make_sound_bank(self):
        self.sound_bank["minotaur_chase"] = pygame.mixer.Sound("sounds/minotaur_chase.ogg")
        self.sound_bank["trap"] = pygame.mixer.Sound("sounds/pulapka.ogg")
        self.sound_bank["treasure"] = pygame.mixer.Sound("sounds/skarb.ogg")
        self.sound_bank["ambient"] = pygame.mixer.Sound("sounds/main_theme.ogg")

    def play_sound(self, name, chan_id):
        """
        Plays given sound. Handles silencing ambient and bringing it back to normal
        :param name: key if self.sound_bank of sound to play
        :param chan_id: channel id
        :return:
        """
        if self.settings.mute:
            return
        if self.unmute_thread is not None and self.unmute_thread.isAlive():
            self.unmute_thread.cancel()

        ambient_chan = pygame.mixer.Channel(AMBIENT_CHANNEL)
        c = pygame.mixer.Channel(chan_id)

        ambient_chan.set_volume(0.15)
        sound = self.sound_bank[name]
        c.play(sound)

        self.unmute_thread = DelayedCall(sound.get_length(), ambient_chan.set_volume, args=(1,))
        self.unmute_thread.start()

    def add_special_tile(self):
        """Generate treasure/trap from randomly selected ContentGen"""
        gen_list = [g for g in self.content_gens if g.generates_tiles]
        for gen in gen_list:
            if gen.tiles_generated == 0:
                t = gen.gen_tile()
                t.pos = random.randrange(0, self.settings.width), random.randrange(0, self.settings.height)
                self.board[t.pos_y][t.pos_x] = t
                return

        gen = random.choice(gen_list)
        t = gen.gen_tile()
        self.all_sprites.add(t)
        t.pos = random.randrange(0, self.settings.width), random.randrange(0, self.settings.height)
        self.board[t.pos_y][t.pos_x] = t

    def make_vision_mask(self):
        """Generate 2d array of booleans, where true = player has vision of given pixel"""
        result = pygame.Surface(self.settings.resolution)
        result.fill((0, 0, 0))
        position = int((self.squad.pos_x + 0.5) * self.settings.tile_size), int((self.squad.pos_y + 0.5) * self.settings.tile_size)
        pygame.draw.circle(result, (255, 255, 255), position, self.squad.vision_radius)
        to_return = pygame.surfarray.array2d(result).astype(np.bool)
        return to_return

    def draw_frame(self):
        # clean after previous frame
        self.main_surf.blit(self.background, (0, 0))

        # wall drawing
        # Iterates over wall list twice. Firs over horizontal, then over vertical in order to
        # make vertical overlap horizontal ones
        for wall in self.wall_list:
            point1 = (wall.x1 * self.settings.tile_size-2, wall.y1 * self.settings.tile_size - 2)
            if wall.y1 == wall.y2:
                self.main_surf.blit(self.wall_horizontal, point1)
        for wall in self.wall_list:
            point1 = (wall.x1 * self.settings.tile_size-2, wall.y1 * self.settings.tile_size - 2)
            if wall.x1 == wall.x2:
                self.main_surf.blit(self.wall_vertical, point1)

        self.all_sprites.draw(self.main_surf)
        # draw arrows indicating individual player decisions
        self.squad.make_decision_arrows(self.main_surf)

        mask = self.make_vision_mask() == False  # Invert mask → True = player has NO vision
        array_view = pygame.surfarray.pixels3d(self.main_surf)
        # black out pixels with no vision
        array_view[mask] = np.array(self.settings.background_color)[:3]
        del array_view  # delete array view of main surface to allow it to be drawn

        self.display.blit(self.main_surf, (0, 0))
        self.display.blit(self.text_display.draw_queue(), (self.settings.resolution[0], 0))

        pygame.display.flip()

    def handle_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False

    def update_ticks(self):
        if time.time() - self.last_tick_time > self.settings.move_time:
            self.last_tick_time = time.time()
            self.ticks += 0.5

    def check_board_integrity(self, log=False):
        """
        Check for orphans in board
        :param log: If true, will log every integrity loss
        """
        lost = False
        del self.orphans
        self.orphans = []
        for s in self.all_sprites:
            if isinstance(s, tiles.Tile) and self.board[s.pos_y][s.pos_x] is not s:
                if log:
                    logger.warning(f"Board lost integrity on coords {s.pos} on tick {self.ticks}")
                lost = True
                self.orphans.append(s)
        return lost

    def kill_the_orphans(self):
        """...And kill them"""
        for s in self.orphans:
            s.kill()

    def update_logic(self):

        # Handle adding new player
        if not self.new_player_queue.empty():
            new_player: group.Player = self.new_player_queue.get()
            goal_str_list = []
            gen_list = random.sample([cg for cg in self.content_gens if cg.generates_goals], 3)
            # For every chosen ContentGen, add new goal to new player
            for gen in gen_list:
                goal = gen.gen_goal(new_player)
                goal_str_list.append(goal.description)
                new_player.goals.append(goal)
                new_player.squad = self.squad
            self.goal_queue.put(goal_str_list)
            # Handle trap knowledge
            known_traps = random.sample(self.trap_gen.traps_generated, self.trap_gen.tiles_generated // 10)
            for t in known_traps:
                t.add_aware_player(new_player)
            self.squad.player_list.append(new_player)

        self.all_sprites.update()

        # Update gametime info
        self.info_queue.put([p.to_dict() for p in self.squad.player_list])

        if self.squad.dead or self.labyrinth_finished:
            self.running = False

    def make_leader_board(self):
        result = []
        for p in self.squad.player_list:
            result.append((p, sum((g.progress / g.aim + int(g.achieved) for g in p.goals))))
        result.sort(key=lambda i: i[1] * -1)
        return result

    def loop(self):
        while self.running:
            self.handle_events()
            self.update_ticks()
            self.update_logic()
            self.draw_frame()
            self.check_board_integrity()
            self.kill_the_orphans()
            self.check_board_integrity(log=True)
            self.clock.tick(60)

        self.server.halt = True
        self.text_display.flush()
        for i, record in enumerate(self.make_leader_board()):
            print(f"{i + 1}. miejsce zajmuje {record[0].name} z wynikiem {record[1]} pkt.")
            self.text_display.print(f"{i + 1}. miejsce zajmuje {record[0].name} z wynikiem {record[1]:.3f} pkt.")

        self.draw_frame()
        pygame.display.flip()

        done = False
        while not done:
            for e in pygame.event.get():
                if e.type == pygame.QUIT:
                    done = True
            self.clock.tick(60)

        pygame.quit()
