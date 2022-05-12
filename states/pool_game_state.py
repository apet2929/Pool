from math import dist, sqrt
import math
from assets import AssetCache
from entitites.entity import Entity
from states.state import State
from pygame import Rect, Surface, Vector2
import pygame
from ui import Text

from utils import BASE_SIZE, check_sides, circle_intersection, is_circle_inside_circle, normalize_angle_rads

class Ball(Entity):
    FRICTION = 0.02
    RADIUS = 10
    HOLE_RADIUS = 20
    TABLE_SIZE = [BASE_SIZE[0], BASE_SIZE[0]/2]
    def __init__(self, color, position, mass=1) -> None:
        super().__init__(draw_ball(color), (Ball.RADIUS * 2, Ball.RADIUS * 2), position)
        self.mass: float = mass
        self.velocity: Vector2 = Vector2(0,0)
        self.forces: list[Vector2] = []

    def update(self, delta, **kwargs):
        self.apply_friction()
        acceleration: Vector2 = self.sum_forces() / self.mass
        self.forces.clear()
        self.velocity += acceleration
        self.position += self.velocity * delta

        self.collide_walls(delta, kwargs["walls"])
        self.collide_balls(delta, kwargs["balls"])
        super().update(delta, **kwargs)

    def get_momentum(self):
        return self.mass * self.velocity

    def is_moving(self):
        return self.velocity.magnitude_squared() > 0.05

    def apply_force(self, force: Vector2):
        self.forces.append(force)

    def sum_forces(self) -> Vector2:
        s = Vector2(0,0)
        for force in self.forces:
            s += force
        return s

    def sweep_circle(self, delta, ball):
        current_time = delta
        intersected = True
        while current_time > -(delta * 3) and intersected:
            self_cur_pos = self.get_pos_after_time(current_time)
            other_cur_pos = ball.get_pos_after_time(current_time)
            if circle_intersection(self_cur_pos, other_cur_pos, Ball.RADIUS):
                # Continue
                current_time -= delta * 0.2
            else:
                intersected = False
                return current_time
        print("Sweep failed! No time found where intersection absent")    

    def get_pos_after_time(self, delta) -> Vector2:
        return self.position + (self.velocity * delta)

    def check_sunk(self, holes: list[tuple]) -> bool:
        for hole in holes:
            if is_circle_inside_circle((self.position.x, self.position.y), Ball.RADIUS, hole, Ball.HOLE_RADIUS):
                return True
        return False

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

    def collide_balls(self, delta, balls):
            # Sweep through time to find the initial intersection point
            future = self.get_pos_after_time(delta)
            for ball in balls:
                if ball == self:
                    continue
                if self.check_collided(ball, future, delta):
                    intersected_time = self.get_intersection_time(ball, delta)
                    if(intersected_time is None):
                        intersected_time = 5 * delta # TODO : Find a way to kick balls out that are slowly intersecting
                    self.position = self.get_pos_after_time(intersected_time)
                    ball.position = ball.get_pos_after_time(intersected_time)
                    self.collide_ball(ball)

    def check_collided(self, ball, future_pos, delta) -> bool:
        future_rect = self.get_rect()
        future_rect.center = [future_pos.x, future_pos.y]
        ball_future = ball.get_pos_after_time(delta)
        ball_rect = ball.get_rect()
        ball_rect.center = [ball_future.x, ball_future.y]
        if future_rect.colliderect(ball_rect): # Fast rectangle collision test
            return circle_intersection(future_pos, ball.get_pos_after_time(delta), Ball.RADIUS)
        return False

    def get_intersection_time(self, ball, delta) -> float or None:
        return self.sweep_circle(delta, ball) # Potentially really expensive, we'll see!

    def collide_ball(self, other):
        difference: Vector2 = self.position - other.position
        unit_normal = difference.normalize()
        unit_tangent = Vector2(-unit_normal.y, unit_normal.x)

        # Tangent and normal components of initial velocity (scalar)
        self_vel_tangent = unit_tangent.dot(self.velocity)
        self_vel_normal = unit_normal.dot(self.velocity)
        other_vel_tangent = unit_tangent.dot(other.velocity)
        other_vel_normal = unit_normal.dot(other.velocity)
        
        self_vel_normal_final = ((self_vel_normal)*(self.mass - other.mass) + (2*other.mass*other_vel_normal)) / (self.mass + other.mass)
        other_vel_normal_final = ((other_vel_normal)*(other.mass - self.mass) + (2*self.mass*self_vel_normal)) / (self.mass + other.mass)

        # Self/other velocity normal/tangent as vectors
        svn_vector = self_vel_normal_final * unit_normal
        svt_vector = self_vel_tangent * unit_tangent
        ovn_vector = other_vel_normal_final * unit_normal
        ovt_vector = other_vel_tangent * unit_tangent

        self.velocity = svn_vector + svt_vector
        other.velocity = ovn_vector + ovt_vector

    def fix_intersection(self, ball):
        return
        difference: Vector2 = self.position - ball.position
        optimal_difference = difference.normalize() * Ball.RADIUS * 2
        # Push both balls out
        self.position += (optimal_difference / 2)
        ball.position += (optimal_difference / 2)

    def setPosition(self, pos: Vector2):
        self.position = pos
        super().update(0)

    def apply_friction(self):
        self.apply_force(self.velocity * -Ball.FRICTION)

    def get_rect(self):
        r = Rect(0,0,Ball.RADIUS * 2, Ball.RADIUS * 2)
        r.centerx = self.position.x
        r.centery = self.position.y
        return r

