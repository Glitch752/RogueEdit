from typing import Optional
import pygame

from engine import Engine
from frame import Frame
from sequencer.sequencer import Sequencer
from input_sequences.input_sequences import InputSequences
from puzzle import puzzles

pygame.init()

MIN_WIDTH = 1280
MIN_HEIGHT = 720
WIN = pygame.Window(size=(1280, 720), resizable=True)
WIN.minimum_size = (MIN_WIDTH, MIN_HEIGHT)
WIN_SURFACE = WIN.get_surface()

TILEMAP = pygame.image.load("assets/tilemap.png").convert_alpha()

def main():
    delta: float = 0.0
    clock: pygame.time.Clock = pygame.time.Clock()

    width, height = WIN.size

    current_puzzle: int = 1
    engine = puzzles[current_puzzle].make_engine(TILEMAP)
    engine_scale = 3
    engine_width = engine.window.width * engine_scale
    engine_height = engine.window.height * engine_scale
    sequencer = Sequencer((0, engine_height, width, height - engine_height), engine_width)
    input_sequences = InputSequences((0, 0, width - engine_width, engine_height))
    
    frames: list[Frame] = [sequencer, input_sequences]

    running: bool = True
    
    while running:
        delta = clock.tick_busy_loop(60.0) / 1000.0

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
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
        
        engine.update(delta)
        sequencer.update(engine, delta)
        input_sequences.update(delta)

        WIN_SURFACE.fill('white')

        engine.draw()
        sequencer.draw(WIN_SURFACE)
        input_sequences.draw(WIN_SURFACE)
        
        WIN_SURFACE.blit(pygame.transform.scale(engine.window, (engine_width, engine_height)), (width - engine_width, 0))
        
        WIN.flip()
    
    pygame.quit()

if __name__ == "__main__":
    main()
