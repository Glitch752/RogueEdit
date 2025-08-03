from enum import Enum
import random
from typing import Self

import pygame

from utils import get_asset

class SoundType(Enum):
    """Enum for all the sound types in the game. If a sound's value is a list of strings, the sound will randomly play one of the sounds in the list."""
    SPEAKING_SOUND = [f"speak_{str(idx).rjust(2, '0')}.wav" for idx in range(1, 15)]
    HOVER = "hover.wav"
    HIT = "hit.wav"
    KEY = "key.wav"
    
    def __init__(self, paths: str | list[str]):
        if isinstance(paths, str):
            paths = [paths]
        
        self.paths = paths
        self.sounds = [pygame.mixer.Sound(get_asset("audio", path)) for path in paths]
    
    def get_sound(self: Self):
        return self.sounds[random.randint(0, len(self.sounds) - 1)]

QueuedSound = tuple[int, pygame.mixer.Sound, float]

class AudioManager:
    current_track: str = ""
    
    queued_sounds: list[QueuedSound] = []
    
    def update(self: Self):
        self.play_sounds()
    
    def play_sounds(self: Self):
        i = 0
        while i < len(self.queued_sounds):
            sound = self.queued_sounds[i]
            if sound[0] <= pygame.time.get_ticks():
                sound[1].set_volume(sound[2])
                sound[1].play()
                self.queued_sounds.pop(i)
                i -= 1
            i += 1
    
    def play_sound(self: Self, sound: SoundType, volume: float = 1, delay_ms: int = 0):
        self.queued_sounds.append((pygame.time.get_ticks() + delay_ms, sound.get_sound(), volume))

audio_manager = AudioManager()