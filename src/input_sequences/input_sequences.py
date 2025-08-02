from typing import Optional
import pygame
from frame import Frame
from graphics.asset_loader import loader
from input_sequences.event import Event, Input, EventVisualizer
from sequencer.constants import PIXELS_PER_BEAT, SECONDS_PER_BEAT
from utils import exp_decay, format_seconds

EVENT_SELECTOR_PADDING = 5
EVENT_SELECTOR_HEADER = 22
SEQUENCE_WINDOW_PADDING = 10

class EventSelector(EventVisualizer):
    dragging: bool
    drag_offset: tuple[int, int]
    title_text: pygame.Surface
    
    def __init__(self, event: Event):
        super().__init__(event)
        self.dragging = False
        self.drag_offset = (0, 0)
        self.title_text = loader.get_font(17).render(f"{format_seconds(self.event.duration * SECONDS_PER_BEAT, True)}s", True, "gray")
    
    def draw_ghost(self, surface: pygame.Surface, x: int, y: int, alpha: float, color = "#777777"):
        self.reset()
        
        temp_surface = pygame.Surface((self.rect.width, self.rect.height), pygame.SRCALPHA)
        temp_surface.fill((0, 0, 0, 0))
        super().draw(temp_surface, 0, 0, color)
        temp_surface.set_alpha(int(alpha * 255))
        surface.blit(temp_surface, (x, y))
    
    def start_drag(self, mouse: tuple[int, int]):
        self.dragging = True
        self.drag_offset = (
            mouse[0] - self.rect.x - EVENT_SELECTOR_PADDING,
            mouse[1] - self.rect.y - EVENT_SELECTOR_PADDING - EVENT_SELECTOR_HEADER
        )
    
    def draw(self, surface: pygame.Surface, x: int, y: int):
        self.reset()
        
        r = self.get_rect(x + EVENT_SELECTOR_PADDING, y + EVENT_SELECTOR_PADDING)
        self.rect = pygame.Rect(
            r.x - EVENT_SELECTOR_PADDING, r.y - EVENT_SELECTOR_PADDING,
            r.width + EVENT_SELECTOR_PADDING * 2, r.height + EVENT_SELECTOR_PADDING * 2 + EVENT_SELECTOR_HEADER
        )
        
        # If not on the screen, don't draw
        if not self.rect.colliderect(surface.get_rect()):
            return
        
        color = "#444444" if self.hovered else "#333333"
        if self.dragging:
            color = "#555555"
        pygame.draw.rect(surface, color, self.rect, 0, 5)
        pygame.draw.rect(surface, "#666666", self.rect, 2, 5)
        
        surface.blit(self.title_text, (x + EVENT_SELECTOR_PADDING + 5, y + EVENT_SELECTOR_PADDING + 4))
        
        super().draw(surface, x + EVENT_SELECTOR_PADDING, y + EVENT_SELECTOR_PADDING + EVENT_SELECTOR_HEADER, "#777777")
    
    def in_self(self, point: tuple[int, int]) -> bool:
        return self.rect.collidepoint(point)

class InputSequences(Frame):
    events: list[EventSelector]
    
    target_scroll_y: float
    scroll_y: float
    
    dragged_item: Optional[EventSelector]
    
    def __init__(self, pos: tuple[int, int, int, int]) -> None:
        super().__init__(pos)
        
        self.title_text = loader.get_font(16).render("Input sequences", True, "white")
        self.target_scroll_y = 0.0
        self.scroll_y = 0.0
        self.dragged_item = None
        
        # Define predefined sequences for different levels/scenarios
        self.events = [
            self.add(EventSelector(Event(time=0, duration=2, inputs=[Input.Right, Input.UseItem]))),
            self.add(EventSelector(Event(time=0, duration=2, inputs=[Input.Right, Input.UseItem]))),
            self.add(EventSelector(Event(time=0, duration=3, inputs=[Input.UseItem, Input.UseItem, Input.UseItem]))),
            self.add(EventSelector(Event(time=0, duration=4, inputs=[Input.Left, Input.Up, Input.Right, Input.Down]))),
            self.add(EventSelector(Event(time=0, duration=4, inputs=[Input.Left, Input.Up, Input.Right, Input.Down]))),
            self.add(EventSelector(Event(time=0, duration=1, inputs=[Input.Wait])))
        ]
    
    def draw(self, surface: pygame.Surface):
        self.window.fill("#222222")
        
        y_offset = 24 + SEQUENCE_WINDOW_PADDING - int(self.scroll_y)
        x_offset = SEQUENCE_WINDOW_PADDING
        
        for i, event in enumerate(self.events):
            # Flex-ish wrapping layout (ish?)
            if x_offset + event.rect.width > self.window.width - SEQUENCE_WINDOW_PADDING:
                x_offset = SEQUENCE_WINDOW_PADDING
                y_offset += event.rect.height + SEQUENCE_WINDOW_PADDING
            
            event.draw(self.window, x_offset, y_offset)
            
            x_offset += event.rect.width + SEQUENCE_WINDOW_PADDING
        
        self.target_scroll_y = min(self.target_scroll_y, max(0, y_offset + event.rect.height + SEQUENCE_WINDOW_PADDING - self.window.height))
        
        self.window.fill("#333333", (0, 0, self.window.width, 24))
        self.window.blit(self.title_text, (8, 5))
        
        super().draw(surface)
        
        if self.dragged_item != None:
            mouse = pygame.mouse.get_pos()
            self.dragged_item.draw_ghost(
                surface,
                mouse[0] - self.dragged_item.drag_offset[0],
                mouse[1] - self.dragged_item.drag_offset[1],
                0.5
            )

    def update(self, delta: float):
        self.scroll_y = exp_decay(self.scroll_y, self.target_scroll_y, 20, delta)
        
        for sequence in self.events:
            sequence.update(delta)
            
    def on_mouse_down(self, mouse: tuple[int, int]):
        for event in self.events:
            if event.rect.collidepoint(mouse):
                event.start_drag(mouse)
                self.dragged_item = event
                return
        
        super().on_mouse_down(mouse)

    def on_mouse_up(self, mouse: tuple[int, int]):
        if self.dragged_item:
            self.dragged_item.dragging = False
            self.dragged_item = None
        
        super().on_mouse_up(mouse)

    def on_scroll(self, y: int):
        self.target_scroll_y -= y * 20
        self.target_scroll_y = max(0, self.target_scroll_y)
        
    def get_dragged_item(self):
        """Returns the currently dragged item, if any"""
        return self.dragged_item