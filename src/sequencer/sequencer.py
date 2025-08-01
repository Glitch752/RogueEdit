import math
import pygame
from engine import Engine
from frame import Frame
from graphics.icon_button import IconButton
from graphics.asset_loader import loader
from input_sequences.event import Input
from sequencer.constants import MARGIN_LEFT, PIXELS_PER_BEAT, TOP_MARGIN
from sequencer.engine_playback_manager import EnginePlaybackManager
from sequencer.track import Event, Track, TrackColor
from utils import exp_decay

class Sequencer(Frame):
    tracks: list[Track]
    
    playing_direction: float
    
    scroll_target_x: float
    "In beats."
    scroll_position_x: float
    "In beats."
    current_position: float
    "In beats."
    
    dragging_playhead: bool
    old_beat: int
    
    time_per_beat: float
    max_length: int
    "In beats."
    
    playback_manager: EnginePlaybackManager
    
    def __init__(self, pos: tuple[int, int, int, int], engine_width: int) -> None:
        super().__init__(pos)
        
        self.engine_width = engine_width
        
        self.title_text = loader.get_font(16).render("Sequencer", True, "white")
        self.play_pause_icon = self.add(IconButton("play_icon.png", self.play_pressed))
        self.rewind_icon = self.add(IconButton("rewind_icon.png", self.rewind_pressed))
        self.fast_forward_icon = self.add(IconButton("fast_forward_icon.png", self.fast_forward_pressed))
        
        self.tracks = [
            self.add(Track([Event(time=0, duration=3, inputs=[Input.Right, Input.Empty, Input.Right]), Event(time=3, duration=1, inputs=[Input.Right])], "A", TrackColor("#995555", "#553333", "#995555"), 11)),
            self.add(Track([Event(time=0, duration=3, inputs=[Input.Wait, Input.Empty, Input.CycleItem]), Event(time=4, duration=3, inputs=[Input.Right, Input.Empty, Input.Down])], "B", TrackColor("#559955", "#335533", "#559955"), 7)),
            self.add(Track([Event(time=0, duration=3, inputs=[Input.Right, Input.Empty, Input.UseItem]), Event(time=4, duration=1, inputs=[Input.Right])], "C", TrackColor("#555599", "#333355", "#555599"), 5))
        ]

        self.playing_direction = 0.0
        
        self.scroll_target_x = 0.0
        self.scroll_position_x = 0.0
        self.current_position = 0.0
        
        self.dragging_playhead = False
        self.old_beat = 0
        
        self.time_per_beat = 0.5
        self.max_length = int(60 / self.time_per_beat)
        
        self.playback_manager = EnginePlaybackManager()
    
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
        
        time_text = loader.get_font(16).render(f"{self.format_seconds(self.current_position * self.time_per_beat)} / {self.format_seconds(self.max_length * self.time_per_beat)}", True, "white")
        self.window.blit(time_text, (self.window.width - self.engine_width + 10, 10))
        
        playback_rate_text = loader.get_font(16).render(f"Playback rate: {self.playing_direction:.1f}x", True, "white")
        self.window.blit(playback_rate_text, (self.window.width - playback_rate_text.width - 10, 10))
        
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

    def update(self, engine: Engine, delta: float):
        self.scroll_position_x = exp_decay(self.scroll_position_x, self.scroll_target_x, 15, delta)
        
        if self.dragging_playhead:
            mouse_x = pygame.mouse.get_pos()[0] - self.rect.x
            self.current_position = (mouse_x - MARGIN_LEFT) / PIXELS_PER_BEAT + self.scroll_position_x
            self.current_position = max(0, self.current_position)
        
        for track in self.tracks:
            track.update(delta)
        
        if self.playing_direction != 0:
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

        beat: int = math.floor(self.current_position)
        if beat != self.old_beat:
            self.old_beat = beat
            self.playback_manager.check_inputs(beat, engine, self.tracks)
    
    def mouse_over_playhead(self, mouse: tuple[int, int]) -> bool:
        playhead_position = (self.current_position - self.scroll_position_x) * PIXELS_PER_BEAT + MARGIN_LEFT
        padding = 4
        return (playhead_position - 1 - padding <= mouse[0] <= playhead_position + 1 + padding) and \
            (32 <= mouse[1] <= self.window.height) or \
            (32 <= mouse[1] <= 48) or \
            (self.window.height - 16 <= mouse[1] <= self.window.height)
    
    def on_mouse_down(self, mouse: tuple[int, int]):
        if self.mouse_over_playhead(mouse):
            self.dragging_playhead = True
            return
        
        return super().on_mouse_down(mouse)

    def on_mouse_up(self, mouse: tuple[int, int]):
        if self.dragging_playhead:
            self.dragging_playhead = False
        
        return super().on_mouse_up(mouse)
    
    def on_mouse_move(self, mouse):
        if self.mouse_over_playhead(mouse):
            super().on_mouse_move((0, 0))
            return pygame.SYSTEM_CURSOR_SIZEWE

        if self.dragging_playhead:
            return
        
        return super().on_mouse_move(mouse)
    
    def on_scroll(self, y: int):
        self.scroll_target_x -= y
        self.scroll_target_x = max(0, self.scroll_target_x)