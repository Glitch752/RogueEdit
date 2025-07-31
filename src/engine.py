import pygame

from tile import *
from entity import *

TILES_PER_ROW = 16
TILE_WIDTH = 8
TILE_HEIGHT = 8
GRID_WIDTH = 32
GRID_HEIGHT = 18

class Engine:
    def __init__(self, tilemap: pygame.Surface) -> None:
        self.tilemap = tilemap

        self.window = pygame.Surface((GRID_WIDTH * TILE_WIDTH, GRID_HEIGHT * TILE_HEIGHT))
        self.world = [[EmptyTile(x, y) for x in range(GRID_WIDTH)] for y in range(GRID_HEIGHT)]
        self.entities = [PlayerEntity(self, 0, GRID_HEIGHT // 2)]

    def move_player(self, dx: int, dy: int):
        self.entities[0].move(dx, dy)

    def draw_tile(self, x, y, tile_index):
        i = tile_index % TILES_PER_ROW
        j = tile_index // TILES_PER_ROW
        self.window.blit(self.tilemap.subsurface(i * TILE_WIDTH, j * TILE_HEIGHT, TILE_WIDTH, TILE_HEIGHT), (x * TILE_WIDTH, y * TILE_HEIGHT))
    
    def update(self, delta: float):
        for entity in self.entities:
            entity.update(delta)

    def draw(self):
        for x in range(GRID_WIDTH):
            for y in range(GRID_HEIGHT):
                self.draw_tile(x, y, self.world[y][x].index)
        
        for entity in self.entities:
            self.draw_tile(entity.show_x, entity.show_y, entity.tile_id)