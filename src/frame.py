from typing import Optional, TypeVar
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
        self.rect.size = (width, height)
    
    T = TypeVar('T', bound=Hoverable)
    def add(self, hoverable: T) -> T:
        self.hoverables.add(hoverable)
        return hoverable

    def remove(self, hoverable: Hoverable):
        self.hoverables.discard(hoverable)

    def mouse_over(self):
        return self.rect.collidepoint(pygame.mouse.get_pos())

    def on_mouse_down(self, mouse: tuple[int, int]):
        for icon in self.hoverables:
            icon.click(mouse[0], mouse[1])
    
    def on_mouse_up(self, mouse: tuple[int, int]):
        pass
    
    def on_mouse_move(self, mouse: tuple[int, int]):
        """Returns the cursor that should be set, if any"""
        
        cursor_set: Optional[pygame.Cursor | int] = None
        for hoverable in self.hoverables:
            if (c := hoverable.mouse_move(mouse)) != None and not cursor_set:
                cursor_set = c
        
        return cursor_set
    
    def on_scroll(self, y: int):
        pass