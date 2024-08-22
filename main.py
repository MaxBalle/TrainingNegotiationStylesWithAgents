from negotiationGenerator.scenario import Scenario
from negotiationGenerator.discreteGenerator import build_negotiation_scenario
import fitness

import random
from multiprocessing import Pool

import tensorflow as tf
from keras import layers, Sequential
#from tensorflow.python.keras import Sequential
#import keras
#import numpy as np

issues = [5, 5, 5, 5, 5]
time_cap = 100 #Max number of send messages / moment of timeout
max_generation = 1 #Number of generations to simulate / last generation
population_size = 20 #Has to be even and be equal to the sum of survivor_count plus the sum of recombination_segments
survivor_count = 2 #Number of survivors per generation
recombination_split = [2, 6, 10] #Top x to group and reproduce (2 -> 2), also has to be even

def init_population(size: int) -> list:
    population: list[Sequential] = []
    for x in range(size):
        model = Sequential()
        model.add(layers.Dense(50, name='In'))
        model.add(layers.GRU(50, name='Recurrent Middle', stateful=True))
        model.add(layers.Dense(28, name='Out', activation='sigmoid')) #First three are continue, accept and decline, the rest is values for a counteroffer
        population.append(model)
    return population

def encode_as_one_hot(li: list[float]) -> list[float]:
    max_index = 0
    max_value = 0
    for index in range(len(li)):
        if li[index] > max_value:
            max_index = index
    res = [0] * len(li)
    res[max_index] = 1
    return res

def calculate_utility(result_one_hot, offer_utilities_a, offer_utilities_b) -> tuple[float, float]:
    utility_a = 0.0
    utility_b = 0.0
    for x in range(len(result_one_hot)):
        utility_a = result_one_hot[x] * offer_utilities_a[x]
        utility_b = result_one_hot[x] * offer_utilities_b[x]
    return utility_a, utility_b

#Negotiation outcome is of the form (result, utility_1, utility_2, time)
def negotiate(agent_a: Sequential, agent_b: Sequential, negotiation_scenario: Scenario) -> tuple[int, float, float, int]:
    outcome, result_utility_a, result_utility_b, time = -1, 0.0, 0.0, 1
    ongoing = True
    #Starting side(agent_1) starts with an offer of max utility (alternative could be generating this as well but that would be an uncommon input and might hinder performance)
    offer_one_hot = []

    for issue in negotiation_scenario.a.get_issues():
        for option in issue[1]:
            offer_one_hot.append(1.0 if option == 1 else 0.0)
    offer_utilities_a = negotiation_scenario.a.get_utility_array()
    offer_utilities_b = negotiation_scenario.b.get_utility_array()
    offer = tf.constant([[[*offer_one_hot, *offer_utilities_a]]])
    while ongoing and time <= time_cap:
        time += 1
        ret_b = agent_b(offer) # Agent B processes offer
        continue_negotiation = ret_b[0][0].numpy() >= ret_b[0][1].numpy() and ret_b[0][0].numpy() >= ret_b[0][2].numpy() # B wants to continue negotiating if the first output (continue) is bigger than second and third (accept and decline)
        if not continue_negotiation: # B ends negotiation
            if ret_b[0][1].numpy() > ret_b[0][2].numpy(): # Accept bigger than decline
                # B accepts last offer from a
                outcome = 1
                result_utility_a, result_utility_b = calculate_utility(offer_one_hot, offer_utilities_a, offer_utilities_b)
                ongoing = False
            else:
                # B terminates the negotiation
                outcome = 0
                ongoing = False
        else:
            # Build the offer by B to A
            offer_one_hot = encode_as_one_hot(ret_b[0][3:].numpy())
            offer = tf.constant([[[*offer_one_hot, *offer_utilities_b]]])
            time += 1
            ret_a = agent_a(offer) # Agent A processes offer
            continue_negotiation = ret_a[0][0].numpy() >= ret_a[0][1].numpy() and ret_a[0][0].numpy() >= ret_a[0][2].numpy()  # A wants to continue negotiating if the first output (continue) is bigger than second and third (accept and decline)
            if not continue_negotiation: # A ends negotiation
                if ret_a[0][1].numpy() > ret_a[0][2].numpy(): # Accept bigger than decline
                    # A accepts last offer from b
                    outcome = 1
                    result_utility_a, result_utility_b = calculate_utility(offer_one_hot, offer_utilities_a, offer_utilities_b)
                    ongoing = False
                else:
                    # A terminates the negotiation
                    outcome = 0
                    ongoing = False
            else:
                # Build new offer by A to B
                offer_one_hot = encode_as_one_hot(ret_a[0][3:].numpy())
                offer = tf.constant([[[*offer_one_hot, *offer_utilities_a]]])
    agent_a.layers[1].reset_states()
    agent_b.layers[1].reset_states()
    return outcome, result_utility_a, result_utility_b, time

def find_fitness(agent_1: Sequential, agent_2: Sequential, negotiation_scenario: Scenario, fitness_function_1, fitness_function_2) -> tuple[float, float]:
    #Negotiate in both constellations to decrease influence of unfair negotiations
    outcome_1_2 = negotiate(agent_1, agent_2, negotiation_scenario)
    outcome_2_1 = negotiate(agent_2, agent_1, negotiation_scenario)
    fitness_1 = fitness_function_1(outcome_1_2, negotiation_scenario.a) + fitness_function_1(outcome_2_1, negotiation_scenario.b)
    fitness_2 = fitness_function_2(outcome_1_2, negotiation_scenario.a) + fitness_function_2(outcome_2_1, negotiation_scenario.b)
    return fitness_1, fitness_2

def reproduce(parent_1: Sequential, parent_2: Sequential) -> tuple[Sequential, Sequential]:
    return parent_1, parent_2

def mutate(agent: Sequential) -> Sequential:
    return agent

if __name__ == "__main__":
    # competing_population = init_population(population_size)
    # accommodating_population = init_population(population_size)
    # avoiding_population = init_population(population_size)
    collaborating_population = init_population(population_size)
    # compromising_population = init_population(population_size)
    generation = 1
    while generation <= max_generation:
        scenario: Scenario = build_negotiation_scenario(issues)
        #Negotiation simulation
        random.shuffle(collaborating_population)
        negotiations: list[tuple] = []
        for i in range(0,population_size, 2):
            negotiations.append((collaborating_population[i], collaborating_population[i+1], scenario, fitness.collaborating, fitness.collaborating))
        print(f"Negotiations: {negotiations}")
        with Pool() as p:
            results = p.starmap(find_fitness, negotiations)
        print(f"Results: {results}")
        #Selection
        agent_fitness_pairs = list(zip(collaborating_population,[fitness for pair in results for fitness in pair]))
        print(f"Agent-Fitness pairs: {agent_fitness_pairs}")
        agent_fitness_pairs.sort(key=lambda x: x[1])
        print(f"Agent-Fitness pairs sorted: {agent_fitness_pairs}")
        collaborating_population.clear()
        collaborating_population.extend(pair[0] for pair in agent_fitness_pairs[-survivor_count:]) #Fittest survive into next generation
        print(f"Collaborating survivors: {collaborating_population}")
        #Recombination and mutation
        for group_size in recombination_split:
            pool = [pair[0] for pair in agent_fitness_pairs[-group_size:]]
            random.shuffle(pool)
            children = []
            for i in range(0, group_size, 2):
                children.extend(reproduce(pool[i], pool[i+1]))
            for child in children:
                collaborating_population.append(mutate(child))
        print(f"Collaborating population: {collaborating_population}")
        generation += 1