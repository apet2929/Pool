from pygame.rect import Rect
from pygame.sprite import Sprite
from pygame.math import Vector2
from pygame.surface import Surface
import pygame.transform

class Entity(Sprite):
    def __init__(self, image: Surface, size:tuple, pos:tuple=None) -> None:
        super().__init__()

        if pos == None:
            pos = (0,0)    
        self.position = Vector2(pos)
        self.rect = Rect(pos[0], pos[1], size[0], size[1])
        if image.get_width() == size[0] and image.get_height() == size[1]:
            self.image = image
        else:
            s = (int(size[0]), int(size[1]))
            im = pygame.transform.scale(image, s)
            self.image = im

    def render(self, screen: Surface):
        screen.blit(self.image, self.rect)

    def update(self, delta, **kwargs):
        self.rect.center = [self.position.x, self.position.y]
        
