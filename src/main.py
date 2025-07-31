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
WIN = pygame.display.set_mode((1280, 720), pygame.RESIZABLE)

TILEMAP = pygame.image.load("kenney_micro-roguelike/colored_tilemap_packed.png").convert_alpha()

def main():
    global WIN
    
    delta: float = 0.0
    clock: pygame.time.Clock = pygame.time.Clock()

    width, height = WIN.get_size()

    current_puzzle: int = 0
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
                width = max(event.w, MIN_WIDTH)
                height = max(event.h, MIN_HEIGHT)
                sequencer.resize(width, height - engine.window.height * engine_scale)
                input_sequences.resize(width - engine.window.width * engine_scale, engine.window.height * engine_scale)
                if width != event.w or height != event.h:
                    WIN = pygame.display.set_mode((width, height), pygame.RESIZABLE)
            elif event.type == pygame.MOUSEMOTION:
                cursor_set: Optional[pygame.Cursor | int] = None
                mouse = pygame.mouse.get_pos()
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
                    for frame in frames:
                        if frame.mouse_over():
                            mouse = pygame.mouse.get_pos()
                            frame.on_mouse_down((mouse[0] - frame.rect.x, mouse[1] - frame.rect.y))
            elif event.type == pygame.MOUSEBUTTONUP:
                if event.button == 1:
                    for frame in frames:
                        mouse = pygame.mouse.get_pos()
                        frame.on_mouse_up((mouse[0] - frame.rect.x, mouse[1] - frame.rect.y))
            elif event.type == pygame.MOUSEWHEEL:
                for frame in frames:
                    if frame.mouse_over():
                        frame.on_scroll(event.y)
        
        engine.update(delta)
        sequencer.update(engine, delta)

        WIN.fill('white')

        engine.draw()
        sequencer.draw(WIN)
        input_sequences.draw(WIN)
        
        WIN.blit(pygame.transform.scale(engine.window, (engine_width, engine_height)), (width - engine_width, 0))

        pygame.display.flip()
    
    pygame.quit()

if __name__ == "__main__":
    main()
