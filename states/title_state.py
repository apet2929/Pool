from states.state import State
from ui import Button, Text
from pygame import Color
from pygame import MOUSEBUTTONUP

from utils import BASE_SIZE

class TitleState(State):
    button_color_1 = Color(147, 198, 237)
    button_color_2 = Color(124, 143, 196)
    button_text_color = Color(48, 36, 23)
    bgcol = Color(209, 255, 214)

    def __init__(self, size, font, play_func, quit_func) -> None:
        title_text = Text("P00L", size, (50,25), font, (0,0,0))
        play_button = Button("PLAY", size, (70, 50), (25, 10), TitleState.button_color_1, TitleState.button_color_2, TitleState.button_text_color, font, 40)
        quit_button = Button("QUIT", size, (30, 50), (25, 10), TitleState.button_color_1, TitleState.button_color_2, TitleState.button_text_color, font, 40)
        self.play_func = play_func
        self.quit_func = quit_func
        self.texts = [title_text]
        self.buttons = [play_button, quit_button]

    def update(self, delta, events):
        for event in events:
            if event.type == MOUSEBUTTONUP:
                index = self.button_clicked(event)
                if index == 0:
                    # Play
                    self.play_func()
                elif index == 1:
                    # Quit
                    self.quit_func()
    
    def render(self, screen):
        screen.fill(self.bgcol)
        self.draw_ui(screen)


