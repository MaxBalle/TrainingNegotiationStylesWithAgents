from keras import Sequential

class Agent:
    def __init__(self, model:Sequential):
        self.model = model
        self.fitness = 0.0