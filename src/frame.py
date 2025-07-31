from typing import TypeVar
import pygame

from graphics.hoverable import Hoverable
from graphics.icon_button import IconButton

class Frame:
    hoverables: set[Hoverable]
    window: pygame.Surface
    
    def __init__(self, bounds: tuple[int, int, int, int]) -> None:
        self.rect = pygame.Rect(bounds)
        self.window = pygame.Surface(self.rect.size)
        self.hoverables = set()
    
    def draw(self, surface: pygame.Surface):
        surface.blit(self.window, (self.rect.x, self.rect.y))

    def resize(self, width, height):
        self.window = pygame.Surface((width, height))
    
    T = TypeVar('T', bound=Hoverable)
    def add(self, hoverable: T) -> T:
        self.hoverables.add(hoverable)
        return hoverable

    def mouse_over(self):
        return self.rect.collidepoint(pygame.mouse.get_pos())

    def on_click(self):
        mouse = pygame.mouse.get_pos()
        (mx, my) = (mouse[0] - self.rect.x, mouse[1] - self.rect.y)
        for icon in self.hoverables:
            icon.click(mx, my)
    
    def on_mouse_move(self):
        mouse = pygame.mouse.get_pos()
        (mx, my) = (mouse[0] - self.rect.x, mouse[1] - self.rect.y)
        for hoverable in self.hoverables:
            hoverable.mouse_move((mx, my))
    
    def on_scroll(self, y: int):
        pass