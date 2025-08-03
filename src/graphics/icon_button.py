from pygame import Surface
import pygame

from graphics.hoverable import Hoverable
from .asset_loader import loader
from typing import Callable
from audio import audio_manager, SoundType

class IconButton(Hoverable):
    icon: Surface
    shown: bool
    
    def __init__(self, filename: str, click_callback: Callable):
        self.icon = loader.load(filename)
        self.rect = pygame.Rect(0, 0, *self.icon.get_size())
        self.click_callback = click_callback
        self.hovered = False
        self.hovered_last = False
        self.shown = True
        
        self.rect_surface = pygame.Surface(self.rect.size, pygame.SRCALPHA)
        pygame.draw.rect(self.rect_surface, "#ffffff", (0, 0, *self.rect.size))
        self.rect_surface.set_alpha(0x33)
    
    def set_icon(self, filename: str):
        self.icon = loader.load(filename)
    
    def in_self(self, point: tuple[int, int]) -> bool:
        if not self.shown:
            return False
        return super().in_self(point)
    
    def draw(self, surface: Surface, pos: tuple[int, int]):
        if not self.shown:
            return
        
        (self.rect.x, self.rect.y) = pos
        
        surface.blit(self.icon, self.rect)
        if self.hovered:
            surface.blit(self.rect_surface, (self.rect.x, self.rect.y))
            if not self.hovered_last:
                audio_manager.play_sound(SoundType.HOVER, 0.3)

        self.hovered_last = self.hovered