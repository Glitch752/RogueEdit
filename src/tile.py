import random

class Tile:
    solid = False
    def __init__(self, x: int, y: int, solid: bool, index: int) -> None:
        self.x = x
        self.y = y
        self.solid = solid
        self.index = index
    
class EmptyTile(Tile):
    def __init__(self, x: int, y: int) -> None:
        super().__init__(x, y, False, random.randint(68, 69))