from audio import QueuedSound
from engine import Engine, EngineState
from input_sequences.event import Input
from sequencer.track import Track


class EnginePlaybackManager:
    starting_state: EngineState
    
    def __init__(self, starting_state: EngineState):
        self.starting_state = starting_state
    
    def reset(self, starting_state: EngineState):
        self.starting_state = starting_state
    
    def recompute(self, beat: int, engine: Engine, tracks: list[Track]):
        engine.import_state(self.starting_state)
        if beat >= 1:
            for i in range(0, beat + 1):
                self.process(i, engine, tracks)
    
    def process(self, beat: int, engine: Engine, tracks: list[Track]):
        inputs = self.get_inputs_at_beat(beat, tracks)
        
        x_input = 0
        y_input = 0
        
        for input in inputs:
            match input:
                case Input.Up: y_input -= 1
                case Input.Down: y_input += 1
                case Input.Left: x_input -= 1
                case Input.Right: x_input += 1
                # todo others idk
        
        if x_input != 0 or y_input != 0:
            engine.move_player(x_input, y_input)
        elif Input.Wait in inputs:
            engine.move_player(0, 0)
            return
    
    def get_inputs_at_beat(self, beat: int, tracks: list[Track]) -> set[Input]:
        inputs = set()
        
        for track in tracks:
            track_beat: int = ((beat - 1) % track.repeat_length) + 1
            
            # Find the event with a time and duration that includes the current beat
            event = None
            for e in track.events:
                if e.time < track_beat <= e.time + e.duration:
                    event = e
                    break
            if event is not None:
                input = event.inputs[track_beat - event.time - 1]
                if input != Input.Empty:
                    inputs.add(input)
    
        return inputs