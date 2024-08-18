import random
import heapq
from negotiationGenerator import discreteEvaluator


def generate_issues_divisive(num: int, decimals: int) -> list[int]:
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

def generate_values(num: int, decimals=-1) -> tuple[list[int], list[int]]:
    sigma = 0.05

    values_low, values_high = [], []
    perfect_low = int(random.triangular(0,num, 0)) #Special case, could be implemented faster if needed
    perfect_high = int(random.triangular(0,num, num)) #Same
    for x in range(num):
        if x == perfect_low:
            values_low.append(1)
        else:
            new_val = -1
            while new_val < 0 or new_val > 1:
                new_val = random.normalvariate(1 - abs(perfect_low - x) / (num - 1), sigma)
            values_low.append(new_val)
        if x == perfect_high:
            values_high.append(1)
        else:
            new_val = -1
            while new_val < 0 or new_val > 1:
                new_val = random.normalvariate(1 - abs(perfect_high - x) / (num - 1), sigma)
            values_high.append(new_val)
    if decimals >= 0:
        for x in range(num):
            values_low[x] = round(values_low[x], decimals)
            values_high[x] = round(values_high[x], decimals)
    return values_low, values_high

def build_raw_negotiation(issues: list[int]) -> tuple[list[tuple[int, list]], list[tuple[int, list]]]:
    issue_utility_a, issue_utility_b = generate_issues_divisive(len(issues), 2), generate_issues_divisive(len(issues), 2)
    res_a, res_b = [], []
    for issue in issues:
        values = generate_values(issue, 2)
        res_a.append((issue_utility_a.pop(), values[0]))
        res_b.append((issue_utility_b.pop(), values[1]))
    return res_a, res_b

def build_negotiation(issues: list[int]) -> tuple[list[tuple[int, list]], list[tuple[int, list]]]:
    negotiation = build_raw_negotiation(issues)
    while not discreteEvaluator.evaluate(negotiation, logging=True, plotting=True):
        negotiation = build_raw_negotiation(issues)
    return negotiation

#Tests:

# print(generate_values(5,2))
# print(generate_issues_divisive(5,2))
# countLow, countHigh = [0,0,0,0,0], [0,0,0,0,0]
# for i in range(10000):
#     values = generate_values(5,2)
#     for j in range(5):
#         if values[0][j] == 1:
#             countLow[j] += 1
#         if values[1][j] == 1:
#             countHigh[j] += 1
#
# print(f"Low {countLow}")
# print(f"High {countHigh}")