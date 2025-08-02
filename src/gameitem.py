class GameItem:
    def __init__(self, display_id):
        self.display_id = display_id

class Potion(GameItem):
    def __init__(self):
        super().__init__()