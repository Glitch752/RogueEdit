import pygame

pygame.init()

WIDTH, HEIGHT = (1280, 720)
WIN = pygame.display.set_mode((WIDTH, HEIGHT))

FONT = pygame.font.SysFont("Courier", 24)

def main():
    delta: float = 0.0
    clock: pygame.time.Clock = pygame.time.Clock()

    running: bool = True
    
    while running:
        delta = clock.tick_busy_loop(60.0) / 1000.0

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
        
        WIN.fill('white')

        WIN.blit(t := FONT.render("keep yourself safe <3", True, 'black'), (WIDTH // 2 - t.get_width() // 2, HEIGHT // 2 - t.get_height() // 2))

        pygame.display.flip()
    
    pygame.quit()

if __name__ == "__main__":
    main()
