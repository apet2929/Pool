import sys
import os.path
import math
from enum import Enum

import pygame
import pygame.event

class CustomEvents(Enum):
    LEVEL_OVER = pygame.USEREVENT + 1
    FALL_TIMER_UP = pygame.USEREVENT + 2

    def post(type, **kwargs):
        pygame.event.post(pygame.event.Event(type.value, kwargs))
    
    def get(type) -> int:
        return type.value


def resource_path(relative_path):
    try:
    # PyInstaller creates a temp folder and stores path in _MEIPASS
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")

    return os.path.join(base_path, relative_path)

def easeinoutsin(x: float):
    return -1 * (math.cos(math.pi * x) - 1) / 2

def rot_center(image, angle, x, y):
    
    rotated_image = pygame.transform.rotate(image, angle)
    new_rect = rotated_image.get_rect(center = image.get_rect(center = (x, y)).center)

    return rotated_image, new_rect

def check_sides(rect1: pygame.Rect, rect2: pygame.Rect) -> str:
    if rect1.midtop[1] > rect2.midtop[1]:
        return "top"
    elif rect1.midleft[0] > rect2.midleft[0]:
        return "left"
    elif rect1.midright[0] < rect2.midright[0]:
        return "right"
    else:
        return "bottom"
  
BASE_SIZE = (640, 480)
PI = 3.1415
TWOPI = PI * 2