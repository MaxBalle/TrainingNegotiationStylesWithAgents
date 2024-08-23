from negotiationGenerator.scenario import Scenario
from negotiationGenerator.discreteGenerator import build_negotiation_scenario
from agent import Agent
from negotiation import negotiate
import fitness

import random
import time
from multiprocessing import Pool

from keras.src.models.cloning import clone_model
import tensorflow as tf
from keras import layers, Sequential
#from tensorflow.python.keras import Sequential
#import keras
import numpy as np

issues = [5, 5, 5, 5, 5]
time_cap = 100 #Max number of send messages / moment of timeout
max_generation = 10 #Number of generations to simulate / last generation
population_size = 100 #Has to be even and be equal to the sum of survivor_count plus the sum of recombination_segments
survivor_count = 10 #Number of survivors per generation
recombination_split = [10, 30, 50] #Top x to group and reproduce (2 -> 2), also has to be even
mutation_stddev = 0.03

def init_population(size: int) -> list[Agent]:
    population: list[Agent] = []
    for x in range(size):
        model = Sequential()
        model.add(layers.Dense(50, name='In'))
        model.add(layers.GRU(50, name='Recurrent Middle', stateful=True))
        model.add(layers.Dense(28, name='Out', activation='sigmoid')) #First three are continue, accept and decline, the rest is values for a counteroffer
        model.build(input_shape=(1, 1, 50))
        population.append(Agent(model))
    return population

def cross_negotiate(agent_1: Agent, agent_2: Agent, negotiation_scenario: Scenario, fitness_function_1, fitness_function_2):
    #Negotiate in both constellations to decrease influence of unfair negotiations
    outcome_1_2 = negotiate(agent_1, agent_2, negotiation_scenario, time_cap)
    outcome_2_1 = negotiate(agent_2, agent_1, negotiation_scenario, time_cap)
    fitness_1 = fitness_function_1(outcome_1_2, negotiation_scenario.a) + fitness_function_1(outcome_2_1, negotiation_scenario.b)
    fitness_2 = fitness_function_2(outcome_1_2, negotiation_scenario.a) + fitness_function_2(outcome_2_1, negotiation_scenario.b)
    return fitness_1, fitness_2

def reproduce(parent_1: Agent, parent_2: Agent) -> tuple[Agent, Agent]:
    genome_parent_1 = parent_1.model.get_weights()
    genome_parent_2 = parent_2.model.get_weights()
    child_1 = Agent(clone_model(parent_1.model))
    child_2 = Agent(clone_model(parent_2.model))
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
    child_1.model.set_weights(genome_child_1)
    child_2.model.set_weights(genome_child_2)
    return child_1, child_2

#Adds gaussian noise to all weights
def mutate(agent: Agent) -> Agent:
    for layer in agent.model.layers:
        for weight in layer.trainable_weights:
            weight.assign_add(tf.random.normal(tf.shape(weight), 0, mutation_stddev))
    return agent

if __name__ == "__main__":
    start_time = time.time()
    populations = {
        "accommodation": init_population(population_size),
        "collaborating": init_population(population_size),
        "compromising": init_population(population_size),
        "avoiding": init_population(population_size),
        "competing": init_population(population_size)
    }
    generation = 1
    while generation <= max_generation:
        generation_start_time = time.time()
        print(f"\nGeneration {generation}")
        scenario: Scenario = build_negotiation_scenario(issues)
        print(f"Scenario:\nPerspective A:{scenario.a.get_issues()}\nPerspective B:{scenario.b.get_issues()}")
        #Negotiation simulation
        random.shuffle(populations["collaborating"])
        #Intra-style negotiations
        negotiations: list[tuple[Agent, Agent, Scenario, any, any]] = []
        for i in range(0,population_size, 2):
            negotiations.append((populations["collaborating"][i], populations["collaborating"][i+1], scenario, fitness.collaborating, fitness.collaborating))
        with Pool() as p:
            negotiation_results = p.starmap(cross_negotiate, negotiations)
        for negotiation, result in zip(negotiations, negotiation_results):
            negotiation[0].fitness += result[0]
            negotiation[1].fitness += result[1]
        #Selection
        populations["collaborating"].sort(key=lambda agent: agent.fitness)
        print(f"Total fitness: {sum([agent.fitness for agent in populations['collaborating']])}")
        print(f"Highest fitness: {populations['collaborating'][-1].fitness}")
        new_population = []
        new_population.extend(populations["collaborating"][-survivor_count:]) #Fittest survive into next generation
        for agent in new_population: #Reset fitness of survivors
            agent.fitness = 0.0
        #Recombination and mutation
        for group_size in recombination_split:
            pool = populations["collaborating"][-group_size:]
            random.shuffle(pool)
            children = []
            for i in range(0, group_size, 2):
                children.extend(reproduce(pool[i], pool[i+1]))
            for child in children:
                new_population.append(mutate(child))
        populations["collaborating"] = new_population
        print(f"Generation training time: {time.time() - generation_start_time}")
        generation += 1
    print(f"\nTotal time: {time.time() - start_time}")