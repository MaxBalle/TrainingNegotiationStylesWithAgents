import os
os.environ["TF_CPP_MIN_LOG_LEVEL"] = "1"

from negotiationGenerator.scenario import Scenario
from negotiationGenerator.discreteGenerator import build_negotiation_scenario
from agent import Agent
from negotiation import generate_simulations, simulate_local_negotiations, process_results
import fitness

import random
import time
import csv
import gc

import tensorflow as tf
from keras import layers, Sequential, backend, models
import numpy as np

from mpi4py import MPI

issues = [5, 5, 5, 5, 5]
starting_generation = 1
generation_count = 10 #Number of generations to simulate / last generation
population_size = 100 #Has to be even and be equal to the sum of survivor_count plus the sum of recombination_segments
survivor_count = 10 #Number of survivors per generation
recombination_split = [10, 30, 50] #Top x to group and reproduce (2 -> 2), also has to be even
mutation_stddev = 0.15

def create_model():
    model = Sequential()
    #model.add(layers.Dense(50, name='In'))
    model.add(layers.GRU(28, name='Recurrent Middle', stateful=True, activation='sigmoid'))
    #model.add(layers.Dense(28, name='Out', activation='sigmoid')) #First three are continue, accept and decline, the rest is values for a counteroffer
    model.build(input_shape=(1, 1, 50))
    return model

#Initializes the populations with random weights
def init_population(size: int, fitness_function, style) -> list[Agent]:
    population: list[Agent] = []
    for x in range(size):
        model = create_model()
        population.append(Agent(model, fitness_function, style))
    return population

def load_population(size, fitness_function, style) -> list[Agent]:
    population: list[Agent] = []
    for i in range(size):
        model = models.load_model(f"models/all/{style}_{i}.keras")
        population.append(Agent(model, fitness_function, style))
    return population

#Returns two new agents that are children of the provided agents through recombination
def crossover(parent_1: Agent, parent_2: Agent) -> tuple:
    genome_parent_1 = parent_1.model.get_weights()
    genome_parent_2 = parent_2.model.get_weights()
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
    return genome_child_1, genome_child_2

#Adds gaussian noise to all weights
def mutate(agent: Agent):
    for layer in agent.model.layers:
        for weight in layer.trainable_weights:
            weight.assign_add(tf.random.normal(tf.shape(weight), 0, mutation_stddev))

def get_last_generation_from_csv() -> int:
    try:
        gen = 0
        with open("training.csv", "r", newline="") as csv_file:
            for row in csv.reader(csv_file, dialect="excel"):
                gen = row[0]
        return int(gen)
    except FileNotFoundError:
        return 0

def write_csv_headers():
    headers = ["Generation"]
    for population_name in populations:
        for population_name_2 in populations:
            headers.append(f"Fitness_{population_name}_vs_{population_name_2}")
    for stat in ["Accepts", "Rejects", "Time"]:
        for population_name in populations:
            active = False
            for population_name_2 in populations:
                if population_name_2 == population_name:
                    active = True
                if active:
                    headers.append(f"{stat}_{population_name}_vs_{population_name_2}")
    for population_name in populations:
        headers.append(f"Total_fitness_{population_name}")
        headers.append(f"Highest_fitness_{population_name}")
    headers.append("Training_Time")
    csv_file = open("training.csv", "w", newline="")
    csv_writer = csv.writer(csv_file, dialect='excel')
    csv_writer.writerow(headers)

def write_to_scv(row):
    csv_file = open("training.csv", "a", newline="")
    csv_writer = csv.writer(csv_file, dialect='excel')
    csv_writer.writerow(row)

if __name__ == "__main__":
    comm = MPI.COMM_WORLD
    size = comm.Get_size()
    rank = comm.Get_rank()

    print(f"Rank {rank}, Size {size}")

    if rank == 0:
        start_time = time.time()
        last_generation = get_last_generation_from_csv()
        if last_generation == 0:
            print("Initializing populations")
            populations = {
                "accommodating": init_population(population_size, fitness.accommodating, "accommodating"),
                "collaborating": init_population(population_size, fitness.collaborating, "collaborating"),
                "compromising": init_population(population_size, fitness.compromising, "compromising"),
                "avoiding": init_population(population_size, fitness.avoiding, "avoiding"),
                "competing": init_population(population_size, fitness.competing, "competing")
            }
            write_csv_headers()
        else:
            print(f"Loading populations from generation {last_generation}")
            starting_generation = last_generation + 1
            populations = {
                "accommodating": load_population(population_size, fitness.accommodating, "accommodating"),
                "collaborating": load_population(population_size, fitness.collaborating, "collaborating"),
                "compromising": load_population(population_size, fitness.compromising, "compromising"),
                "avoiding": load_population(population_size, fitness.avoiding, "avoiding"),
                "competing": load_population(population_size, fitness.competing, "competing")
            }
    for generation in range(starting_generation, starting_generation + generation_count):
        if rank == 0:
            csv_row = [generation]
            generation_start_time = time.time()
            print(f"\nGeneration {generation}")
            scenario: Scenario = build_negotiation_scenario(issues)
        # Parallel Negotiation / Fitness
        simulations = None
        if rank == 0:
            all_simulations = generate_simulations(populations, scenario)
            simulations = all_simulations
        simulations = comm.bcast(simulations, root=0)
        local_simulation_results = simulate_local_negotiations(simulations, rank, size)
        simulation_results = comm.gather(local_simulation_results, root=0)
        if rank == 0:
            simulation_results = [item for sublist in simulation_results for item in sublist] #Flatten results
            simulation_stats = process_results(populations, all_simulations, simulation_results)
            for matrix in simulation_stats:
                #print(f"Matrix: {matrix}")
                csv_row.extend([value for value in matrix.values()])
            new_generation_genomes = {}
            for population_name in populations:
                #Selection
                populations[population_name].sort(key=lambda agent: agent.fitness)
                total_fitness = sum([simulation_stats[0][(population_name, population_name_2)] for population_name_2 in populations])
                #print(f"Total fitness {population_name}: {total_fitness}")
                csv_row.append(total_fitness)
                highest_fitness = populations[population_name][-1].fitness
                #print(f"Highest fitness {population_name}: {highest_fitness}")
                csv_row.append(highest_fitness)
                new_generation_genomes[population_name] = [survivor.model.get_weights() for survivor in populations[population_name][-survivor_count:]] #Fittest survive into next generation
                #Recombination
                for group_size in recombination_split:
                    pool = populations[population_name][-group_size:]
                    random.shuffle(pool)
                    for i in range(0, group_size, 2):
                        new_generation_genomes[population_name].extend(crossover(pool[i], pool[i + 1]))
                #Clear old population
                for agent in populations[population_name]:
                    del agent
                populations[population_name] = []
            backend.clear_session()
            gc.collect()
            for population_name in populations:
                for genome in new_generation_genomes[population_name]:
                    agent = Agent(create_model(), getattr(fitness, population_name), population_name)
                    agent.model.set_weights(genome)
                    populations[population_name].append(agent)
                #Mutate non survivors
                for agent in populations[population_name][survivor_count:]:
                    mutate(agent)
            generation_training_time = time.time() - generation_start_time
            print(f"Generation training time: {generation_training_time}")
            csv_row.append(generation_training_time)
            write_to_scv(csv_row)
        gc.collect()
    if rank == 0:
        print(f"\nTotal training time: {time.time() - start_time}")
        #Save all models
        for population_name in populations:
            for i in range(len(populations[population_name])):
                populations[population_name][i].model.save(f"models/all/{population_name}_{i}.keras")
