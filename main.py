from negotiationGenerator.scenario import Scenario
from negotiationGenerator.discreteGenerator import build_negotiation_scenario
import fitness
from negotiation import negotiate

import random
from multiprocessing import Pool

from keras.src.models.cloning import clone_model
#import tensorflow as tf
from keras import layers, Sequential
#from tensorflow.python.keras import Sequential
#import keras
import numpy as np

issues = [5, 5, 5, 5, 5]
time_cap = 100 #Max number of send messages / moment of timeout
max_generation = 1 #Number of generations to simulate / last generation
population_size = 20 #Has to be even and be equal to the sum of survivor_count plus the sum of recombination_segments
survivor_count = 2 #Number of survivors per generation
recombination_split = [2, 6, 10] #Top x to group and reproduce (2 -> 2), also has to be even

def init_population(size: int) -> list[Sequential]:
    population: list[Sequential] = []
    for x in range(size):
        model = Sequential()
        model.add(layers.Dense(50, name='In'))
        model.add(layers.GRU(50, name='Recurrent Middle', stateful=True))
        model.add(layers.Dense(28, name='Out', activation='sigmoid')) #First three are continue, accept and decline, the rest is values for a counteroffer
        model.build(input_shape=(1, 1, 50))
        population.append(model)
    return population

def find_fitness(agent_1: Sequential, agent_2: Sequential, negotiation_scenario: Scenario, fitness_function_1, fitness_function_2) -> tuple[float, float]:
    #Negotiate in both constellations to decrease influence of unfair negotiations
    outcome_1_2 = negotiate(agent_1, agent_2, negotiation_scenario, time_cap)
    outcome_2_1 = negotiate(agent_2, agent_1, negotiation_scenario, time_cap)
    fitness_1 = fitness_function_1(outcome_1_2, negotiation_scenario.a) + fitness_function_1(outcome_2_1, negotiation_scenario.b)
    fitness_2 = fitness_function_2(outcome_1_2, negotiation_scenario.a) + fitness_function_2(outcome_2_1, negotiation_scenario.b)
    return fitness_1, fitness_2

def reproduce(parent_1: Sequential, parent_2: Sequential) -> tuple[Sequential, Sequential]:
    genome_parent_1 = parent_1.get_weights()
    genome_parent_2 = parent_2.get_weights()
    child_1 = clone_model(parent_1)
    child_2 = clone_model(parent_2)
    genome_child_1 = []
    genome_child_2 = []
    for arr_1, arr_2 in zip(genome_parent_1, genome_parent_2):
        axis = random.randrange(0,len(arr_1.shape))
        index = random.randrange(1, arr_1.shape[axis])
        arr_1_split = np.split(arr_1, [index], axis)
        arr_2_split = np.split(arr_2, [index], axis)
        new_arr_1 = np.concatenate((arr_1_split[0], arr_2_split[1]), axis=axis)
        new_arr_2 = np.concatenate((arr_2_split[0], arr_1_split[1]), axis=axis)
        if random.choice([True, False]): #Randomly assign the recombined weight matrices to the children
            genome_child_1.append(new_arr_1)
            genome_child_2.append(new_arr_2)
        else:
            genome_child_1.append(new_arr_2)
            genome_child_2.append(new_arr_1)
    child_1.set_weights(genome_child_1)
    child_2.set_weights(genome_child_2)
    return child_1, child_2

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