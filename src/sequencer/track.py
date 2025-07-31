from dataclasses import dataclass
import math
from graphics.asset_loader import loader
import pygame

from graphics.hoverable import Hoverable
from sequencer.constants import MARGIN_LEFT, PIXELS_PER_BEAT, TRACK_HEIGHT

from input_sequences.event import Event, EventVisualizer

@dataclass
class TrackColor:
    background: str
    repeat_background: str
    title: str

class Track(Hoverable):
    events: list[Event]
    visualizers: list[EventVisualizer]
    name_text: pygame.Surface
    color: TrackColor
    repeat_length: int
    background_surface: pygame.Surface | None
    
    def __init__(self, events: list[Event], name: str, color: TrackColor, repeat_length: int) -> None:
        self.events = events
        self.visualizers = [EventVisualizer(ev) for ev in events]
        
        super().__init__()
        
        self.name_text = loader.get_font(32).render(name, True, "white")
        self.color = color
        self.repeat_length = repeat_length
        self.background_surface = None
    
    def update(self, delta: float):
        for vis in self.visualizers:
            vis.update(delta)
    
    def draw(self, surface: pygame.Surface, y: int, scroll_position_x: float):
        width = min(surface.width, MARGIN_LEFT + PIXELS_PER_BEAT * self.repeat_length)
        self.rect = pygame.Rect(0, y, surface.width, TRACK_HEIGHT)
        
        if self.background_surface == None or self.background_surface.width != surface.width:
            self.background_surface = pygame.Surface((surface.width, TRACK_HEIGHT))
            self.background_surface.set_alpha(0x80)
            self.background_surface.fill(self.color.repeat_background)
        
        surface.blit(self.background_surface, (0, y))
        
        pygame.draw.rect(surface, self.color.background, (-scroll_position_x * PIXELS_PER_BEAT, y, width, TRACK_HEIGHT), 2)

        start_idx = math.floor(scroll_position_x / self.repeat_length)
        end_idx = math.ceil((scroll_position_x + surface.width / PIXELS_PER_BEAT) / self.repeat_length)\
        
        for vis in self.visualizers:
            vis.reset()
        
        for i in range(start_idx, end_idx + 1):
            x = MARGIN_LEFT + i * self.repeat_length * PIXELS_PER_BEAT - scroll_position_x * PIXELS_PER_BEAT
            for vis in self.visualizers:
                event_x = math.floor(x + vis.event.time * PIXELS_PER_BEAT)
                vis.draw(surface, event_x, y, self.color.repeat_background if i > 0 else self.color.background)
        
        pygame.draw.rect(surface, self.color.title, (0, y, MARGIN_LEFT, TRACK_HEIGHT))
        surface.blit(self.name_text, (10, y + 8))
        
    def mouse_move(self, mouse: tuple[int, int]):
        if self.in_self(mouse):
            for vis in self.visualizers:
                vis.mouse_move(mouse)
        else:
            for vis in self.visualizers:
                vis.hovered = False
    
    def click(self, x: int, y: int):
        for vis in self.visualizers:
            vis.click(x, y)