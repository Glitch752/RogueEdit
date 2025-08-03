from enum import Enum
import pygame
from audio import audio_manager
from dialogue.renderer import DialogueRenderer

BOSS_NAME = "Manager"
class DialogueType(Enum):
    INTRO = [
        [
            BOSS_NAME,
            "Hey, trainee!",
            "I hear you're new here."
        ],
        [
            BOSS_NAME,
            "Let's get you started with your first task."
        ],
        [
            BOSS_NAME,
            "As a video editor, you'll be working with",
            "sequences to finish levels of the game in",
            "the top right!"
        ]
    ]
    FINISHED_FIRST_LEVEL = [
        [
            BOSS_NAME,
            "Great job on the first level!",
            "Things will get harder from here,",
            "but I know you can handle it."
        ],
        [
            BOSS_NAME,
            "Press the green continue arrow",
            "to move on!"
        ]
    ]
    FINISHED_GAME = [
        [
            BOSS_NAME,
            "Wow, you did it!",
            "That's all the levels you're tasked to",
            "finish for now."
        ],
        [
            BOSS_NAME,
            "Great work, trainee! You'll be a valuable",
            "member of the team in no time."
        ],
        [
            "The actual developers",
            "Thanks for playing our game!",
            "We really hope you enjoyed it."
        ],
        [
            "The actual developers",
            "We couldn't fit in all the content",
            "we wanted to, but it was a fun project",
            "and we hope you liked it!"
        ]
    ]

class DialogueManager:
    renderer: DialogueRenderer = DialogueRenderer()
    
    queue: list[list[str]] = []
    current_lines: list[str] = []
    
    def queue_dialogue(self, type: DialogueType):
        for lines in type.value:
            self.queue.append(list(lines)) # Copy the list to prevent modification of the original
        if not self.is_shown():
            self.renderer.reset()
            self.current_lines = self.queue.pop(0)
    
    def on_confirm(self):
        if self.is_active():
            self.renderer.skip_to_end(self.current_lines)
        else:
            self.current_lines.clear()
            self.renderer.reset()
            if len(self.queue):
                self.current_lines = self.queue.pop(0)
    
    def is_shown(self):
        return len(self.current_lines) != 0
    
    def is_active(self):
        return len(self.current_lines) != 0 and not self.renderer.done
    
    def update(self, delta: float):
        if self.is_active():
            self.renderer.update(self.current_lines, delta, audio_manager)
    
    def draw(self, win: pygame.Surface):
        if len(self.current_lines):
            self.renderer.draw(win, self.current_lines)