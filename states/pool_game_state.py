from math import dist, sqrt
import math
from assets import AssetCache
from entitites.entity import Entity
from states.state import State
from pygame import Rect, Vector2
import pygame

from utils import BASE_SIZE, check_sides, circle_intersection

class Ball(Entity):
    FRICTION = 0.02
    RADIUS = 20
    def __init__(self, image: pygame.Surface, position, mass) -> None:
        super().__init__(image, (Ball.RADIUS * 2, Ball.RADIUS * 2), position)
        self.mass: float = mass
        self.velocity: Vector2 = Vector2(0,0)
        self.forces: list[Vector2] = []
        
    def render(self, screen):
        # super().render(screen)
        pygame.draw.circle(screen, (255,0,0), self.rect.center, Ball.RADIUS)

    def update(self, delta, **kwargs):
        self.apply_friction()
        acceleration: Vector2 = self.sum_forces() / self.mass
        self.forces.clear()
        self.velocity += acceleration
        self.position += self.velocity * delta

        self.collide_walls(delta, kwargs["walls"])
        self.collide_balls(delta, kwargs["balls"])

        if self.velocity.magnitude_squared() < 0.001:
            self.velocity.x = 0
            self.velocity.y = 0
        super().update(delta, **kwargs)

    def apply_force(self, force: Vector2):
        self.forces.append(force)

    def sum_forces(self) -> Vector2:
        s = Vector2(0,0)
        for force in self.forces:
            s += force
        return s

    def collide_balls(self, delta, balls):
        # Sweep through time to find the initial intersection point
        future = self.get_pos_at_time(delta)
        future_rect = self.get_rect()
        future_rect.center = [future.x, future.y]
        for ball in balls:
            if ball == self:
                continue
            ball_future = ball.get_pos_at_time(delta)
            ball_rect = ball.get_rect()
            ball_rect.center = [ball_future.x, ball_future.y]
            if future_rect.colliderect(ball_rect): # Fast rectangle collision test
                # Perform a better test
                if circle_intersection(future, ball.get_pos_at_time(delta), Ball.RADIUS) and ball.velocity.magnitude() == 0:
                    # Sweep back in time

                    intersected_time = self.sweep_circle(delta, ball) # Potentially really expensive, we'll see!
                    if(intersected_time is not None):
                        my_int_pos = self.get_pos_at_time(intersected_time)
                        ball_int_pos = ball.get_pos_at_time(intersected_time)
                        difference = my_int_pos - ball_int_pos
                        tangent_slope = math.degrees(math.atan2(difference.y,difference.x)) + 90

                        print("Balls collided!")
                        print(my_int_pos, ball_int_pos, tangent_slope)
                        self.apply_collision_force(ball, tangent_slope)
                        pygame.event.post(pygame.event.Event(pygame.USEREVENT + 1))

    def sweep_circle(self, delta, ball):
        current_time = delta
        intersected = True
        while current_time > -(delta * 2) and intersected:
            self_cur_pos = self.get_pos_at_time(current_time)
            other_cur_pos = ball.get_pos_at_time(current_time)
            if circle_intersection(self_cur_pos, other_cur_pos, Ball.RADIUS):
                # Continue
                current_time -= delta * 0.2
            else:
                intersected = False
                return current_time
        print("Sweep failed! No time found where intersection absent")    

    def get_pos_at_time(self, delta):
        return self.position + (self.velocity * delta)

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

    def apply_collision_force(self, other, collision_normal):
        a = (self.velocity.angle_to(Vector2(1,0))) - collision_normal
        
        momentum_transfered_percent = math.sin(math.radians(a))
        initial_velocity_magnitude = self.velocity.magnitude()
        my_final_velocity_mag = initial_velocity_magnitude * (1 - momentum_transfered_percent)
        other_final_velocity_mag = initial_velocity_magnitude * momentum_transfered_percent
        my_result_angle = math.radians(collision_normal)
        other_result_angle = math.radians(collision_normal - 90)
        my_new_momentum = Vector2(my_final_velocity_mag * math.cos(my_result_angle), my_final_velocity_mag * math.sin(my_result_angle))
        other_new_momentum = Vector2(other_final_velocity_mag * math.cos(other_result_angle), other_final_velocity_mag * math.sin(other_result_angle))

        my_change_momentum = my_new_momentum - self.velocity
        other_change_momentum = other.velocity - other_new_momentum 
        self.apply_force(my_change_momentum)
        other.apply_force(other_change_momentum)
        print(my_final_velocity_mag, other_final_velocity_mag, my_change_momentum, other_change_momentum)
        print(a, momentum_transfered_percent, math.degrees(my_result_angle), math.degrees(other_result_angle))

    def apply_friction(self):
        self.apply_force(self.velocity * -Ball.FRICTION)

    def get_rect(self):
        r = Rect(0,0,Ball.RADIUS * 2, Ball.RADIUS * 2)
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
        self.balls.append(Ball(ass_cache.get_asset("CropSprite"), (200,200), 1))
        self.balls.append(Ball(ass_cache.get_asset("CropSprite"), (400,200), 1))
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
            ball.update(delta, walls=self.walls, balls=self.balls)
    
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
