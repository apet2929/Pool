import random
from enum import Enum

import pygame
import pygame.display
import pygame.draw
import pygame.event
import pygame.mouse
import pygame.rect
import pygame.surface
import pygame.time
from pygame.color import Color
from entitites.entity import Entity
from states.fall_game_state import FallGameState
from states.pool_game_state import PoolGameState
import ui
from assets import AssetCache
from states.state import State
from states.state_manager import GameStateManager
from states.title_state import TitleState
from states.transition_state import TransitionState
from utils import BASE_SIZE
from pygame import Vector2

pygame.init()

class TestState(State):
    def __init__(self) -> None:
        self.bgcol = Color(
            random.randint(0, 255), random.randint(0, 255), random.randint(0, 255)
        )

    def render(self, screen: pygame.Surface):
        screen.fill(self.bgcol)

    def on_enter(self):
        print(f"State {self.bgcol} on_enter()")

    def on_exit(self):
        print(f"State {self.bgcol} on_exit()")

    def __repr__(self) -> str:
        return f"State {self.bgcol}"

class Game:
    def __init__(self) -> None:
        self.running = False
        self.display = pygame.display.set_mode(BASE_SIZE)
        self.screen = pygame.Surface(BASE_SIZE)
        self.screen = self.screen.convert()
        self.display.fill((255, 255, 255))
        self.asset_cache = AssetCache()
        print(self.asset_cache.asset_manager.assets)

        self.clock = pygame.time.Clock()
        self.font = ui.Font(20, BASE_SIZE[0], False, False)
        self.gsm = GameStateManager()
        self.gsm.push(PoolGameState(), self.asset_cache)


    def run(self):
        self.running = True
        while self.running:
            delta = self.clock.tick(FPS) / 1000
            events = pygame.event.get()

            self.update(delta, events)

            self.render()
            self.display.blit(self.screen, (0, 0))

            pygame.display.flip()

    def handle_events(self, events: list[pygame.event.Event]):
        for event in events:
            if event.type == pygame.QUIT:
                self.running = False
            if event.type == pygame.KEYUP:
                if event.key == pygame.K_RETURN:
                    self.transition()
                if event.key == pygame.K_RSHIFT:
                    self.transition(TestState())
                if event.key == pygame.K_0:
                    for i, state in enumerate(self.gsm.states):
                        print(i, state)

            if event.type == pygame.USEREVENT + 1:
                pygame.image.save(self.screen, "collision_point.jpg")

    def play(self):
        print("Playing Game!")
        self.transition(TestState())

    def quit(self):
        print("Quitting")
        self.running = False

    def transition(self, state=None):
        def fade_out_done():
            print("Fade out done")
            self.gsm.pop()
            if state is not None:
                self.gsm.push(state, self.asset_cache)
            else:
                self.gsm.pop()
            self.fade_in()

        self.gsm.push(
            TransitionState(
                fade_out_done, 2, (0, 0, 0), self.screen.get_size(), TransitionState.OUT
            ), self.asset_cache
        )

    def fade_in(self):
        def fade_in_done():
            print("Fade in done")
            self.gsm.pop()

        self.gsm.push(
            TransitionState(
                fade_in_done, 2, (0, 0, 0), self.screen.get_size(), TransitionState.IN
            ), self.asset_cache
        )

    def update(self, delta, events):
        """
        Handle input, and update the top state in the stack
        """
        self.handle_events(events)
        self.gsm.peek().update(delta, events)

    def render(self):
        """
        Render every state in the stack
        """
        self.display.fill((255, 255, 255))
        self.screen.fill((255, 255, 255))
        for state in self.gsm.states:
            state.render(self.screen)
        
    


def main():
    game = Game()
    game.run()
    pygame.quit()


FPS = 60
if __name__ == "__main__":
    # logger, handler = log.setup_logs("Game Jam", logging.DEBUG)
    main()
