from typing import Optional
import pygame
from frame import Frame
from graphics.asset_loader import loader
from input_sequences.event import Event, EventId, Input, EventVisualizer, get_next_event_id
from sequencer.constants import SECONDS_PER_BEAT
from utils import exp_decay, format_seconds

EVENT_SELECTOR_PADDING = 5
EVENT_SELECTOR_HEADER = 22
SEQUENCE_WINDOW_PADDING = 10

class EventSelector(EventVisualizer):
    dragging: bool
    drag_offset: tuple[int, int]
    title_text: pygame.Surface
    visible: bool
    
    def __init__(self, inputs: list[Input]):
        super().__init__(Event(
            id=get_next_event_id(),
            time=0,
            duration=len(inputs),
            inputs=inputs
        ))
        self.visible = True
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
        return self.visible and self.rect.collidepoint(point)

class InputSequences(Frame):
    events: list[EventSelector]
    
    target_scroll_y: float
    scroll_y: float
    
    no_events_text: pygame.Surface
    
    dragged_item: Optional[EventSelector]
    
    def __init__(self, pos: tuple[int, int, int, int]) -> None:
        super().__init__(pos)
        
        self.title_text = loader.get_font(16).render("Input sequences", True, "white")
        self.target_scroll_y = 0.0
        self.scroll_y = 0.0
        self.dragged_item = None
        
        self.no_events_text = loader.get_font(20).render("No remaining sequences", True, "gray")
        
        # Define predefined sequences for different levels/scenarios
        self.events = []
    
    def set_events(self, events: list[list[Input]]):
        for event in self.events:
            self.remove(event)
        
        self.events = [self.add(EventSelector(inputs)) for inputs in events]
    
    def draw(self, surface: pygame.Surface):
        self.window.fill("#222222")
        
        y_offset = 24 + SEQUENCE_WINDOW_PADDING - int(self.scroll_y)
        x_offset = SEQUENCE_WINDOW_PADDING
        
        drawn = 0
        for i, event in enumerate(self.events):
            if not event.visible:
                continue
            drawn += 1
            
            # Flex-ish wrapping layout (ish?)
            if x_offset + event.rect.width > self.window.width - SEQUENCE_WINDOW_PADDING:
                x_offset = SEQUENCE_WINDOW_PADDING
                y_offset += event.rect.height + SEQUENCE_WINDOW_PADDING
            
            event.draw(self.window, x_offset, y_offset)
            
            x_offset += event.rect.width + SEQUENCE_WINDOW_PADDING
        
        if drawn > 0:
            last_event = self.events[-1]
            self.target_scroll_y = min(self.target_scroll_y, max(0, y_offset + last_event.rect.height + SEQUENCE_WINDOW_PADDING - self.window.height))
        else:
            self.target_scroll_y = 0
            
            self.window.blit(
                self.no_events_text,
                (self.window.width // 2 - self.no_events_text.get_width() // 2, 64)
            )
        
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
            if event.in_self(mouse):
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

    def dragged_item_dropped(self):
        """Called when the dragged item is dropped elsewhere"""
        if self.dragged_item:
            self.dragged_item.visible = False
        self.dragged_item = None
    
    def begin_drag(self, event_id: EventId, drag_offset: tuple[int, int]) -> Optional[EventSelector]:
        """Begins dragging an event from the sequencer, e.g. one that is hidden on our side"""
        if self.dragged_item:
            return
        
        matching_selector = next((e for e in self.events if e.event.id == event_id), None)
        if matching_selector:
            self.dragged_item = matching_selector
            matching_selector.visible = True
            matching_selector.dragging = True
            matching_selector.drag_offset = drag_offset
        return matching_selector
