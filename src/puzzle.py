from dataclasses import dataclass
from pygame import Surface
from engine import Engine, EngineState
from input_sequences.event import Input
from input_sequences.input_sequences import InputSequences
from sequencer.sequencer import Sequencer
from sequencer.track import Track, TrackColor
from tile import EmptyTile, WallTile, PitTile, LeftVerticalWallTile, RightVerticalWallTile, FrontCornerLeftWallTile, FrontCornerRightWallTile, BackCornerLeftWallTile, BackCornerRightWallTile, BackWallTile, BackCornerLeftPitTile,BackCornerRightPitTile, FrontCornerLeftPitTile, FrontCornerRightPitTile, BackPitTile, RightVerticalPitTile, LeftVerticalPitTile, FrontPitTile
from entity import PlayerEntity, SnakeEntity, RatEntity, KeyEntity, DoorEntity, ExitEntity

CONTEXTUALIZED_WALLS = True

all_tiles = {
    ".": EmptyTile,
    "#": WallTile,
    "%": BackPitTile,
    "_": FrontPitTile, 
    "[": LeftVerticalPitTile,
    "]": RightVerticalPitTile,
    "<": FrontCornerLeftPitTile,
    ">": FrontCornerRightPitTile,
    "{": BackCornerLeftPitTile,
    "}": BackCornerRightPitTile,
    " ": PitTile,
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
    input_sequences: list[list[Input]]
    track_lengths: list[int]

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

    def update_sequencer(self, sequencer: Sequencer):
        track_datas: list[tuple[str, TrackColor]] = [
            ("A", TrackColor("#995555", "#553333", "#995555")),
            ("B", TrackColor("#559955", "#335533", "#559955")),
            ("C", TrackColor("#555599", "#333355", "#555599"))
        ]
        
        
        # self.add(Track([], "A", TrackColor("#995555", "#553333", "#995555"), 11)),
        # self.add(Track([], "B", TrackColor("#559955", "#335533", "#559955"), 7)),
        # self.add(Track([], "C", TrackColor("#555599", "#333355", "#555599"), 5))
        
        if len(self.track_lengths) > len(track_datas):
            raise ValueError("idk add some more tracks in puzzle.py")
        
        sequencer.set_tracks([
            Track([], *track_datas[i], length) for i, length in enumerate(self.track_lengths)
        ])
        
        sequencer.reset()

    def make_input_sequences(self, pos: tuple[int, int, int, int]):
        input_sequences = InputSequences(pos)
        input_sequences.set_events(self.input_sequences)
        
        return input_sequences
    
    def update(self, sequencer: Sequencer, state: EngineState, input_sequences: InputSequences):
        self.update_sequencer(sequencer)
        sequencer.playback_manager.reset(state)
        input_sequences.set_events(self.input_sequences)
    
puzzles = [
    Puzzle("Beginnings", [
            "################################",
            "#..............................#",
            "#.............#######..........#",
            "#.............#.....#.....####.#",
            "#.............#.....#.....#..#.#",
            "#.............#######.....#..#.#",
            "#.........................####.#",
            "#..............................#",
            "#..............................#",
            "#..p.............s.............#",
            "#..............................#",
            "#..............................#",
            "#........##########............#",
            "#........#........#............#",
            "#........#........#............#",
            "#........##########............#",
            "#..............................#",
            "################################",
        ], [
            [Input.Right],
            [Input.Left],
            [Input.Wait]
        ], [3]),
    Puzzle("Locked Door", [
            "################################",
            "#..............................#",
            "#............#######...........#",
            "#............#...r.#......####.#",
            "#............#.....#......#..#.#",
            "#............###d###......#..#.#",
            "#.........................####.#",
            "#..............................#",
            "#..............................#",
            "#..p..k.........s..............#",
            "#..............................#",
            "#..............................#",
            "#........##########............#",
            "#........#........#............#",
            "#........#........#............#",
            "#........##########............#",
            "#..............................#",
            "################################",
        ], [
            [Input.Right, Input.Up],
            [Input.Right, Input.Down],
            [Input.Left, Input.Right],
            [Input.Wait]
        ],  [6]),
    Puzzle("Locked Door + Pit", [
            "################################",
            "#..............................#",
            "#.............#######..........#",
            "#.............#...r.#.....####.#",
            "#.............#.....#.....#..#.#",
            "#.............###d###.....#..#.#",
            "#.........................####.#",
            "#..............................#",
            "#.........{%%%}................#",
            "#..p.k....[   ]..s.............#",
            "#.........<___>................#",
            "#..............................#",
            "#........##########............#",
            "#........#........#............#",
            "#........#........#............#",
            "#........##########............#",
            "#..............................#",
            "################################",
        ], [
            [Input.Right, Input.Up],
            [Input.Right, Input.Down],
            [Input.Left],
            [Input.Wait]
        ],  [4, 5]),
        Puzzle("Locked Door + Pit (2)", [
            "################################",
            "#..............................#",
            "#.............#######..........#",
            "#.............#...r.#....#####.#",
            "#.............#.....#....#..s#.#",
            "#.............###d###....#...#.#",
            "#........................##d##.#",
            "#..............................#",
            "#.........{%%%}................#",
            "#..p.k....[   ]..s.............#",
            "#.........<___>................#",
            "#..............................#",
            "#........##########............#",
            "#........#........#............#",
            "#........#........#............#",
            "#........##########............#",
            "#..............................#",
            "################################",
        ], [
            [Input.Right, Input.Up],
            [Input.Right, Input.Down],
            [Input.Left],
            [Input.Wait],
        ],  [3, 4, 5]),
                Puzzle("Locked Door + Pit (3)", [
            "################################",
            "#..............................#",
            "#.............#######..........#",
            "#.............#...r.#..........#",
            "#.............#.....#..........#",
            "#.............###d###..........#",
            "#..............................#",
            "#..............................#",
            "#.........{%%%}................#",
            "#..p.k....[   ]..s.............#",
            "#.........<___>................#",
            "#.......................#####..#",
            "#........##########.....#..s#..#",
            "#........#........#.....#...#..#",
            "#........#........#.....##d##..#",
            "#........##########............#",
            "#...........s..................#",
            "################################",
        ], [
            [Input.Right, Input.Up],
            [Input.Right, Input.Down],
            [Input.Left],
            [Input.Wait],
            [Input.Wait]
        ],  [3, 4, 5])
]

# TURN BACK NOW PLEASE

wall_types = {
    WallTile: 1, # Default wall tile
    BackCornerLeftWallTile: 2,
    BackCornerRightWallTile: 3,
    BackWallTile: 4,
    LeftVerticalWallTile: 5,
    RightVerticalWallTile: 6
}

pit_types = {
    PitTile: 1, # Default wall tile
    BackCornerLeftPitTile: 2,
    BackCornerRightPitTile: 3,
    BackPitTile: 4,
    LeftVerticalPitTile: 5,
    RightVerticalPitTile: 6,
    FrontPitTile: 7
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
                        ]: wall = BackCornerLeftWallTile

                        case [
                            [_, _, _],
                            [4, 1, _],
                            [_, 1, _]
                        ]: wall = BackCornerRightWallTile

                        case [
                            [_, 5, _],
                            [_, 1, 1],
                            [_, _, _]
                        ]: wall = FrontCornerLeftWallTile

                        case [
                            [_, 6, _],
                            [1, 1, _],
                            [_, _, _]
                        ]: wall = FrontCornerRightWallTile

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

                # if isinstance(world[y][x], PitTile):
                #     nearby_tiles = [[0 for _ in range(sample_range)] for _ in range(sample_range)]
                #     for index in range(sample_range ** 2):
                #         i = index // sample_range
                #         j = index % sample_range
                #         i_x = (i+x-1)
                #         i_y = (j+y-1)

                #         # help meeee -_-
                #         try:
                #             if type(world[i_y][i_x]) in pit_types:
                #                 nearby_tiles[j][i] = pit_types[type(world[i_y][i_x])]
                #             else:
                #                 nearby_tiles[j][i] = 0
                #         except IndexError:
                #             nearby_tiles[j][i] = 0
                                
                #             # if isinstance(world[i_y][i_x], (WallTile, BackCornerLeftTile, BackCornerRightTile, FrontCornerLeftTile, FrontCornerRightTile, LeftVerticalWallTile, RightVerticalWallTile)):
                #             #     nearby_tiles[j][i] = 1
                #                 # nearby_tiles[j][i] = [i_x, i_y]
                        
                #     pit = None
                #     print(
                #         "wtf"
                #     )
                    # match nearby_tiles:
                    #     case [
                    #         [_, _, _],
                    #         [_, 1, 1],
                    #         [_, 1, _]
                    #     ]: pit = BackCornerLeftPitTile

                    #     case [
                    #         [_, _, _],
                    #         [4, 1, _],
                    #         [_, 1, _]
                    #     ]: pit = BackCornerRightPitTile

                    #     case [
                    #         [_, 5, _],
                    #         [_, 1, 1],
                    #         [_, _, _]
                    #     ]: pit = FrontCornerLeftPitTile

                    #     case [
                    #         [_, 6, _],
                    #         [1, 1, _],
                    #         [_, _, _]
                    #     ]: pit = FrontCornerRightPitTile

                    #     case [
                    #         [_, _, _],
                    #         [2 | 4, _, _],
                    #         [_, _, _]
                    #     ]: pit = BackPitTile

                    #     case [
                    #         [_, 5 | 2, _],
                    #         [_, 1, _],
                    #         [_, _, _]
                    #     ]: pit = LeftVerticalPitTile

                    #     case [
                    #         [_, 6 | 3, _],
                    #         [_, 1, _],
                    #         [_, _, _]
                    #     ]: pit = RightVerticalPitTile
                    #     case _:
                    #         pit = PitTile
                    # contextualized_world[y][x] = pit(x,y)
        return contextualized_world
                