import numpy as np
from tcod import path
import typing
if typing.TYPE_CHECKING:
    from engine import Engine
from tile import *
from utils import exp_decay
from uuid import UUID, uuid4

def lerp(a, b, t): return a + (b - a) * t

class Entity:
    id: UUID
    
    def __init__(self, x: int, y: int, tile_index: int, health: int = 999) -> None:
        self.id = uuid4()
        self.x = x
        self.y = y
        self.show_x = x
        self.show_y = y
        self.tile_id = tile_index
        self.health = self.max_health = health
        self.marked_for_death = False

    def on_my_turn(self, engine: "Engine", target_x: int, target_y: int):
        # i hate this but it gets liveshare to shut the fuck up
        pass

    def move(self, engine: "Engine", dx: int, dy: int):
        # returns the entity that gets collided with on move
        self.x += dx
        self.y += dy
        try:
            if engine.world[self.y][self.x].solid:
                self.x -= dx
                self.y -= dy
            else:
                for entity in engine.entities.values():
                    if entity is not self and entity.x == self.x and entity.y == self.y:
                        if isinstance(entity, DoorEntity) and entity.open:
                            continue
                        self.x -= dx
                        self.y -= dy
                        return entity
        except IndexError:
            self.x -= dx
            self.y -= dy
        return None

    def update(self, delta: float) -> None:
        self.show_x = exp_decay(self.show_x, self.x, 10, delta)
        self.show_y = exp_decay(self.show_y, self.y, 10, delta)
    
    def import_state_from(self, other: "Entity"):
        self.x = other.x
        self.y = other.y
        self.health = other.health

class PlayerEntity(Entity):
    def __init__(self, x: int, y: int) -> None:
        super().__init__(x, y, 17, 3)

class EnemyEntity(Entity):
    def __init__(self, x: int, y: int, index: int) -> None:
        super().__init__(x, y, index, 1)

    def on_my_turn(self, engine: "Engine", target_x: int, target_y: int):
        solids = [[not engine.world[y][x].solid for x in range(engine.world_width)] for y in range(engine.world_height)]

        solids = np.transpose(solids, (1, 0))

        graph = path.SimpleGraph(cost=solids, cardinal=1, diagonal=0)
        
        finder = path.Pathfinder(graph)
        finder.add_root((self.x, self.y))
        
        new_path = finder.path_to((target_x, target_y))
        new_path = new_path.tolist()[1:-1]

        if len(new_path):
            dx: int = new_path[0][0] - self.x
            dy: int = new_path[0][1] - self.y

            self.move(engine, dx, dy)
        elif engine.player:
            # ATTACK!
            player = engine.player
            player.health = max(player.health - 1, 0)
            pass

class SnakeEntity(EnemyEntity):
    def __init__(self, x: int, y: int) -> None:
        super().__init__(x, y, 8)

class RatEntity(EnemyEntity):
    def __init__(self, x: int, y: int) -> None:
        super().__init__(x, y, 6)

class KeyEntity(Entity):
    def __init__(self, x: int, y: int) -> None:
        super().__init__(x, y, 26)

class ExitEntity(Entity):
    def __init__(self, x: int, y: int) -> None:
        super().__init__(x, y, 35)

class DoorEntity(Entity):
    def __init__(self, x: int, y: int) -> None:
        super().__init__(x, y, 22)
        self.open = False

    def open_door(self):
        self.open = True
        self.tile_id = 21