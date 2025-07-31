import math
import pygame
from frame import Frame
from graphics.icon_button import IconButton
from graphics.asset_loader import loader
from input_sequences.event import Input
from sequencer.constants import MARGIN_LEFT, PIXELS_PER_BEAT, TOP_MARGIN
from sequencer.track import Event, Track, TrackColor
from utils import exp_decay

class Sequencer(Frame):
    tracks: list[Track]
    
    playing_direction: float
    
    time_per_beat: float
    
    scroll_target_x: float
    scroll_position_x: float
    current_position: float
    
    def __init__(self, pos: tuple[int, int, int, int], engine_width: int) -> None:
        super().__init__(pos)
        
        self.engine_width = engine_width
        
        self.title_text = loader.get_font(16).render("Sequencer", True, "white")
        self.play_pause_icon = self.add(IconButton("play_icon.png", self.play_pressed))
        self.rewind_icon = self.add(IconButton("rewind_icon.png", self.rewind_pressed))
        self.fast_forward_icon = self.add(IconButton("fast_forward_icon.png", self.fast_forward_pressed))
        
        self.tracks = [
            self.add(Track([Event(time=0, duration=3, inputs=[Input.Right, Input.Empty, Input.Right]), Event(time=4, duration=1, inputs=[Input.Right])], "A", TrackColor("#995555", "#553333", "#aa8888"), 10)),
            self.add(Track([Event(time=0, duration=3, inputs=[Input.Right, Input.Empty, Input.CycleItem]), Event(time=4, duration=3, inputs=[Input.Right, Input.Empty, Input.Down])], "B", TrackColor("#559955", "#335533", "#88aa88"), 8)),
            self.add(Track([Event(time=0, duration=3, inputs=[Input.Right, Input.Empty, Input.UseItem]), Event(time=4, duration=1, inputs=[Input.Right])], "C", TrackColor("#555599", "#333355", "#8888aa"), 5))
        ]

        self.playing_direction = 0.0
        
        self.scroll_target_x = 0.0
        self.scroll_position_x = 0.0
        self.current_position = 0.0
        
        self.time_per_beat = 0.5
    
    def play_pressed(self):
        self.playing_direction = 1 if self.playing_direction == 0 else 0
        if self.playing_direction != 0:
            self.play_pause_icon.set_icon("pause_icon.png")
        else:
            self.play_pause_icon.set_icon("play_icon.png")
    
    def rewind_pressed(self):
        self.playing_direction = -1.0 if self.playing_direction == 0.0 else 0.0

    def fast_forward_pressed(self):
        self.playing_direction = 2.0 if self.playing_direction == 0.0 else 1.0

    @staticmethod
    def format_seconds(duration: float) -> str:
        minutes = int(duration // 60)
        seconds = int(duration % 60)
        milliseconds = int((duration - int(duration)) * 1000)
        return f"{minutes:02}:{seconds:02}.{milliseconds:03}"

    def draw(self, surface: pygame.Surface):
        self.window.fill("#222222")
        pygame.draw.rect(self.window, "#333333", (0, 0, self.window.width, 32))
        self.window.blit(self.title_text, (10, 10))
        
        icon_center = self.window.width - self.engine_width // 2
        self.play_pause_icon.draw(self.window, (icon_center - 16, 0))
        self.rewind_icon.draw(self.window, (icon_center - 64, 0))
        self.fast_forward_icon.draw(self.window, (icon_center + 32, 0))
        
        # Draw the grid
        start_idx = math.floor(self.scroll_position_x) - 1
        end_idx = math.ceil((self.scroll_position_x + surface.width / PIXELS_PER_BEAT))
        
        for i in reversed(range(start_idx, end_idx + 1)):
            x = MARGIN_LEFT + i * PIXELS_PER_BEAT - self.scroll_position_x * PIXELS_PER_BEAT - 1
            pygame.draw.line(self.window, "#444444", (x, 32), (x, self.window.height), 1)
            
            sublines = 10
            for j in range(1, sublines):
                sub_x = x + j * PIXELS_PER_BEAT / sublines
                pygame.draw.line(self.window, "#444444", (sub_x, 32), (sub_x, 40), 1)
                pygame.draw.line(self.window, "#444444", (sub_x, self.window.height - 8), (sub_x, self.window.height), 1)
            
            if i % 2 == 0:
                pygame.draw.line(self.window, "#777777", (x, 32), (x, 48), 1)
                pygame.draw.line(self.window, "#777777", (x, self.window.height - 16), (x, self.window.height), 1)
            
            if i % 4 == 0:
                time_text = loader.get_font(12).render(f"{self.format_seconds(i * self.time_per_beat)}", True, "#aaaaaa")
                self.window.blit(time_text, (x + 4, 44))
        
        
        for i, track in enumerate(self.tracks):
            track.draw(self.window, 32 + TOP_MARGIN + i * 64, self.scroll_position_x)
        
        # Draw the playhead
        playhead_position = (self.current_position - self.scroll_position_x) * PIXELS_PER_BEAT + MARGIN_LEFT
        pygame.draw.rect(self.window, "#ee8888", (playhead_position - 1, 32, 2, self.window.height - 32))
        pygame.draw.polygon(self.window, "#ee8888", [
            (playhead_position, 32),
            (playhead_position + 8, 32),
            (playhead_position, 32 + 8)
        ])
        
        super().draw(surface)

    def update(self, engine, delta):
        self.scroll_position_x = exp_decay(self.scroll_position_x, self.scroll_target_x, 15, delta)
        
        for track in self.tracks:
            track.update(delta)
        
        if self.playing_direction != 0:
            old_beat: int = int(self.current_position)
            self.current_position += delta / self.time_per_beat * self.playing_direction
            if self.current_position <= 0:
                self.current_position = 0
                self.playing_direction = 0.0
            
            # Scroll the playhead into view
            scroll_margin = self.window.width / 5
            if self.current_position * PIXELS_PER_BEAT < self.scroll_position_x * PIXELS_PER_BEAT + scroll_margin:
                self.scroll_target_x = max(0, self.current_position - scroll_margin / PIXELS_PER_BEAT)
            elif self.current_position * PIXELS_PER_BEAT > self.scroll_position_x * PIXELS_PER_BEAT + self.window.width - scroll_margin:
                self.scroll_target_x = self.current_position + scroll_margin / PIXELS_PER_BEAT - self.window.width / PIXELS_PER_BEAT
            
            beat: int = int(self.current_position)

            if len(engine.entities) and engine.entities[0].health <= 0:
                return

            # every beat, loop over the tracks and
            # some other shit in order to trigger
            # events/inputs
            if beat != old_beat:
                for track in self.tracks:
                    track_beat: int = beat % track.repeat_length
                    event_index: int = -1
                    input_index: int = -1
                    for i, event in enumerate(track.events):
                        if track_beat in [event.time + j for j in range(event.duration)]:
                            event_index = i
                            input_index = int(track_beat - event.time)
                            break
                    new_input: Input = track.events[event_index].inputs[input_index]
                    if new_input != Input.Empty:
                        # trigger a function
                        match new_input:
                            case Input.Up: engine.move_player(0, -1)
                            case Input.Down: engine.move_player(0, 1)
                            case Input.Left: engine.move_player(-1, 0)
                            case Input.Right: engine.move_player(1, 0)
    
    def on_scroll(self, y: int):
        self.scroll_target_x -= y
        self.scroll_target_x = max(0, self.scroll_target_x)