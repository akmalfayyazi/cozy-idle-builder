class Quest:
    def __init__(self, description, target, reward_coins, reward_xp):
        self.description = description
        self.target = target
        self.progress = 0
        self.reward_coins = reward_coins
        self.reward_xp = reward_xp
        self.completed = False
    
    def update_progress(self, amount):
        self.progress += amount
        if self.progress >= self.target:
            self.completed = True