from keras import Sequential

class Agent:
    def __init__(self, model:Sequential, fitness_function, style):
        self.model = model
        self.fitness = 0.0
        self.fitness_function = fitness_function
        self.style = style