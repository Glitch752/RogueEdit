import numpy as np
from tcod import path
from tile import *
from utils import exp_decay

def lerp(a, b, t): return a + (b - a) * t

class Entity:
    def __init__(self, engine, x: int, y: int, tile_index: int, health: int = 999) -> None:
        self.engine = engine
        self.x = x
        self.y = y
        self.show_x = x
        self.show_y = y
        self.tile_id = tile_index
        self.health = self.max_health = health

    def on_my_turn(self, target_x: int, target_y: int):
        # i hate this but it gets liveshare to shut the fuck up
        pass

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
        self.show_x = exp_decay(self.show_x, self.x, 10, delta)
        self.show_y = exp_decay(self.show_y, self.y, 10, delta)

class PlayerEntity(Entity):
    def __init__(self, engine, x: int, y: int) -> None:
        super().__init__(engine, x, y, 5, 3)

class EnemyEntity(Entity):
    def __init__(self, engine, x: int, y: int, index: int) -> None:
        super().__init__(engine, x, y, index, 1)

    def on_my_turn(self, target_x: int, target_y: int):
        solids = [[not self.engine.world[y][x].solid for x in range(self.engine.world_width)] for y in range(self.engine.world_height)]

        solids = np.transpose(solids, (1, 0))

        graph = path.SimpleGraph(cost=solids, cardinal=1, diagonal=0)
        
        finder = path.Pathfinder(graph)
        finder.add_root((self.x, self.y))
        
        new_path = finder.path_to((target_x, target_y))
        new_path = new_path.tolist()[1:-1]

        if len(new_path):
            dx: int = new_path[0][0] - self.x
            dy: int = new_path[0][1] - self.y

            self.move(dx, dy)
        elif len(self.engine.entities) and isinstance(self.engine.entities[0], PlayerEntity):
            # ATTACK!
            player = self.engine.entities[0]
            player.health = max(player.health - 1, 0)
            pass

class SnakeEntity(EnemyEntity):
    def __init__(self, engine, x: int, y: int) -> None:
        super().__init__(engine, x, y, 20)

class RatEntity(EnemyEntity):
    def __init__(self, engine, x: int, y: int) -> None:
        super().__init__(engine, x, y, 22)