from typing import Callable, Optional
import pygame

class Hoverable:
    rect: pygame.Rect
    hovered: bool
    click_callback: Optional[Callable]
    
    def __init__(self):
        self.rect = pygame.Rect()
        self.hovered = False
        self.click_callback = None
    
    def in_self(self, point: tuple[int, int]) -> bool:
        return self.rect.collidepoint(point)
    
    def mouse_move(self, mouse: tuple[int, int]):
        self.hovered = self.in_self(mouse)
        
    def click(self, x: int, y: int):
        if self.in_self((x, y)):
            if self.click_callback:
                self.click_callback()