from math import sqrt
from assets import AssetCache
from entitites.entity import Entity
from states.state import State
from pygame import Rect, Vector2
import pygame

from utils import BASE_SIZE, check_sides

class Ball(Entity):
    FRICTION = 0.02
    def __init__(self, image: pygame.Surface, position, radius, mass) -> None:
        super().__init__(image, (radius * 2, radius * 2), position)
        self.mass: float = mass
        self.velocity: Vector2 = Vector2(0,0)
        self.radius: float = radius
        self.forces: list[Vector2] = []

    def update(self, delta, **kwargs):
        self.apply_friction()
        acceleration: Vector2 = self.sum_forces() / self.mass
        self.forces.clear()
        self.velocity += acceleration
        self.position += self.velocity * delta

        self.collide_walls(delta, kwargs["walls"])
        super().update(delta, **kwargs)

    def apply_force(self, force: Vector2):
        self.forces.append(force)

    def sum_forces(self) -> Vector2:
        s = Vector2(0,0)
        for force in self.forces:
            s += force
        return s

    def collide_walls(self, delta, walls: list[Rect]):
        # Check for collision next frame
        my_rect: Rect = self.get_rect()
        my_rect.x += self.velocity.x * delta
        my_rect.y += self.velocity.y * delta
    
        collided = False
        for i in range(len(walls)):
            wall = walls[i]
            if my_rect.colliderect(wall):
                collided = True
                if i == 0: # top
                    my_rect.top = wall.bottom
                    self.velocity.y *= -1
                elif i == 1: # bottom
                    my_rect.bottom = wall.top
                    self.velocity.y *= -1
                elif i == 2: # left
                    my_rect.left = wall.right
                    self.velocity.x *= -1
                elif i == 3: # right
                    my_rect.right = wall.left
                    self.velocity.x *= -1
        if collided:
            self.position.x = my_rect.centerx
            self.position.y = my_rect.centery
            
    def apply_friction(self):
        self.apply_force(self.velocity * -Ball.FRICTION)

    def get_rect(self):
        r = Rect(0,0,self.radius * 2, self.radius * 2)
        r.centerx = self.position.x
        r.centery = self.position.y
        return r

class PoolGameState(State):
    def __init__(self) -> None:
        super().__init__()
        self.balls: list[Ball] = []
        self.aim: Vector2 = None
        self.walls: list[Rect] = []

    def on_enter(self, ass_cache: AssetCache):
        self.balls.append(Ball(ass_cache.get_asset("CropSprite"), (200,200), 20, 1))
        # self.balls[0].apply_force(Vector2(10, 10))
        self.init_walls()

    def render(self, screen):
        screen.fill((0,0,0))
        for ball in self.balls:
            ball.render(screen)

        self.draw_walls(screen)            
        self.draw_line(screen)
        super().render(screen)
    
    def draw_line(self, screen):
        if self.aim is not None:
            pygame.draw.line(screen, (255,0,0), self.getCueBall().position, self.aim)

    def update(self, delta, events):
        keys = pygame.key.get_pressed()
        for event in events:
            if event.type == pygame.MOUSEBUTTONDOWN:
                pos = pygame.mouse.get_pos()
                self.aim = Vector2(pos[0], pos[1])
            if event.type == pygame.MOUSEMOTION:
                if pygame.mouse.get_pressed()[0]:
                    pos = pygame.mouse.get_pos()
                    self.aim = Vector2(pos[0], pos[1])
            
            if event.type == pygame.MOUSEBUTTONUP:
                difference =  self.aim - self.getCueBall().position
                difference *= 2
                self.getCueBall().apply_force(difference)
                self.aim = None
        
        for ball in self.balls:
            ball.update(delta, walls=self.walls)
    
    def getCueBall(self) -> Ball:
        return self.balls[0]

    def init_walls(self):
        width = 10
        self.walls.append(Rect(0,0,BASE_SIZE[0], width)) # top
        self.walls.append(Rect(0,BASE_SIZE[1] - width,BASE_SIZE[0], width)) # bottom
        self.walls.append(Rect(0,0,width, BASE_SIZE[1])) # left
        self.walls.append(Rect(BASE_SIZE[0]-width,0,width, BASE_SIZE[1])) # right

    def draw_walls(self, screen):
        for wall in self.walls:
            pygame.draw.rect(screen, (0,255,0), wall)
