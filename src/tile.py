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
        super().__init__(x, y, False, random.randint(10, 13))

class WallTile(Tile):
    def __init__(self, x: int, y: int) -> None:
        super().__init__(x, y, True, 20)

class BackWallTile(Tile):
    def __init__(self, x: int, y: int) -> None:
        super().__init__(x, y, True, 2)

class LeftVerticalWallTile(Tile):
    def __init__(self, x: int, y: int) -> None:
        super().__init__(x, y, True, 9)

class RightVerticalWallTile(Tile):
    def __init__(self, x: int, y: int) -> None:
        super().__init__(x, y, True, 14)

class FrontCornerLeftTile(Tile):
    def __init__(self, x: int, y: int) -> None:
        super().__init__(x, y, True, 18)

class FrontCornerRightTile(Tile):
    def __init__(self, x: int, y: int) -> None:
        super().__init__(x, y, True, 23)

class BackCornerLeftTile(Tile):
    def __init__(self, x: int, y: int) -> None:
        super().__init__(x, y, True, 0)

class BackCornerRightTile(Tile):
    def __init__(self, x: int, y: int) -> None:
        super().__init__(x, y, True, 5)
