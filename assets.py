from utils import resource_path
from pygame import Surface
import pygame.transform
import pygame.image

class AssetManager:
    def __init__(self) -> None:
        self.assets = {
            "NOT_FOUND": resource_path("assets/not_found.jpg"),
            "CropSprite": resource_path("assets/cabbage.png"),
            "Table": resource_path("assets/pool_table.jpg")
        }
    
    def get_asset_path(self, name):
        if name in self.assets.keys():
            return self.assets[name]

        # Asset not found
        print(f"Asset {name} not found!")
        return self.assets["NOT_FOUND"]

class AssetCache:
    def __init__(self) -> None:
        self.asset_manager = AssetManager()

        self.assets = {
            "NOT_FOUND": pygame.image.load(self.asset_manager.get_asset_path("NOT_FOUND")).convert()
        }

    def get_asset(self, name:str) -> Surface:
        if name not in self.assets.keys():
            self.assets[name] = pygame.image.load(self.asset_manager.get_asset_path(name)).convert()
        return self.assets[name]

