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

    mute = False
    try:
        mute = sys.argv[2]
    except IndexError:
        pass
    settings = Settings(40, 20, 20, move_time=0.5, vision_radius=400, mute=mute)
    game = Game(settings)
    game.init()
    try:
        game.loop()
    except KeyboardInterrupt:
        game.server.halt = True
        game.unmute_thread.cancel()
