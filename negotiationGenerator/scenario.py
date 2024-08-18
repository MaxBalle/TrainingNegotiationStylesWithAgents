#Class to represent the scenario of a negotiation
class Scenario:

    def __init__(self, a: list[tuple[float, list]], b: list[tuple[float, list]]):
        self.a = a
        self.b = b