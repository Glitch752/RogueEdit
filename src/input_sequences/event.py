from dataclasses import dataclass
from enum import Enum
import math

import pygame
from graphics.asset_loader import loader
from graphics.hoverable import Hoverable
from sequencer.constants import MARGIN_LEFT, PIXELS_PER_BEAT, TRACK_HEIGHT
from utils import exp_decay

class Input(Enum):
    Empty = "empty", "empty_input.png"
    Up = "up", "up_arrow.png"
    Left = "left", "left_arrow.png"
    Right = "right", "right_arrow.png"
    Down = "down", "down_arrow.png"
    UseItem = "use_item", "swords.png"
    CycleItem = "cycle_item", "cycle.png"
    Wait = "wait", "wait.png"
    
    icon: str
    
    def __new__(cls, value: str, icon: str):
        member = object.__new__(cls)
        member._value_ = value
        member.icon = icon
        return member

@dataclass
class Event:
    inputs: list[Input]
    time: int
    duration: int

class EventVisualizer(Hoverable):
    event: Event
    float_height: float
    float_height_target: float
    rects: list[pygame.Rect]
    
    def __init__(self, event: Event):
        super().__init__()
        self.rects = []
        self.event = event
        self.float_height = 0.0
        self.float_height_target = 0.0
    
    def update(self, dt: float):
        self.float_height_target = 3.0 if self.hovered else 0.0
        self.float_height = exp_decay(self.float_height, self.float_height_target, 15, dt)
    
    def reset(self):
        self.rects = []
    
    def get_rect(self, x: int, y: int):
        event_width = self.event.duration * PIXELS_PER_BEAT
        return pygame.Rect(x, y, event_width, TRACK_HEIGHT)
    
    def draw(self, surface: pygame.Surface, x: int, y: int, color: str):
        float_height = math.floor(self.float_height)
        self.rects.append(self.get_rect(x, y))
        event_width = self.event.duration * PIXELS_PER_BEAT
        pygame.draw.rect(surface, "#111111", (x + 3, y + 3, event_width - 6, TRACK_HEIGHT - 6), 0, 10)
        pygame.draw.rect(surface, color, (x + 3, y + 3 - float_height, event_width - 6, TRACK_HEIGHT - 9), 0, 10)
        for i, input in enumerate(self.event.inputs):
            surface.blit(t := loader.load(input.icon), (
                x + i * PIXELS_PER_BEAT + PIXELS_PER_BEAT // 2 - t.width // 2,
                y + 24 - t.height // 2 - 2 - float_height
            ))

    def in_self(self, point: tuple[int, int]) -> bool:
        for rect in self.rects:
            if rect.collidepoint(point):
                return True
        return False