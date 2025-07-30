import random

class Tile:
    def __init__(self, x: int, y: int, index: int) -> None:
        self.x = x
        self.y = y
        self.index = index

class EmptyTile(Tile):
    def __init__(self, x: int, y: int) -> None:
        super().__init__(x, y, random.randint(68, 69))