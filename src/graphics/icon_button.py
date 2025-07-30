from pygame import Surface
import pygame
from .asset_loader import loader
from typing import Callable

class IconButton:
    icon: Surface
    hovered: bool
    
    def __init__(self, filename: str, click_callback: Callable):
        self.icon = loader.load(filename)
        self.rect = pygame.Rect(0, 0, *self.icon.get_size())
        self.click_callback = click_callback
        self.hovered = False
        
        self.rect_surface = pygame.Surface(self.rect.size, pygame.SRCALPHA)
        pygame.draw.rect(self.rect_surface, "#ffffff", (0, 0, *self.rect.size))
        self.rect_surface.set_alpha(0x33)
    
    def set_icon(self, filename: str):
        self.icon = loader.load(filename)
        
    def mouse_move(self, mouse: tuple[int, int]):
        self.hovered = self.rect.collidepoint(*mouse)
    
    def draw(self, surface: Surface, pos: tuple[int, int]):
        (self.rect.x, self.rect.y) = pos
        
        surface.blit(self.icon, self.rect)
        if self.hovered:
            surface.blit(self.rect_surface, (self.rect.x, self.rect.y))
    
    def click(self, x: int, y: int):
        if self.rect.collidepoint(x, y):
            self.click_callback()