def draw_ball(color) -> Surface:
    surf = pygame.Surface((Ball.RADIUS * 2, Ball.RADIUS * 2))
    pygame.draw.circle(surf, color, surf.get_rect().center, Ball.RADIUS)
    surf.set_colorkey(surf.get_at((0,0)))
    return surf

class PoolGameState(State):
    POWER_MIN = 1
    POWER_MAX = 100
    def __init__(self, font) -> None:
        super().__init__()
        self.font = font
        self.balls: list[Ball] = []
        self.aim: Vector2 = Vector2(100, 0)
        self.power: float = 1
        self.mousePos_i = None
        self.walls: list[Rect] = []
        self.holes: list[tuple] = []

        self.table = Rect(10, (BASE_SIZE[1] - Ball.TABLE_SIZE[1]) / 2, Ball.TABLE_SIZE[0], Ball.TABLE_SIZE[1])
        self.table_color = (42, 102, 55)
        self.bg_color = (80, 101, 148)
        self.wall_color = (79, 51, 16)
        self.states = {
            "INACTIVE": 0,
            "AIMING": 1,
            "POWER": 2,
            "SCRATCH": 3,
            "WIN": 4
        }
        self.state = self.states["AIMING"]

    def on_enter(self, ass_cache: AssetCache):
        self.init_balls(ass_cache)
        self.init_walls()
        self.init_holes()
        self.texts = [
            Text("Waiting...", BASE_SIZE, (50, 5), self.font, (self.wall_color)),
            Text("You scratched! Place the ball with LEFT CLICK", BASE_SIZE, (50, 5), self.font, (self.wall_color)),
            Text("You win!", BASE_SIZE, (50, 5), self.font, (self.wall_color))
        ]

    def render(self, screen: pygame.Surface):
        self.draw_background(screen)

        self.draw_holes(screen)
        for ball in self.balls:
            ball.render(screen)

        self.draw_walls(screen)            
        self.drawAim(screen)
        self.draw_ui(screen)
        super().render(screen)
    
    def drawAim(self, screen):
        if self.aim is not None:
            pointA = self.getCueBall().position - (self.aim * (Ball.RADIUS * 2 + self.power))
            pointB = self.getCueBall().position - (self.aim * (Ball.RADIUS * 12 + self.power))
            pygame.draw.line(screen, (255,0,0), pointA, pointB)

    def update(self, delta, events):
        keys = pygame.key.get_pressed()
        if self.state == self.states["AIMING"]:
            self.updateAim(events)
        elif self.state == self.states["POWER"]:
            self.updatePower(events)
        elif self.state == self.states["SCRATCH"]:
            self.updateScratch(events)
        elif self.state == self.states["INACTIVE"]:
            self.updateInactive(delta)

    def shoot(self):
        self.getCueBall().apply_force(self.aim * self.power * self.getCueBall().mass * 10)
        self.aim = None
        self.power = 1
        self.state = self.states["INACTIVE"]

    def updateAim(self, events: list[pygame.event.Event]):
        for event in events:
            if event.type == pygame.MOUSEMOTION:
                print("Aiming")
                mousePos = pygame.mouse.get_pos()
                self.aim = Vector2(mousePos[0] - self.getCueBall().position.x, mousePos[1] - self.getCueBall().position.y).normalize()
            if event.type == pygame.MOUSEBUTTONDOWN:
                self.state = self.states["POWER"]
                self.mousePos_i = pygame.mouse.get_pos()
                
    def updatePower(self, events: list[pygame.event.Event]):
        for event in events:
            if event.type == pygame.MOUSEBUTTONUP:
                print(f"power = {self.power}")
                self.shoot()
            elif event.type == pygame.MOUSEMOTION:
                mousePos = pygame.mouse.get_pos()
                difference = Vector2(mousePos[0] - self.mousePos_i[0], mousePos[1] - self.mousePos_i[1])
                mag = -difference.magnitude()
                if mag == 0:
                    intendedPower = 0
                else:
                    difference.normalize_ip()
                    intendedPower = difference.dot(self.aim) * mag
                self.power = min(max(intendedPower, PoolGameState.POWER_MIN), PoolGameState.POWER_MAX)
    
    def updateScratch(self, events: list[pygame.event.Event]):
        for event in events:
            if event.type == pygame.MOUSEMOTION:
                mPos = pygame.mouse.get_pos()
                self.getCueBall().setPosition(Vector2(mPos[0], mPos[1]))
            elif event.type == pygame.MOUSEBUTTONDOWN:
                mPos = pygame.mouse.get_pos()
                self.getCueBall().setPosition(Vector2(mPos[0], mPos[1]))
                self.state = self.states["AIMING"]

    def updateInactive(self, delta):
        self.updateBalls(delta)

        doneWaiting = True
        for ball in self.balls:
            if ball.is_moving():
                doneWaiting = False
        if doneWaiting:
            self.state = self.states["AIMING"]
            print("Done waiting")
        
    def updateBalls(self, delta):
        for ball in self.balls:
            ball.update(delta, walls=self.walls, balls=self.balls)
            if ball.check_sunk(self.holes):
                if ball == self.getCueBall():
                    self.state = self.states["SCRATCH"]
                    ball.setPosition(Vector2(-50, -50))
                else:
                    self.balls.remove(ball)

    def getCueBall(self) -> Ball:
        return self.balls[0]

    def init_walls(self):
        width = 10
        tw = Ball.TABLE_SIZE[0]
        th = Ball.TABLE_SIZE[1]
        margin_top = (BASE_SIZE[1] - th) / 2
        self.walls.append(Rect(0,margin_top,tw, width)) # top
        self.walls.append(Rect(0,th - width + margin_top,tw, width)) # bottom
        self.walls.append(Rect(0,margin_top,width, th)) # left
        self.walls.append(Rect(tw-width,margin_top,width, th)) # right

    def init_balls(self, ass_cache):
        w = BASE_SIZE[0]
        h = BASE_SIZE[1]
        r = Ball.RADIUS
        d = Ball.RADIUS * 2
        # self.balls.append(Ball(ass_cache.get_asset("CropSprite"), (400,200), 1))
        balls = [
            Ball((242, 230, 216), (w/4,h/2), 1.005), #cue ball

            Ball((242, 224, 82), (3*w/4,h/2)),

            Ball((112, 156, 255), (3*w/4 + d,h/2 + r)),
            Ball((217, 41, 214), (3*w/4 + d,h/2 - r)),

            Ball((72, 4, 110), (3*w/4 + 2*d, h/2)),
            Ball((242, 235, 99), (3*w/4 + 2*d, h/2 - d)),
            Ball((232, 162, 32), (3*w/4 + 2*d, h/2 + d)),

            Ball((68, 161, 42), (3*w/4 + 3*d, h/2 + r)),
            Ball((176, 36, 32), (3*w/4 + 3*d, h/2 - r)),

            Ball((38, 8, 7), (3*w/4 + 4*d, h/2)),
        ]
        self.balls.extend(balls)
    
    def init_holes(self):
        r = Ball.HOLE_RADIUS
        margin = 5
        rm = r + margin
        w = Ball.TABLE_SIZE[0]
        h = Ball.TABLE_SIZE[1]
        tm = (BASE_SIZE[1] - h)/2
        self.holes = [
            (rm, rm + tm), (w - rm, rm + tm), (w - rm, h - rm + tm), (rm, h - rm + tm),
            (w/2, rm + tm), (w/2, h - rm + tm)
        ]

    def draw_walls(self, screen):
        for wall in self.walls:
            pygame.draw.rect(screen, self.wall_color, wall)

    def draw_holes(self, screen):
        for hole in self.holes:
            pygame.draw.circle(screen, (0,0,0), hole, Ball.HOLE_RADIUS)

    def draw_background(self, screen: Surface):
        screen.fill(self.bg_color)
        screen.fill(self.table_color, self.table)

    def draw_ui(self, screen):
        if self.state == self.states["INACTIVE"]:
            self.texts[0].draw(screen)
        elif self.state == self.states["SCRATCH"]:
            self.texts[1].draw(screen)
        elif self.state == self.states["WIN"]:
            self.texts[2].draw(screen)

    def run_test(self, launch_angle):
        a = math.radians(launch_angle)
        self.balls[0].position = Vector2(300,200)
        self.balls[1].position = Vector2(300,400)

        self.balls[0].velocity = Vector2(0,0)
        self.balls[1].velocity = Vector2(0,0)

        self.balls[0].apply_force(Vector2(1000 * math.sin(a), 1000 * math.cos(a)))
        
