from tile import *

class Entity:
    def __init__(self, engine, x: int, y: int, tile_index: int) -> None:
        self.engine = engine
        self.x = x
        self.y = y
        self.tile_id = tile_index

    def move(self, dx: int, dy: int):
        self.x += dx
        self.y += dy
        if 0 > self.x >= len(self.engine[0]) or 0 > self.y >= len(self.engine):
            self.x -= dx
            self.y -= dy
        elif self.engine.world[self.y][self.x].solid:
            self.x -= dx
            self.y -= dy
            
class PlayerEntity(Entity):
    def __init__(self, x: int, y: int) -> None:
        self.x = x
        self.y = y
        self.tile_id = 5