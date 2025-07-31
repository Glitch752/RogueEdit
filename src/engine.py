import pygame
import random

random.seed(69)

from tile import *
from entity import *
from utils import clamp

TILES_PER_ROW = 16
TILE_WIDTH = 8
TILE_HEIGHT = 8
GRID_WIDTH = 32
GRID_HEIGHT = 18

class Engine:
    def __init__(self, tilemap: pygame.Surface, width=GRID_WIDTH, height=GRID_HEIGHT) -> None:
        self.world_width, self.world_height = width, height
        self.tilemap = tilemap

        self.window = pygame.Surface((GRID_WIDTH * TILE_WIDTH, GRID_HEIGHT * TILE_HEIGHT))
        self.world = [[EmptyTile(x, y) for x in range(self.world_width)] for y in range(self.world_height)]
        self.entities: list[Entity] = []

        self.camera_x: float = 0
        self.camera_y: float = 0

    def move_player(self, dx: int, dy: int):
        self.entities[0].move(dx, dy)

        for entity in filter(lambda e: isinstance(e, EnemyEntity), self.entities):
            entity.on_my_turn(self.entities[0].x, self.entities[0].y)

    def draw_tile(self, x: float, y: float, tile_index: int):
        i = tile_index % TILES_PER_ROW
        j = tile_index // TILES_PER_ROW
        self.window.blit(self.tilemap.subsurface(i * TILE_WIDTH, j * TILE_HEIGHT, TILE_WIDTH, TILE_HEIGHT), (x * TILE_WIDTH, y * TILE_HEIGHT))
    
    def update(self, delta: float):
        for entity in self.entities:
            entity.update(delta)
        if len(self.entities):
            self.camera_x = -GRID_WIDTH // 2 + self.entities[0].show_x
            self.camera_x = clamp(self.camera_x, 0, self.world_width - GRID_WIDTH)
            self.camera_y = -GRID_HEIGHT // 2 + self.entities[0].show_y
            self.camera_y = clamp(self.camera_y, 0, self.world_height - GRID_HEIGHT)

    def draw(self):
        self.window.fill('black')

        for x in range(self.world_width):
            for y in range(self.world_height):
                self.world[y][x].draw(self)

        for i, entity in enumerate(self.entities):
            tile_idx = entity.tile_id
            if i == 0 and entity.health <= 0:
                tile_idx = 25 # ghost tile
            self.draw_tile(entity.show_x - self.camera_x, entity.show_y - self.camera_y, tile_idx)
        
        # HUD
        if len(self.entities) and isinstance(self.entities[0], PlayerEntity):
            for x in range(self.entities[0].health):
                self.draw_tile(x * 1.5 + 0.5, 0.5, 102)
            for x in range(self.entities[0].max_health - self.entities[0].health):
                self.draw_tile((self.entities[0].health + x) * 1.5 + 0.5, 0.5, 100)