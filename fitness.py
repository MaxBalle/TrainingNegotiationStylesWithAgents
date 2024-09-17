from negotiationGenerator.scenario import ScenarioPerspective
from negotiation import time_cap

#These are fitness functions for agents of different TKI negotiation styles. They can only be compared within a style, not across!

def accommodating(outcome: tuple[int, float, float, int], negotiation_scenario_perspective: ScenarioPerspective) -> float:
    return __calc_fairness(outcome, time_weight=0, partner_utility_weight=1) #Negative fairness maybe

def collaborating(outcome: tuple[int, float, float, int], negotiation_scenario_perspective: ScenarioPerspective) -> float:
    return __calc_fairness(outcome, time_weight=0, own_utility_weight=1, partner_utility_weight=1, joint_utility_weight=1, fairness_weight=1)

def compromising(outcome: tuple[int, float, float, int], negotiation_scenario_perspective: ScenarioPerspective) -> float:
    return __calc_fairness(outcome, time_weight=0, own_utility_weight=0.25, partner_utility_weight=0.25, joint_utility_weight=0.5, fairness_weight=1)

def avoiding(outcome: tuple[int, float, float, int], negotiation_scenario_perspective: ScenarioPerspective) -> float:
    return __calc_fairness(outcome, time_weight=1, fairness_weight=0.25)

def competing(outcome: tuple[int, float, float, int], negotiation_scenario_perspective: ScenarioPerspective) -> float:
    return __calc_fairness(outcome, time_weight=0, own_utility_weight=1, fairness_weight=-1)

def __calc_fairness(outcome: tuple[int, float, float, int], time_weight=0.0, own_utility_weight=0.0, partner_utility_weight=0.0, joint_utility_weight=0.0, fairness_weight=0.0) -> float:
    result, own_utility, partner_utility, time = outcome
    joint_utility = own_utility + partner_utility
    fairness = abs(own_utility - partner_utility)
    return own_utility_weight * own_utility + partner_utility_weight * partner_utility + joint_utility_weight * joint_utility + fairness_weight * fairness - time_weight * (time / time_cap)
