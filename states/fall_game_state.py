import random
from pygame.sprite import Group
from assets import AssetCache
from entitites.entity import Entity
from entitites.player import Player
from states.state import State

from pygame.color import Color
from pygame import Surface, Vector2
import pygame.transform
import pygame.sprite
import pygame
import pygame.key
import pygame.draw
import pygame.time
import pygame.event

from ui import Text, Font
from utils import BASE_SIZE, CustomEvents, rot_center

class FallingCrop(Entity):
    GRAVITY = 500
    def __init__(self, image: Surface, size: tuple, pos: tuple = None, initial_vel: tuple = None) -> None:
        self.size = size
        self.original_image = pygame.transform.scale(image.copy(), (int(size[0]), int(size[1])))
        self.original_image.set_colorkey((255,255,255))
        super().__init__(self.original_image, size, pos=pos)
        self.rot_speed = random.randint(-500, 500)
        self.rotation = 0.0     #   Rotation in degrees
        if initial_vel is None:
            self.velocity = Vector2(0,0)
        else:
            self.velocity = Vector2(initial_vel)

    def update(self, delta, **kwargs):
        # Rotate
        self.rotation += self.rot_speed * delta

        # Gravity
        self.velocity.y += FallingCrop.GRAVITY * delta
        self.position += self.velocity * delta
        if self.position.y > 10000:
            # Remove if far below screen
            self.kill()

        super().update(delta)
        self.rotate()

    def rotate(self):
        c = self.get_center()
        self.image, self.rect = rot_center(self.original_image, self.rotation, c[0], c[1])
        # self.rect = self.image.get_rect(center=(cX, cY))

    def get_center(self) -> tuple:
        return (self.position.x - self.size[0]/2, self.position.y + self.size[1]/2)

class Spawner:
    MAX_SPEED_X = 100
    MAX_SPEED_Y = 100
    
    def __init__(self, crop_sprite:Surface, screen_size: tuple, level: list[tuple], spawn_crop_function) -> None:
        self.spawn_list:list[tuple] = level   #   Entity x position, and then time offset
        self.entities = []
        self.spawn_crop_function = spawn_crop_function
        self.playing = False
        self.time = 0.0
        
        for i in range(len(self.spawn_list)):
            crop_size = (screen_size[0] * 0.1, screen_size[1] * 0.1)
            crop_pos = (self.spawn_list[i][0], -100)
            vel_x = random.randint(-Spawner.MAX_SPEED_X, Spawner.MAX_SPEED_X)
            vel_y = random.randint(0, Spawner.MAX_SPEED_Y)
            crop_vel = (vel_x, vel_y)
            self.entities.append(FallingCrop(crop_sprite, crop_size, crop_pos, crop_vel))

    def start(self):
        print("Spawner start!")
        self.playing = True

    def pause(self):
        self.playing = False

    def update(self, delta):
        if self.playing:
            self.time += delta * 1000
            if self.time > self.spawn_list[0][1]:
                # Spawn next crop
                self.time = 0
                self.spawn_next_crop()
            
    def level_over(self):
        print("Level over!")
        CustomEvents.post(CustomEvents.LEVEL_OVER)
        self.playing = False
    
    def spawn_next_crop(self):
        try:
            print(f"Spawning the next crop, crops left: {len(self.spawn_list)}")
            c = self.entities[0]
            self.spawn_crop_function(c)
            self.entities.remove(c)
            self.spawn_list.remove(self.spawn_list[0])
            if len(self.entities) == 0:
                self.level_over()
        except IndexError:
            self.level_over()
        
class FallPlayer(Player):
    def __init__(self, image: Surface, size: tuple, increment_score, pos: tuple = None, mass=10, move_y=True) -> None:
        super().__init__(image, size, pos=pos, mass=mass, move_y=move_y)
        self.increment_score = increment_score
    def update(self, delta, **kwargs):
        self.do_movement(kwargs["keys"])
        self.collide(kwargs["crops"])
        super().update(delta, **kwargs)

    def collide(self, crops:Group):
        gets_hit = pygame.sprite.spritecollide(self, crops, True)
        for _ in range(len(gets_hit)):
            self.increment_score(10)

class FallGameState(State):
    def __init__(self) -> None:
        super().__init__()

    def on_enter(self, ass_cache: AssetCache):
        self.player = FallPlayer(ass_cache.get_asset("PlayerSprite"), (BASE_SIZE[0] * 0.1, BASE_SIZE[0] * 0.1), increment_score=self.increment_score, pos=(0, BASE_SIZE[1]*0.75), mass=30, move_y=False)
        self.crop_sprite = ass_cache.get_asset("CropSprite")
        self.crops = Group()
        self.bg_col = Color(185, 243, 207)
        self.text_col = Color(255-185, 255-243, 255-207)
        self.font = Font(20, BASE_SIZE[0], False, False)
        self.score: int = 0
        self.score_text = Text("Score: 0", BASE_SIZE, (50,50), self.font, self.text_col)
        self.texts = [self.score_text]
        level = [
            (0, 500), (50, 100), (200, 200), (300, 300)
        ]
        self.spawner = Spawner(self.crop_sprite, BASE_SIZE, level, self.spawn_crop)

    def render(self, screen):
        screen.fill(self.bg_col)
        self.player.render(screen)
        self.crops.draw(screen)
        super().render(screen)

    def update(self, delta, events):
        # Make shit fall
        self.spawner.update(delta)
        keys = pygame.key.get_pressed()
        for event in events:
            if event.type == pygame.KEYUP:
                if event.key == pygame.K_u:
                    self.crops.add(FallingCrop(self.crop_sprite, (BASE_SIZE[0] * 0.1, BASE_SIZE[0] * 0.1), (BASE_SIZE[0]*0.5,0)))

                elif event.key == pygame.K_p:
                    # Play game
                    self.spawner.start()

            elif event.type == CustomEvents.get(CustomEvents.LEVEL_OVER):
                print("Level over here!")

        self.player.update(delta, keys=keys, crops=self.crops)
        self.crops.update(delta)

    def spawn_crop(self, crop: FallingCrop):
        self.crops.add(crop)
        print("Adding crop!")

    def increment_score(self, amt):
        print("incrementing score")
        self.score += amt
        self.score_text.set_text(f"Score: {self.score}")

