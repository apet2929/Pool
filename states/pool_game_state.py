from assets import AssetCache
from entitites.entity import Entity
from states.state import State
from pygame import Vector2
import pygame

class Ball(Entity):
    def __init__(self, image: pygame.Surface, position, radius, mass) -> None:
        super().__init__(image, (radius * 2, radius * 2), position)
        self.mass: float = mass
        self.velocity: Vector2 = Vector2(0,0)
        self.radius: float = radius
        self.forces: list[Vector2] = []

    def update(self, delta, **kwargs):
        acceleration: Vector2 = self.sum_forces() / self.mass
        self.forces.clear()
        self.velocity += acceleration
        self.velocity *= 0.98
        self.position += self.velocity * delta

        super().update(delta, **kwargs)

    def apply_force(self, force: Vector2):
        self.forces.append(force)

    def sum_forces(self) -> Vector2:
        s = Vector2(0,0)
        for force in self.forces:
            s += force
        return s

class PoolGameState(State):
    def __init__(self) -> None:
        super().__init__()
        self.balls: list[Ball] = []
        self.aim: Vector2 = None

    def on_enter(self, ass_cache: AssetCache):
        self.balls.append(Ball(ass_cache.get_asset("CropSprite"), (0,0), 10, 1))
        self.balls[0].apply_force(Vector2(10, 10))

    def render(self, screen):
        screen.fill((0,0,0))
        for ball in self.balls:
            ball.render(screen)
            
        self.draw_line(screen)
        super().render(screen)
    
    def draw_line(self, screen):
        if self.aim is not None:
            pygame.draw.line(screen, (255,0,0), self.getCueBall().position, self.aim)

    def update(self, delta, events):
        keys = pygame.key.get_pressed()
        for event in events:
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_p:
                    print("P Pressed")
                    self.getCueBall().apply_force(Vector2(100,0))
            if event.type == pygame.MOUSEMOTION:
                if pygame.mouse.get_pressed()[0]:
                    pos = pygame.mouse.get_pos()
                    self.aim = Vector2(pos[0], pos[1])
            
            if event.type == pygame.MOUSEBUTTONUP:
                difference =  self.aim - self.getCueBall().position
                self.getCueBall().apply_force(difference)
                self.aim = None
        
        for ball in self.balls:
            ball.update(delta)
    
    def getCueBall(self) -> Ball:
        return self.balls[0]
