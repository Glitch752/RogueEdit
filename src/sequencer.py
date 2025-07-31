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

        for event in self.events:
            for i, _input in enumerate(event["inputs"]):
                if _input != "none":
                    j = event["time"] + i
                    surface.blit(t := loader.get_font(16).render(_input.capitalize(), True, 'white'), (48 + PIXELS_PER_BEAT * j + PIXELS_PER_BEAT // 2 - t.get_width() // 2, y + 24 - t.get_height() // 2))

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
        
        self.title_text = loader.get_font(16).render("Sequencer", True, "white")
        self.play_pause_icon = self.add_icon(IconButton("play_icon.png", self.play_pressed))
        self.rewind_icon = self.add_icon(IconButton("rewind_icon.png", self.rewind_pressed))
        self.fast_forward_icon = self.add_icon(IconButton("fast_forward_icon.png", self.fast_forward_pressed))
        
        self.tracks = [
            Track([{"time": 0, "duration": 3, "inputs": ["right", "none", "right"]}, {"time": 4, "duration": 1, "inputs": ["up"]}], "A", TRACK_COLORS[0], 10),
            Track([{"time": 0, "duration": 3, "inputs": ["right", "none", "right"]}, {"time": 4, "duration": 1, "inputs": ["up"]}], "B", TRACK_COLORS[1], 8),
            Track([{"time": 0, "duration": 3, "inputs": ["right", "none", "right"]}, {"time": 4, "duration": 1, "inputs": ["up"]}], "C", TRACK_COLORS[2], 5)
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

    def update(self, engine, delta):
        if self.playing:
            old_beat: int = self.current_position // self.time_per_beat
            self.current_position += delta
            beat: int = self.current_position // self.time_per_beat

            # every beat, loop over the tracks and
            # some other shit in order to trigger
            # events/inputs
            if beat != old_beat:
                for track in self.tracks:
                    track_beat: int = beat % track.repeat_length
                    event_index: int = -1
                    input_index: int = -1
                    for i, event in enumerate(track.events):
                        if track_beat in [event["time"] + j for j in range(event["duration"])]:
                            event_index = i
                            input_index = int(track_beat - event["time"])
                            break
                    new_input: str = track.events[event_index]["inputs"][input_index]
                    if new_input != "none":
                        # trigger a function
                        match new_input:
                            case "up": engine.move_player(0, -1)
                            case "down": engine.move_player(0, 1)
                            case "left": engine.move_player(-1, 0)
                            case "right": engine.move_player(1, 0)