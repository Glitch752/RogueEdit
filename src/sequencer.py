from dataclasses import dataclass
import pygame
from frame import Frame
from graphics.icon_button import IconButton
from graphics.asset_loader import loader

@dataclass
class TrackColor:
    background: str
    repeat_background: str
    title: str

TRACK_COLORS = [
    TrackColor("#995555", "#553333", "#aa8888"),
    TrackColor("#559955", "#335533", "#88aa88"),
    TrackColor("#555599", "#333355", "#8888aa"),
    TrackColor("#999955", "#555533", "#aaaa88")
]
TOP_MARGIN = 32
PIXELS_PER_BEAT = 50

class Track:
    events: list[str]
    name_text: pygame.Surface
    color: TrackColor
    repeat_length: float
    
    def __init__(self, events: list[str], name: str, color: TrackColor, repeat_length: float) -> None:
        self.events = events
        self.name_text = loader.get_font(32).render(name, True, "white")
        self.color = color
        self.repeat_length = repeat_length
        
    def draw(self, surface: pygame.Surface, y: int):
        width = min(surface.get_width(), 48 + PIXELS_PER_BEAT * self.repeat_length)
        pygame.draw.rect(surface, self.color.background, (0, y, width, 48))
        pygame.draw.rect(surface, self.color.repeat_background, (width, y, surface.get_width() - width, 48))
        pygame.draw.rect(surface, self.color.title, (0, y, 48, 48))
        surface.blit(self.name_text, (10, y + 8))

class Sequencer(Frame):
    tracks: list[Track]
    
    playing: bool
    rewind: bool
    fast_forward: bool
    playing_direction: float
    
    time_per_beat: float
    
    current_position: float
    
    def __init__(self, pos: tuple[int, int, int, int], engine_width: int) -> None:
        super().__init__(pos)
        
        self.engine_width = engine_width
        
        self.title_text = loader.get_font(12).render("Sequencer", True, "white")
        self.play_pause_icon = self.add_icon(IconButton("play_icon.png", self.play_pressed))
        self.rewind_icon = self.add_icon(IconButton("rewind_icon.png", self.rewind_pressed))
        self.fast_forward_icon = self.add_icon(IconButton("fast_forward_icon.png", self.fast_forward_pressed))
        
        self.tracks = [
            Track(["event1", "event2"], "A", TRACK_COLORS[0], 3),
            Track(["event1", "event2"], "B", TRACK_COLORS[1], 5),
            Track(["event1", "event2"], "C", TRACK_COLORS[2], 8),
            Track(["event1", "event2"], "D", TRACK_COLORS[3], 10)
        ]

        self.playing = False
        self.rewind = False
        self.fast_forward = False
        
        self.playing_direction = 1.0
        
        self.current_position = 0.0
        
        self.time_per_beat = 0.25
    
    def play_pressed(self):
        self.playing = not self.playing
        if self.playing:
            self.play_pause_icon.set_icon("pause_icon.png")
        else:
            self.play_pause_icon.set_icon("play_icon.png")
    
    def rewind_pressed(self):
        self.rewind = not self.rewind
        self.playing_direction = -1.0 if self.rewind else 1.0

    def fast_forward_pressed(self):
        self.fast_forward = not self.fast_forward
        self.playing_direction = 2.0 if self.fast_forward else 1.0

    def draw(self, surface: pygame.Surface):
        self.window.fill("#222222")
        pygame.draw.rect(self.window, "#333333", (0, 0, self.window.get_width(), 32))
        self.window.blit(self.title_text, (10, 10))
        
        icon_center = self.window.get_width() - self.engine_width // 2
        self.play_pause_icon.draw(self.window, (icon_center - 16, 0))
        self.rewind_icon.draw(self.window, (icon_center - 64, 0))
        self.fast_forward_icon.draw(self.window, (icon_center + 32, 0))
        
        for i, track in enumerate(self.tracks):
            track.draw(self.window, 32 + TOP_MARGIN + i * 64)
        
        super().draw(surface)

    def update(self, delta):
        self.beat_timer += delta
        if self.beat_timer >= self.time_per_beat:
            self.beat_timer -= self.time_per_beat

            self.current_beat += 1