import json


class GameStats():

    def __init__(self,ai_settings):
        try:
            with open('high_score.json') as hs:
                self.high_score = json.load(hs)
        except FileNotFoundError:
            with open('high_score.json', 'w') as hs:
                json.dump(0, hs)
                self.high_score = 0
        self.ai_settings = ai_settings
        self.reset_stats()
        self.game_active = False

    def reset_stats(self):
        self.ships_left = self.ai_settings.ship_limit
        self.score = 0
        self.level = 1
        self.kill_num = 0