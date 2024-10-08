#Half of a negotiation
class ScenarioPerspective:

    def __init__(self, perspective: list[tuple[float, list[float]]]):
        self.__issues = perspective
        self.__utility_list = []
        for issue in self.__issues:
            for option in issue[1]:
                self.__utility_list.append(option * issue[0])

    def get_issues(self):
        return self.__issues

    def get_issue(self, index: int):
        return self.__issues[index]

    def get_utility_array(self):
        return self.__utility_list

#Class to represent the scenario of a negotiation
class Scenario:

    def __init__(self, issue_shape: list[int],a: ScenarioPerspective, b: ScenarioPerspective):
        self.issue_shape = issue_shape
        self.a = a
        self.b = b

    def get_perspective(self, role):
        if role == 'a':
            return self.a
        elif role == 'b':
            return self.b
        return None