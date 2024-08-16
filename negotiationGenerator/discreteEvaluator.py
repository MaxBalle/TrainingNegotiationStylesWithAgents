import matplotlib.pyplot as plt
import discreteGenerator
import itertools

negotiation_params = [5,5,5,5,5]

negotiation = discreteGenerator.build_negotiation(negotiation_params)
print(f"A: {negotiation[0]}")
print(f"B: {negotiation[1]}")

#All possible solutions
utilityPairs = []

ranges = []
for param in negotiation_params:
    ranges.append(range(0,param))

for point in itertools.product(*ranges):
    utility_a, utility_b = 0, 0
    for i in range(0,len(point)):
        utility_a += negotiation[0][i][0] * negotiation[0][i][1][point[i]]
        utility_b += negotiation[1][i][0] * negotiation[1][i][1][point[i]]
    utilityPairs.append((utility_a, utility_b))

distributive_utilities_a, distributive_utilities_b = [], []
integrative_utilities_a, integrative_utilities_b = [], []
#optimal according to pareto-optimum
optimal_utilities_a, optimal_utilities_b = [], []

utilityPairs.sort(key=lambda x: -x[0])
max_b_utility = -1
max_joint_utility = (0,0)
fairest_pareto_outcome = (0,1)

for utilityPair in utilityPairs:
    if utilityPair[1] > max_b_utility:
        optimal_utilities_a.append(utilityPair[0])
        optimal_utilities_b.append(utilityPair[1])
        max_b_utility = utilityPair[1]
        if utilityPair[0]+utilityPair[1] > max_joint_utility[0]+max_joint_utility[1]:
            max_joint_utility = (utilityPair[0],utilityPair[1])
        if abs(utilityPair[0]-utilityPair[1]) < abs(fairest_pareto_outcome[0]-fairest_pareto_outcome[1]):
            fairest_pareto_outcome = (utilityPair[0],utilityPair[1])
    if utilityPair[0]+utilityPair[1] <= 1:
        distributive_utilities_a.append(utilityPair[0])
        distributive_utilities_b.append(utilityPair[1])
    else:
        integrative_utilities_a.append(utilityPair[0])
        integrative_utilities_b.append(utilityPair[1])


plt.figure(dpi=300)
plt.xlim(0,1)
plt.ylim(0,1)

plt.plot(optimal_utilities_a, optimal_utilities_b, '-k')
plt.plot(distributive_utilities_a, distributive_utilities_b, 'or', markersize=1)
plt.plot(integrative_utilities_a, integrative_utilities_b, 'og', markersize=1)
plt.plot(max_joint_utility[0],max_joint_utility[1], '+b')
plt.plot(fairest_pareto_outcome[0], fairest_pareto_outcome[1], 'xc')

plt.xlabel('utility a')
plt.ylabel('utility b')

plt.show()

#print(len(suboptimal_utilities_a))