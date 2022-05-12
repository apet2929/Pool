from assets import AssetCache
from ui import Button, Text
from pygame import MOUSEBUTTONUP


class State:
    def __init__(self) -> None:
        self.buttons: list[Button] = []
        self.texts: list[Text] = []

    def update(self, delta, events):
        pass

    def render(self, screen):
        pass
    
    def on_enter(self, asset_cache:AssetCache):
        """
        Initialize any assets
        """
        pass
    
    def on_exit(self):
        self.buttons = []
        self.texts = []
        pass

    def button_clicked(self, event):
        assert event.type == MOUSEBUTTONUP
        for i, button in enumerate(self.buttons):
            if button.check_click(event.pos):
                return i
        return None

    def draw_ui(self, screen):
        for text in self.texts:
            text.draw(screen)
        
        for button in self.buttons:
            button.draw(screen)