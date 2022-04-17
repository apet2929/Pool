from enum import Enum
import pygame.key
from pygame import K_LEFT, K_RIGHT, K_UP, K_DOWN

class Direction(Enum):
    UP =  0
    DOWN = 1
    LEFT = 2
    RIGHT = 3

class Key:
    def __init__(self, direction) -> None:
        self.direction = direction
        self.pressed = False

class Controller:
    def __init__(self) -> None:
        self.keys = {
            Direction.UP, pygame.key.key_code(K_UP),
            Direction.DOWN, pygame.key.key_code(K_DOWN),
            Direction.LEFT, pygame.key.key_code(K_LEFT),
            Direction.RIGHT, pygame.key.key_code(K_RIGHT)
        }

        self.pressed = {
            Direction.UP, False,
            
        }

