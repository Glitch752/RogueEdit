from tile import *

def lerp(a, b, t): return a + (b - a) * t

class Entity:
    def __init__(self, engine, x: int, y: int, tile_index: int) -> None:
        self.engine = engine
        self.x = x
        self.y = y
        self.show_x = x
        self.show_y = y
        self.tile_id = tile_index

    def move(self, dx: int, dy: int):
        self.x += dx
        self.y += dy
        try:
            if self.engine.world[self.y][self.x].solid:
                self.x -= dx
                self.y -= dy
        except IndexError:
            self.x -= dx
            self.y -= dy

    def update(self, delta: float) -> None:
        self.show_x = lerp(self.show_x, self.x, 0.1)
        self.show_y = lerp(self.show_y, self.y, 0.1)

class PlayerEntity(Entity):
    def __init__(self, engine, x: int, y: int) -> None:
        super().__init__(engine, x, y, 5)