import pygame
from frame import Frame
from graphics.asset_loader import loader

class InputSequences(Frame):
    def __init__(self, pos: tuple[int, int, int, int]) -> None:
        super().__init__(pos)
        
        self.title_text = loader.get_font(16).render("Input sequences", True, "white")
        
    def resize(self, width, height):
        self.window = pygame.Surface((width, height))

    def draw(self, surface: pygame.Surface):
        self.window.fill("#222222")
        self.window.fill("#333333", (0, 0, self.window.width, 24))
        self.window.blit(self.title_text, (8, 5))
        
        super().draw(surface)