import pygame


class Sequencer:
    def __init__(self, size: tuple[int, int]) -> None:
        self.window = pygame.Surface(size)
        
        self.tracks = [
            "R...R...R...R...",
            "D..D.",
        ]

        self.current_beat: int = 0
        self.beat_timer: float = 0.0
        self.time_per_beat: float = 0.25
        
    def resize(self, width, height):
        self.window = pygame.Surface((width, height))

    def draw(self):
        self.window.fill("#222222")

    def update(self, delta):
        self.beat_timer += delta
        if self.beat_timer >= self.time_per_beat:
            self.beat_timer -= self.time_per_beat

            self.current_beat += 1