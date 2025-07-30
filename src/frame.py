import pygame

from graphics.icon_button import IconButton
from graphics.asset_loader import loader

class Frame:
    icons: set[IconButton]
    window: pygame.Surface
    
    def __init__(self, bounds: tuple[int, int, int, int]) -> None:
        self.rect = pygame.Rect(bounds)
        self.window = pygame.Surface(self.rect.size)
        self.icons = set()
    
    def draw(self, surface: pygame.Surface):
        surface.blit(self.window, (self.rect.x, self.rect.y))

    def resize(self, width, height):
        self.window = pygame.Surface((width, height))
    
    def add_icon(self, icon: IconButton) -> IconButton:
        self.icons.add(icon)
        return icon

    def on_click(self):
        mouse = pygame.mouse.get_pos()
        if self.rect.collidepoint(mouse):
            (mx, my) = (mouse[0] - self.rect.x, mouse[1] - self.rect.y)
            for icon in self.icons:
                icon.click(mx, my)
    
    def on_mouse_move(self):
        mouse = pygame.mouse.get_pos()
        (mx, my) = (mouse[0] - self.rect.x, mouse[1] - self.rect.y)
        for icon in self.icons:
            icon.mouse_move((mx, my))