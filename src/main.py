import pygame

from engine import Engine
from sequencer import Sequencer
from input_sequences import InputSequences

pygame.init()

WIN = pygame.display.set_mode((1280, 720), pygame.RESIZABLE)

TILEMAP = pygame.image.load("kenney_micro-roguelike/colored_tilemap_packed.png").convert_alpha()

def main():
    delta: float = 0.0
    clock: pygame.time.Clock = pygame.time.Clock()

    width, height = WIN.get_size()

    engine = Engine(TILEMAP)
    engine_scale = 3
    engine_width = engine.window.get_width() * engine_scale
    engine_height = engine.window.get_height() * engine_scale
    sequencer = Sequencer((0, engine_height, width, height - engine_height), engine_width)
    input_sequences = InputSequences((0, 0, width - engine_width, engine_height))

    running: bool = True
    
    while running:
        delta = clock.tick_busy_loop(60.0) / 1000.0

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.VIDEORESIZE:
                width, height = event.w, event.h
                sequencer.resize(width, height - engine.window.get_height() * engine_scale)
                input_sequences.resize(width - engine.window.get_width() * engine_scale, engine.window.get_height() * engine_scale)
            elif event.type == pygame.MOUSEMOTION:
                sequencer.on_mouse_move()
                input_sequences.on_mouse_move()
            elif event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:
                    sequencer.on_click()
                    input_sequences.on_click()
        
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
