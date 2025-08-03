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

class PitTile(Tile):
    def __init__(self, x: int, y: int, index=None) -> None:
        super().__init__(x, y, False, 49 if not index else index)

class BackCornerLeftPitTile(PitTile):
    def __init__(self, x: int, y: int) -> None:
        super().__init__(x, y, 39)

class BackCornerRightPitTile(PitTile):
    def __init__(self, x: int, y: int) -> None:
        super().__init__(x, y, 41)

class FrontCornerRightPitTile(PitTile):
    def __init__(self, x: int, y: int) -> None:
        super().__init__(x, y, 59)

class FrontCornerLeftPitTile(PitTile):
    def __init__(self, x: int, y: int) -> None:
        super().__init__(x, y, 57)

class BackPitTile(PitTile):
    def __init__(self, x: int, y: int) -> None:
        super().__init__(x, y, 40)

class FrontPitTile(PitTile):
    def __init__(self, x: int, y: int) -> None:
        super().__init__(x, y, 58)

class LeftVerticalPitTile(PitTile):
    def __init__(self, x: int, y: int) -> None:
        super().__init__(x, y, 48)

class RightVerticalPitTile(PitTile):
    def __init__(self, x: int, y: int) -> None:
        super().__init__(x, y, 50)

class BackWallTile(Tile):
    def __init__(self, x: int, y: int) -> None:
        super().__init__(x, y, True, 2)

class LeftVerticalWallTile(Tile):
    def __init__(self, x: int, y: int) -> None:
        super().__init__(x, y, True, 9)

class RightVerticalWallTile(Tile):
    def __init__(self, x: int, y: int) -> None:
        super().__init__(x, y, True, 14)

class FrontCornerLeftWallTile(Tile):
    def __init__(self, x: int, y: int) -> None:
        super().__init__(x, y, True, 18)

class FrontCornerRightWallTile(Tile):
    def __init__(self, x: int, y: int) -> None:
        super().__init__(x, y, True, 23)

class BackCornerLeftWallTile(Tile):
    def __init__(self, x: int, y: int) -> None:
        super().__init__(x, y, True, 0)

class BackCornerRightWallTile(Tile):
    def __init__(self, x: int, y: int) -> None:
        super().__init__(x, y, True, 5)
