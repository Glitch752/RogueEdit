from dataclasses import dataclass
import pygame
import random
from typing import Optional

random.seed(69)

from tile import *
from entity import *
from utils import clamp

from copy import deepcopy

TILES_PER_ROW = 16
TILE_WIDTH = 8
TILE_HEIGHT = 8
GRID_WIDTH = 32
GRID_HEIGHT = 18

@dataclass
class EngineState:
    entities: dict[UUID, Entity]

class Engine:
    entities: dict[UUID, Entity]
    
    def __init__(self, tilemap: pygame.Surface, width=GRID_WIDTH, height=GRID_HEIGHT) -> None:
        self.world_width, self.world_height = width, height
        self.tilemap = tilemap

        self.window = pygame.Surface((GRID_WIDTH * TILE_WIDTH, GRID_HEIGHT * TILE_HEIGHT))
        self.world = [[EmptyTile(x, y) for x in range(self.world_width)] for y in range(self.world_height)]
        self.entities = dict()
        self.player: Optional[Entity] = None

        self.camera_x: float = 0
        self.camera_y: float = 0
    
    def export_state(self) -> EngineState:
        return EngineState({e.id: deepcopy(e) for e in self.entities.values()})
    
    def import_state(self, state: EngineState):
        for entity in self.entities.values():
            if not entity.id in state.entities:
                del self.entities[entity.id]
        
        for entity in state.entities.values():
            if entity.id in self.entities:
                curr = self.entities[entity.id]
                curr.import_state_from(entity)
            else:
                self.entities.update({entity.id: entity})
        
        for entity in state.entities:
            if isinstance(entity, PlayerEntity):
                self.player = entity
                break

    def move_player(self, dx: int, dy: int):
        if self.player == None:
            return
        
        self.player.move(self, dx, dy)

        for entity in filter(lambda e: isinstance(e, EnemyEntity), self.entities.values()):
            entity.on_my_turn(self, self.player.x, self.player.y)

    def draw_tile(self, x: float, y: float, tile_index: int):
        i = tile_index % TILES_PER_ROW
        j = tile_index // TILES_PER_ROW
        self.window.blit(self.tilemap.subsurface(i * TILE_WIDTH, j * TILE_HEIGHT, TILE_WIDTH, TILE_HEIGHT), (x * TILE_WIDTH, y * TILE_HEIGHT))
    
    def update(self, delta: float):
        for entity in self.entities.values():
            entity.update(delta)
        if self.player is not None:
            self.camera_x = -GRID_WIDTH // 2 + self.player.show_x
            self.camera_x = clamp(self.camera_x, 0, self.world_width - GRID_WIDTH)
            self.camera_y = -GRID_HEIGHT // 2 + self.player.show_y
            self.camera_y = clamp(self.camera_y, 0, self.world_height - GRID_HEIGHT)

    def draw(self):
        self.window.fill('black')

        for x in range(self.world_width):
            for y in range(self.world_height):
                self.world[y][x].draw(self)

        for i, entity in enumerate(self.entities.values()):
            tile_idx = entity.tile_id
            if i == 0 and entity.health <= 0:
                tile_idx = 25 # ghost tile
            self.draw_tile(entity.show_x - self.camera_x, entity.show_y - self.camera_y, tile_idx)
        
        # HUD
        if self.player is not None:
            for x in range(self.player.health):
                self.draw_tile(x * 1.5 + 0.5, 0.5, 102)
            for x in range(self.player.max_health - self.player.health):
                self.draw_tile((self.player.health + x) * 1.5 + 0.5, 0.5, 100)