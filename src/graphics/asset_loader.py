import os
from pygame import Font, Surface
import pygame

class AssetLoader:
    icons: dict[str, Surface]
    fonts: dict[int, Font]
    
    def __init__(self):
        self.icons = dict()
        self.fonts = dict()
    
    def load(self, filename: str) -> Surface:
        if filename not in self.icons:
            self.icons[filename] = pygame.image.load(os.path.join("assets", filename)).convert_alpha()
        return self.icons[filename]
    
    def get_font(self, size: int) -> Font:
        if size not in self.fonts:
            self.fonts[size] = pygame.font.SysFont("Courier", size)
        return self.fonts[size]

loader = AssetLoader()