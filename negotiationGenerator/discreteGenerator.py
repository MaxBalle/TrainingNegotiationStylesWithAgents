import random
import heapq
from negotiationGenerator import discreteEvaluator
from negotiationGenerator.scenario import Scenario

#Divisive approach to generate the importance of a given number of issues for one side of the negotiation
def generate_importance(num: int, decimals: int) -> list[float]:
    max_value = pow(10, decimals)
    values = [-max_value]

    for x in range(num - 1):
        biggest = - heapq.heappop(values)
        new = int(round(random.triangular(0.5, biggest + 0.4999)))
        heapq.heappush(values, - new)
        heapq.heappush(values, - (biggest - new))

    for x in range(num):
        values[x] /= - max_value

    random.shuffle(values)

    return values

#Generates the preferences of both parties for one issue
#Each set of preferences has one 1 randomly chosen from a triangular distribution that is biased to the opposing side than the opponents distribution
#The remaining values are randomly generated with a normal variation around a mean decreasing by the relative distance to the value with preference 1
def generate_preference(num: int, decimals: int = -1, sigma: float = 0.05) -> tuple[list[float], list[float]]:

    values_low, values_high = [], []
    perfect_low = int(random.triangular(0,num, 0)) #Special case, could be implemented faster if needed
    perfect_high = int(random.triangular(0,num, num)) #Same
    for x in range(num):
        if x == perfect_low:
            values_low.append(1)
        else:
            new_val = 2.0
            while new_val > 1:
                new_val = random.normalvariate(1 - abs(perfect_low - x) / (num - 1), sigma)
            if new_val < 0:
                new_val = 0
            values_low.append(new_val)
        if x == perfect_high:
            values_high.append(1)
        else:
            new_val = 2.0
            while new_val > 1:
                new_val = random.normalvariate(1 - abs(perfect_high - x) / (num - 1), sigma)
            if new_val < 0:
                new_val = 0
            values_high.append(new_val)
    if decimals >= 0:
        for x in range(num):
            values_low[x] = round(values_low[x], decimals)
            values_high[x] = round(values_high[x], decimals)
    return values_low, values_high

#Builds a negotiation scenario (that might be flawed)
#This function takes a list of integers and returns a Scenario with an issue for each int and for each issue as many options as the value of the int
def build_raw_negotiation_scenario(issues: list[int]) -> Scenario:
    importance_a, importance_b = generate_importance(len(issues), 2), generate_importance(len(issues), 2)
    res_a, res_b = [], []
    for issue in issues:
        preferences = generate_preference(issue, decimals=2)
        res_a.append((importance_a.pop(), preferences[0]))
        res_b.append((importance_b.pop(), preferences[1]))
    return Scenario(res_a, res_b)

#Builds negotiation scenarios until a suitable one (as per discreteEvaluator.py) is found
#This function takes a list of integers and returns a Scenario with an issue for each int and for each issue as many options as the value of the int
def build_negotiation_scenario(issues: list[int], logging=False, plotting=False) -> Scenario:
    negotiation: Scenario = build_raw_negotiation_scenario(issues)
    while not discreteEvaluator.evaluate(negotiation, logging=logging, plotting=plotting):
        negotiation = build_raw_negotiation_scenario(issues)
    return negotiation