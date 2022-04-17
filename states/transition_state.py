import pygame
from assets import AssetCache
from utils import easeinoutsin
from pygame import Color, Surface
from states.state import State

class TransitionState(State):
    # Transition direction
    IN = True
    OUT = False

    def __init__(self, end, duration: float, color: tuple, size, direction=IN) -> None:
        self.end_func = end
        self.duration = duration
        self.color = Color(color)
        self.size = size
        self.direction = direction

    def update(self, delta, events):
        self.time += delta

        if self.time > self.duration:
            self.end_func()

    def render(self, screen:Surface):
        if self.direction == TransitionState.OUT:
            a = int(easeinoutsin(self.time / self.duration) * 255)
        else:
            a = int((1 - easeinoutsin(self.time / self.duration)) * 255)

        self.overlay.set_alpha(a)
        screen.blit(self.overlay, (0,0))
    
    def on_enter(self, ass_cache: AssetCache):
        self.color.a = 0
        self.time = 0
        self.overlay = Surface(self.size)
        self.overlay.fill((0,0,0))
        print(f"TransitionState {self.color} on_enter()")

    def on_exit(self):
        print(f"TransitionState {self.color} on_exit()")
        del self.overlay
        del self.color

    def __repr__(self) -> str:
        if self.direction == TransitionState.IN:
            dire = "In"
        else:
            dire = "Out"
        return f"Transition {dire} duration = {self.duration}"
        

if __name__ == "__main__":
    print("Wrong file!")
    