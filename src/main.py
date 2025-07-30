import pygame

from engine import Engine
from sequencer import Sequencer

pygame.init()

WIN = pygame.display.set_mode((1280, 720), pygame.RESIZABLE)

FONT = pygame.font.SysFont("Courier", 24)

TILEMAP = pygame.image.load("kenney_micro-roguelike/colored_tilemap_packed.png").convert_alpha()

def main():
    delta: float = 0.0
    clock: pygame.time.Clock = pygame.time.Clock()

    width, height = WIN.get_size()

    engine = Engine(TILEMAP)
    engine_scale = 3
    sequencer = Sequencer((width, height - engine.window.get_height() * engine_scale))

    running: bool = True
    
    while running:
        delta = clock.tick_busy_loop(60.0) / 1000.0

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.VIDEORESIZE:
                width, height = event.w, event.h
                sequencer.resize(width, height - engine.window.get_height() * engine_scale)
        
        WIN.fill('white')

        engine.draw()
        sequencer.draw()

        engine_width = engine.window.get_width() * engine_scale
        engine_height = engine.window.get_height() * engine_scale
        WIN.blit(pygame.transform.scale(engine.window, (engine_width, engine_height)), (width - engine_width, 0))
        WIN.blit(sequencer.window, (0, engine_height))

        pygame.display.flip()
    
    pygame.quit()

if __name__ == "__main__":
    main()
