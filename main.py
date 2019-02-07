import pygame
import sys
from loguru import logger

try:
    logger.add(sys.stdout, level=sys.argv[1])
    logger.remove(0)
except IndexError:
    logger.warning("No logging level provided. Falling back to ERROR")
    logger.remove(0)
    logger.add(sys.stdout, level="ERROR")

from game import Game, Settings

if __name__ == '__main__':

    settings = Settings(50, 20, 20, move_time=1, vision_radius=1500)
    game = Game(settings)
    game.init()
    try:
        game.loop()
    except KeyboardInterrupt:
        game.server.halt = True
