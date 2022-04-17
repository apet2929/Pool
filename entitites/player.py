from typing import Sequence
from entitites.entity import Entity
from pygame import Surface, Vector2
from pygame import K_LEFT, K_RIGHT, K_DOWN, K_UP

class Player(Entity):
    DAMP = 0.98
    ACCEL_SPEED = 2000
    def __init__(self, image: Surface, size: tuple, pos: tuple = None, mass=10, move_y=True) -> None:
        self.velocity = Vector2(0,0)
        self.force = Vector2(0,0)
        self.mass = mass
        self.move_y = move_y
        super().__init__(image, size, pos=pos)

    def update(self, delta, **kwargs):
        """
        Call this after do_movement (or after self.force != (0,0))
        """
        self.velocity += (self.force / self.mass) * delta
        self.velocity *= Player.DAMP
        self.position += self.velocity * delta
        super().update(delta)
        self.force.x = 0
        self.force.y = 0

    
    def do_movement(self, keys: Sequence[bool]):
        if keys[K_LEFT]:
            self.force.x -= Player.ACCEL_SPEED
        if keys[K_RIGHT]:
            self.force.x += Player.ACCEL_SPEED
        if self.move_y:
            if keys[K_UP]:
                self.force.y -= Player.ACCEL_SPEED
            if keys[K_DOWN]:
                self.force.y += Player.ACCEL_SPEED 
        
    