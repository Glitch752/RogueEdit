from dataclasses import dataclass
from pygame import Surface
from engine import Engine
from tile import EmptyTile, WallTile, LeftVerticalWallTile, RightVerticalWallTile, FrontCornerLeftTile, FrontCornerRightTile, BackCornerLeftTile, BackCornerRightTile, BackWallTile
from entity import PlayerEntity, SnakeEntity, RatEntity, KeyEntity, DoorEntity, ExitEntity
from typing import Any

CONTEXTUALIZED_WALLS = True

all_tiles = {
    ".": EmptyTile,
    "#": WallTile,
    "%": BackWallTile,
    "[": LeftVerticalWallTile,
    "]": RightVerticalWallTile,
    "<": FrontCornerLeftTile,
    ">": FrontCornerRightTile,
    "{": BackCornerLeftTile,
    "}": BackCornerRightTile,
}

all_entities = {
    "p": PlayerEntity,
    "s": SnakeEntity,
    "r": RatEntity,
    "k": KeyEntity,
    "d": DoorEntity,
    "X": ExitEntity
}

@dataclass
class Puzzle:
    name: str
    grid: list[str]

    def make_engine(self, tilemap: Surface) -> Engine:
        width, height = len(self.grid[0]), len(self.grid)
        engine: Engine = Engine(tilemap, width, height)

        # process the grid
        self.world = [[EmptyTile(x, y) for x in range(width)] for y in range(height)]
        for y, line in enumerate(self.grid):
            for x, char in enumerate(line):
                if char in all_tiles:
                    self.world[y][x] = all_tiles[char](x, y)

                elif char in all_entities:
                    t = all_entities[char]
                    entity = t(x, y)
                    engine.entities.update({entity.id: entity})
                    if t == PlayerEntity:
                        engine.player = list(engine.entities.values())[-1]
                    self.world[y][x] = EmptyTile(x, y)
                else:
                    raise ValueError(f"Unknown character '{char}' at ({x}, {y}) goober")

        # check wall tiles

        print("FINISH")
        # self.contextualized_world = self.world
        engine.world = contextualize(self.world, self.grid, width, height) if CONTEXTUALIZED_WALLS else self.world
        # engine.world = self.world
        return engine
    
puzzles = [
    Puzzle("IDK", [
            "##################################################",
            "#................................................#",
            "#.............#######............................#",
            "#.............#.....#.....####...................#",
            "#.............###d###.....#..#...................#",
            "#.......................#..#.....................#",
            "#.......................####.....................#",
            "#................................................#",
            "#................................................#",
            "#..p.............s...............................#",
            "#................................................#",
            "#................................................#",
            "#........##########..............................#",
            "#........#........#..............................#",
            "#........#........#..............................#",
            "#........##########..............................#",
            "#................................................#",
            "#................................................#",
            "##################################################",
        ]
    ),
    Puzzle("Locked Door", [
            "<###########################<>###########################>",
            "[...........................[]...........................]",
            "[...........................[]...........................]",
            "[..........r................[]...........................]",
            "[...........................[]...........................]",
            "[...........................[]...........................]",
            "[...........................[]...........................]",
            "[.......................s...[]...........................]",
            "[...........................##...........................]",
            "[..p..............k.........dd...........................]",
            "[...........................<>...........................]",
            "[...........................[]...........................]",
            "[...........................[]...........................]",
            "[...........................[]...........................]",
            "[...........................[]............s..............]",
            "[.........r.................[]...........................]",
            "[...........................[]...........................]",
            "[...........................[]...........................]",
            "##########################################################",
        ]
    )
]

# TURN BACK NOW PLEASE

wall_types = {
    WallTile: 1, # Default wall tile
    BackCornerLeftTile: 2,
    BackCornerRightTile: 3,
    BackWallTile: 4,
    LeftVerticalWallTile: 5,
    RightVerticalWallTile: 6
}

# hey im really sorry this shit is ugly af and almost 100% not how either of you would likely do this, sorry for wasting time on it, its just really late and i cant make myself put this off until tommorow :sob:
def contextualize(world, grid, width, height):
        # contextualized_world = [[world[y][x] for x in range(width)] for y in range(height)] # I was originally going to do this
        contextualized_world = world
        sample_range = 3
        for y, line in enumerate(grid):
            for x, tile in enumerate(line):
                if isinstance(world[y][x], WallTile):
                    nearby_tiles = [[0 for _ in range(sample_range)] for _ in range(sample_range)]
                    for index in range(sample_range ** 2):
                        i = index // sample_range
                        j = index % sample_range
                        i_x = (i+x-1)
                        i_y = (j+y-1)

                        # help meeee -_-
                        try:
                            if type(world[i_y][i_x]) in wall_types:
                                nearby_tiles[j][i] = wall_types[type(world[i_y][i_x])]
                            else:
                                nearby_tiles[j][i] = 0
                        except IndexError:
                            nearby_tiles[j][i] = 0
                                
                            # if isinstance(world[i_y][i_x], (WallTile, BackCornerLeftTile, BackCornerRightTile, FrontCornerLeftTile, FrontCornerRightTile, LeftVerticalWallTile, RightVerticalWallTile)):
                            #     nearby_tiles[j][i] = 1
                                # nearby_tiles[j][i] = [i_x, i_y]
                        
                    wall = None
                    match nearby_tiles:
                        case [
                            [_, _, _],
                            [_, 1, 1],
                            [_, 1, _]
                        ]: wall = BackCornerLeftTile

                        case [
                            [_, _, _],
                            [4, 1, _],
                            [_, 1, _]
                        ]: wall = BackCornerRightTile

                        case [
                            [_, 5, _],
                            [_, 1, 1],
                            [_, _, _]
                        ]: wall = FrontCornerLeftTile

                        case [
                            [_, 6, _],
                            [1, 1, _],
                            [_, _, _]
                        ]: wall = FrontCornerRightTile

                        case [
                            [_, _, _],
                            [2 | 4, _, _],
                            [_, _, _]
                        ]: wall = BackWallTile

                        case [
                            [_, 5 | 2, _],
                            [_, 1, _],
                            [_, _, _]
                        ]: wall = LeftVerticalWallTile

                        case [
                            [_, 6 | 3, _],
                            [_, 1, _],
                            [_, _, _]
                        ]: wall = RightVerticalWallTile
                        case _:
                            wall = WallTile
                    contextualized_world[y][x] = wall(x,y)
        return contextualized_world
                