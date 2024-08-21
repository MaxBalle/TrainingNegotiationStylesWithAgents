from negotiationGenerator.scenario import ScenarioPerspective

# def competing(outcome: tuple[int, float, float, int], negotiation_scenario_perspective: ScenarioPerspective) -> float:
#
# def accommodating(outcome: tuple[int, float, float, int], negotiation_scenario_perspective: ScenarioPerspective) -> float:
#
# def avoiding_population(outcome: tuple[int, float, float, int], negotiation_scenario_perspective: ScenarioPerspective) -> float:
    

def collaborating(outcome: tuple[int, float, float, int], negotiation_scenario_perspective: ScenarioPerspective) -> float:
    result, utility_a, utility_b, time = outcome
    joint_utility = utility_a + utility_b
    return joint_utility #TODO insert realistic function

# def compromising(outcome: tuple[int, float, float, int], negotiation_scenario_perspective: ScenarioPerspective) -> float: