import platform
import pygame

from utils import is_web

if platform.system() == "Windows":
    import ctypes
    ctypes.windll.user32.SetProcessDPIAware()

pygame.mixer.pre_init(44100, -16, 2, 512)
pygame.init()

from typing import TYPE_CHECKING, Optional

from dialogue import DialogueManager, DialogueType
from frame import Frame
from sequencer.sequencer import Sequencer
from puzzle import puzzles
from audio import SoundType, audio_manager

MIN_WIDTH = 1280
MIN_HEIGHT = 720
if is_web():
    WIN_SURFACE = pygame.display.set_mode((1280, 720))
else:
    WIN = pygame.Window(size=(1280, 720), resizable=True)
    WIN.minimum_size = (MIN_WIDTH, MIN_HEIGHT)
    WIN_SURFACE = WIN.get_surface()

TILEMAP = pygame.image.load("assets/tilemap.png").convert_alpha()

def main():
    global WIN_SURFACE
    
    delta: float = 0.0
    clock: pygame.time.Clock = pygame.time.Clock()

    running: bool = True

    if is_web():
        width, height = WIN_SURFACE.get_size()
    else:
        width, height = WIN.size

    def advance_puzzle():
        nonlocal current_puzzle, engine, sequencer, input_sequences, running
        current_puzzle += 1
        if current_puzzle >= len(puzzles):
            running = False
        p = puzzles[current_puzzle]
        engine = p.make_engine(TILEMAP)
        p.update(sequencer, engine.export_state(), input_sequences)

    current_puzzle: int = 0
    engine = puzzles[current_puzzle].make_engine(TILEMAP)
    engine_scale = 3
    engine_width = engine.window.width * engine_scale
    engine_height = engine.window.height * engine_scale
    sequencer = Sequencer((0, engine_height, width, height - engine_height), engine_width, engine, advance_puzzle)
    puzzles[current_puzzle].update_sequencer(sequencer)
    input_sequences = puzzles[current_puzzle].make_input_sequences((0, 0, width - engine_width, engine_height))
    dialogue_manager = DialogueManager()
    dialogue_manager.queue_dialogue(DialogueType.INTRO)
    first_complete: bool = False
    had_key_last_frame: bool = False
    
    frames: list[Frame] = [sequencer, input_sequences]

    pygame.mixer.music.load("assets/master_track.ogg")
    pygame.mixer.music.set_volume(0.3)
    pygame.mixer.music.play(-1, fade_ms=500)
    
    def handle_event(event: pygame.Event):
        nonlocal running, width, height
        if event.type == pygame.QUIT:
            running = False
            return
        
        if dialogue_manager.is_shown() and event.type in [pygame.KEYDOWN, pygame.JOYBUTTONDOWN, pygame.MOUSEBUTTONDOWN]:
            dialogue_manager.on_confirm()
            return
        
        elif event.type == pygame.VIDEORESIZE:
            width, height = event.w, event.h
            sequencer.resize(width, height - engine.window.height * engine_scale)
            input_sequences.resize(width - engine.window.width * engine_scale, engine.window.height * engine_scale)
        elif event.type == pygame.MOUSEMOTION:
            cursor_set: Optional[pygame.Cursor | int] = None
            mouse = pygame.mouse.get_pos()
            
            # Handle drag-and-drop; this could be a more modular/clean system, but whatever
            dragged_item = input_sequences.get_dragged_item()
            if dragged_item:
                if sequencer.rect.collidepoint(mouse):
                    sequencer_mouse = (mouse[0] - sequencer.rect.x, mouse[1] - sequencer.rect.y)
                    sequencer.update_drop_target(sequencer_mouse, dragged_item)
                else:
                    sequencer.drop_state = None
            
            for frame in frames:
                (mx, my) = (mouse[0] - frame.rect.x, mouse[1] - frame.rect.y)
                if (c := frame.on_mouse_move((mx, my))) != None:
                    cursor_set = c
            if cursor_set:
                pygame.mouse.set_cursor(cursor_set)
            else:
                pygame.mouse.set_cursor(pygame.SYSTEM_CURSOR_ARROW)
        elif event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == 1:
                mouse = pygame.mouse.get_pos()
                
                # Handle drag-and-drop start
                if sequencer.rect.collidepoint(mouse):
                    sequencer_mouse = (mouse[0] - sequencer.rect.x, mouse[1] - sequencer.rect.y)
                    drag = sequencer.check_drag_start(sequencer_mouse, engine)
                    if drag:
                        if selector := input_sequences.begin_drag(*drag):
                            sequencer.update_drop_target(sequencer_mouse, selector)
                
                for frame in frames:
                    if frame.mouse_over():
                        frame.on_mouse_down((mouse[0] - frame.rect.x, mouse[1] - frame.rect.y))
        elif event.type == pygame.MOUSEBUTTONUP:
            if event.button == 1:
                mouse = pygame.mouse.get_pos()
                
                # Handle drag-and-drop completion
                dragged_item = input_sequences.get_dragged_item()
                if dragged_item and sequencer.rect.collidepoint(mouse):
                    if sequencer.drop(engine):
                        input_sequences.dragged_item_dropped()
                
                for frame in frames:
                    frame.on_mouse_up((mouse[0] - frame.rect.x, mouse[1] - frame.rect.y))
        elif event.type == pygame.MOUSEWHEEL:
            for frame in frames:
                if frame.mouse_over():
                    scroll = event.y
                    if event.x != 0:
                        scroll = -event.x
                    frame.on_scroll(scroll)
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_SPACE:
                sequencer.play_pressed()
    
    while running:
        delta = clock.tick_busy_loop(60.0) / 1000
        delta = min(delta, 1 / 30)

        for event in pygame.event.get():
            handle_event(event)
        
        all_dead = engine.all_enemies_dead()
        sequencer.next_level_icon.shown = all_dead
        if all_dead:
            sequencer.playing_direction = 0.0
            sequencer.update_icons()
            if not first_complete:
                first_complete = True
                dialogue_manager.queue_dialogue(DialogueType.FINISHED_FIRST_LEVEL)
        
        key_exists = engine.key_exists()
        if not key_exists and had_key_last_frame:
            audio_manager.play_sound(SoundType.KEY)
        had_key_last_frame = key_exists
        
        engine.update(delta)
        
        sequencer.update(engine, delta)
        input_sequences.update(delta)
        dialogue_manager.update(delta)

        WIN_SURFACE.fill('white')

        engine.draw()
        sequencer.draw(WIN_SURFACE)
        input_sequences.draw(WIN_SURFACE)
        
        WIN_SURFACE.blit(pygame.transform.scale(engine.window, (engine_width, engine_height)), (width - engine_width, 0))
        
        dialogue_manager.draw(WIN_SURFACE)
        audio_manager.update()
        
        if is_web() and not TYPE_CHECKING:
            from platform import window
            if int(window.innerWidth) != WIN_SURFACE.width or int(window.innerHeight) != WIN_SURFACE.height:
                WIN_SURFACE = pygame.display.set_mode((int(window.innerWidth), int(window.innerHeight)), pygame.RESIZABLE)
        
        WIN.flip()
    
    pygame.quit()

if __name__ == "__main__":
    main()
