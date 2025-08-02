from dataclasses import dataclass
import math
from typing import Optional
import pygame
from engine import Engine
from frame import Frame
from graphics.icon_button import IconButton
from graphics.asset_loader import loader
from input_sequences.event import EventVisualizer
from input_sequences.input_sequences import EventSelector
from sequencer.constants import MARGIN_LEFT, PIXELS_PER_BEAT, SECONDS_PER_BEAT, TOP_MARGIN
from sequencer.engine_playback_manager import EnginePlaybackManager
from sequencer.track import Event, Track, TrackColor
from utils import exp_decay, format_seconds

TRACK_SPACING = 64

@dataclass
class DropTarget:
    """The target for a dropped event."""
    track: int
    time: int
    "In beats."
    is_valid: bool

@dataclass
class TimelinePosition:
    """Any position on the timeline"""
    track: int
    time: float
    
@dataclass
class DroppingState:
    indicator_pos: TimelinePosition
    visualizer: EventSelector
    target: DropTarget

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
    
    max_length: int
    "In beats."
    
    playback_manager: EnginePlaybackManager
    drop_state: Optional[DroppingState]
    
    def __init__(self, pos: tuple[int, int, int, int], engine_width: int) -> None:
        super().__init__(pos)
        
        self.engine_width = engine_width
        
        self.title_text = loader.get_font(16).render("Sequencer", True, "white")
        self.play_pause_icon = self.add(IconButton("play_icon.png", self.play_pressed))
        self.rewind_icon = self.add(IconButton("rewind_icon.png", self.rewind_pressed))
        self.fast_forward_icon = self.add(IconButton("fast_forward_icon.png", self.fast_forward_pressed))
        
        self.tracks = [
            self.add(Track([], "A", TrackColor("#995555", "#553333", "#995555"), 11)),
            self.add(Track([], "B", TrackColor("#559955", "#335533", "#559955"), 7)),
            self.add(Track([], "C", TrackColor("#555599", "#333355", "#555599"), 5))
        ]

        self.playing_direction = 0.0
        
        self.scroll_target_x = 0.0
        self.scroll_position_x = 0.0
        self.current_position = 0.0
        
        self.dragging_playhead = False
        self.old_beat = 0
        
        self.max_length = int(60 / SECONDS_PER_BEAT)
        
        self.playback_manager = EnginePlaybackManager()
        self.drop_state = None
    
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

    def draw(self, surface: pygame.Surface):
        self.window.fill("#222222")
        pygame.draw.rect(self.window, "#333333", (0, 0, self.window.width, 32))
        self.window.blit(self.title_text, (10, 10))
        
        icon_center = self.window.width - self.engine_width // 2
        self.play_pause_icon.draw(self.window, (icon_center - 16, 0))
        self.rewind_icon.draw(self.window, (icon_center - 64, 0))
        self.fast_forward_icon.draw(self.window, (icon_center + 32, 0))
        
        time_text = loader.get_font(16).render(f"{format_seconds(self.current_position * SECONDS_PER_BEAT)} / {format_seconds(self.max_length * SECONDS_PER_BEAT)}", True, "white")
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
                time_text = loader.get_font(12).render(f"{format_seconds(i * SECONDS_PER_BEAT)}", True, "#aaaaaa")
                self.window.blit(time_text, (x + 4, 44))
        
        
        for i, track in enumerate(self.tracks):
            track.draw(self.window, 32 + TOP_MARGIN + i * TRACK_SPACING, self.scroll_position_x)
        
        # Draw drop target indicator when dragging
        if self.drop_state != None:
            indicator_pos = self.drop_state.indicator_pos
            target = self.drop_state.target
            track = self.tracks[indicator_pos.track]
            
            drop_y = 32 + TOP_MARGIN + indicator_pos.track * TRACK_SPACING
            
            indicator_x = (indicator_pos.time - self.scroll_position_x) * PIXELS_PER_BEAT + MARGIN_LEFT
            pygame.draw.rect(self.window, track.color.title, (indicator_x - 2, drop_y, 4, 48), 0, 2)
            pygame.draw.circle(self.window, track.color.title, (int(indicator_x), drop_y + 24), 6, 2)
            
            start_idx = math.floor(self.scroll_position_x / track.repeat_length)
            end_idx = math.ceil((self.scroll_position_x + surface.width / PIXELS_PER_BEAT) / track.repeat_length)
        
            for i in range(start_idx, end_idx + 1):
                drop_x = int(
                    MARGIN_LEFT + (target.time - self.scroll_position_x) * PIXELS_PER_BEAT +\
                    i * track.repeat_length * PIXELS_PER_BEAT
                )
                # Draw a preview of the event being dropped
                self.drop_state.visualizer.draw_ghost(
                    self.window,
                    drop_x, drop_y, 0.5 if target.is_valid else 0.2,
                    track.color.repeat_background if i > 0 else track.color.background
                )
        
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
            self.current_position += delta / SECONDS_PER_BEAT * self.playing_direction
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
    
    def get_drop_target(self, mouse: tuple[int, int]) -> Optional[TimelinePosition]:
        if mouse[1] < 32 + TOP_MARGIN:
            return None
        
        track_index = (mouse[1] - 32 - TOP_MARGIN) // TRACK_SPACING
        if track_index < 0 or track_index >= len(self.tracks):
            return None
        
        track = self.tracks[track_index]
        
        time_position = (mouse[0] - MARGIN_LEFT) / PIXELS_PER_BEAT + self.scroll_position_x
        time_position = max(0, time_position) % track.repeat_length
        
        return TimelinePosition(track_index, time_position)
    
    def get_event_drop_position(self, indicator: TimelinePosition, event: Event, drag_offset: tuple[int, int]) -> DropTarget:
        track = self.tracks[indicator.track]
        time_position = indicator.time - drag_offset[0] / PIXELS_PER_BEAT
        
        # Clamp to the track
        time_position = round(max(0, min(time_position, track.repeat_length - event.duration)))
        
        is_valid = True
        for existing_event in track.events:
            if not (time_position + event.duration <= existing_event.time or time_position >= existing_event.time + existing_event.duration):
                is_valid = False
                break
        
        return DropTarget(
            track=indicator.track,
            time=int(time_position),
            is_valid=is_valid
        )
    
    def drop(self) -> bool:
        """Returns if the drop was successful"""
        if self.drop_state == None:
            return False
        
        target = self.drop_state.target
        event = self.drop_state.visualizer.event
        
        self.drop_state = None
        
        if not target.is_valid:
            return False

        
        track = self.tracks[target.track]
        
        new_event = Event(
            time=target.time,
            duration=event.duration,
            inputs=event.inputs.copy()
        )
        
        # Insert the event in the correct position
        inserted = False
        for i, existing_event in enumerate(track.events):
            if existing_event.time > new_event.time:
                track.events.insert(i, new_event)
                track.visualizers.insert(i, EventVisualizer(new_event))
                inserted = True
                break
        
        if not inserted:
            track.events.append(new_event)
            track.visualizers.append(EventVisualizer(new_event))
        
        return True
    
    def update_drop_target(self, mouse: tuple[int, int], visualizer: EventSelector):
        """Update the drop target visualization"""
        target = self.get_drop_target(mouse)
        if target == None:
            self.drop_state = None
        else:
            self.drop_state = DroppingState(
                target,
                visualizer,
                self.get_event_drop_position(target, visualizer.event, visualizer.drag_offset)
            )