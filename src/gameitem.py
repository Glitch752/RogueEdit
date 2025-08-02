class GameItem:
    def __init__(self, display_id):
        self.display_id = display_id

    def on_use(self, engine):
        pass

class Potion(GameItem):
    def __init__(self):
        super().__init__(69_420)
    
    def on_use(self, engine):
        engine.player.health = engine.player.max_health