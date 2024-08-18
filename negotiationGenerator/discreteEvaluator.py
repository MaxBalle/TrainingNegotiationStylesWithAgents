import matplotlib.pyplot as plt
import itertools

def evaluate(negotiation: tuple[list[tuple[int, list]], list[tuple[int, list]]], logging=False, plotting=False) -> bool:
    if logging:
        print(f"Negotiation:")
        print(f"A: {negotiation[0]}")
        print(f"B: {negotiation[1]}")

    #All possible solutions
    utility_pairs = []

    ranges = []
    for issue in negotiation[0]:
        ranges.append(range(0,len(issue[1])))

    for point in itertools.product(*ranges):
        utility_a, utility_b = 0, 0
        for i in range(0,len(point)):
            utility_a += negotiation[0][i][0] * negotiation[0][i][1][point[i]]
            utility_b += negotiation[1][i][0] * negotiation[1][i][1][point[i]]
        utility_pairs.append((utility_a, utility_b))

    distributive_utilities_a, distributive_utilities_b = [], []
    integrative_utilities_a, integrative_utilities_b = [], []
    #optimal according to pareto-optimum
    optimal_utilities_a, optimal_utilities_b = [], []

    utility_pairs.sort(key=lambda x: -x[0])
    max_b_utility = -1
    max_joint_utility = (0,0)
    fairest_pareto_outcome = (0,1)

    for utilityPair in utility_pairs:
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

    if plotting:
        plt.figure(dpi=300)
        plt.xlim(0,1)
        plt.ylim(0,1)
        plt.xlabel('utility a')
        plt.ylabel('utility b')

        #Pareto optimal solutions as a solid black pareto front
        plt.plot(optimal_utilities_a, optimal_utilities_b, '-k')
        #Direct connection of the extremes of this front as a dashed line to visualize curvature
        plt.plot([optimal_utilities_a[0],optimal_utilities_a[len(optimal_utilities_a)-1]], [optimal_utilities_b[0],optimal_utilities_b[len(optimal_utilities_b)-1]], '--k')
        #All distributive solutions as red points
        plt.plot(distributive_utilities_a, distributive_utilities_b, 'or', markersize=1)
        #All integrative solutions as green points
        plt.plot(integrative_utilities_a, integrative_utilities_b, 'og', markersize=1)
        #Solution with the highest joint utility as a blue plus
        plt.plot(max_joint_utility[0],max_joint_utility[1], '+b')
        #Solution with the fairest outcome as a cyan x
        plt.plot(fairest_pareto_outcome[0], fairest_pareto_outcome[1], 'xc')

        plt.show()

    pareto_extremes_distance = pow((pow(1-optimal_utilities_b[0],2)+pow(1-optimal_utilities_a[len(optimal_utilities_a)-1],2)),0.5)

    #Integral to measure curvature
    area = 0.0
    curr_point = (optimal_utilities_a[0], optimal_utilities_b[0])
    for i in range(1,len(optimal_utilities_a)):
        new_point = (optimal_utilities_a[i], optimal_utilities_b[i])
        area += (curr_point[0] - new_point[0]) * (curr_point[1] + 0.5 * (new_point[1]-curr_point[1]))
        curr_point = new_point
    area -= (1-optimal_utilities_a[len(optimal_utilities_a)-1]) * (optimal_utilities_b[0] + 0.5 * (1-optimal_utilities_b[0]))
    relative_area = area / (0.5 * (1-optimal_utilities_a[len(optimal_utilities_a)-1]) * (1-optimal_utilities_b[0]))

    #Recommendation
    recommendation = "Usable"
    recommended = True
    if pareto_extremes_distance < 0.5:
        recommendation = "Unusable (Pareto front to narrow)"
        recommended = False
    elif relative_area < 0.2:
        recommendation = "Unusable (Pareto front to flat)"
        recommended = False
    elif abs(fairest_pareto_outcome[0] - fairest_pareto_outcome[1]) > 0.2:
        recommendation = "Unusable (No fair options)"
        recommended = False

    if logging:
        print(f"Number of pareto solutions: {len(optimal_utilities_a)}")
        print(f"Highest possible joint utility: {sum(max_joint_utility)}")
        print(f"Fairest outcome {fairest_pareto_outcome} with difference {abs(fairest_pareto_outcome[0]-fairest_pareto_outcome[1])}")
        print(f"Distance between pareto extremes: {pareto_extremes_distance}")
        print(f"Curvature indicator {relative_area}") #Relation of area between pareto front and dashed reference line and the remaining upper right triangle
        print(f"Recommendation: {recommendation}")

    return recommended