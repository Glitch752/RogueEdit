import random

class Tile:
    solid = False
    def __init__(self, x: int, y: int, solid: bool, index: int) -> None:
        self.x = x
        self.y = y
        self.solid = solid
        self.index = index
    
    def draw(self, engine):
        engine.draw_tile(self.x - engine.camera_x, self.y - engine.camera_y, self.index)
    
class EmptyTile(Tile):
    def __init__(self, x: int, y: int) -> None:
        super().__init__(x, y, False, random.randint(68, 69))

class WallTile(Tile):
    def __init__(self, x: int, y: int) -> None:
        super().__init__(x, y, True, 1)

class LeftVerticalWallTile(Tile):
    def __init__(self, x: int, y: int) -> None:
        super().__init__(x, y, True, 16)

class RightVerticalWallTile(Tile):
    def __init__(self, x: int, y: int) -> None:
        super().__init__(x, y, True, 19)

class CornerLeftTile(Tile):
    def __init__(self, x: int, y: int) -> None:
        super().__init__(x, y, True, 0)

class CornerRightTile(Tile):
    def __init__(self, x: int, y: int) -> None:
        super().__init__(x, y, True, 3)