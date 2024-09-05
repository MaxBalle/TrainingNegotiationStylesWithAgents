from typing import List

from agent import Agent
from negotiationGenerator.scenario import Scenario

import tensorflow as tf

import random
from multiprocessing import Pool

#This file contains the logic to simulate the negotiation between two agents

time_cap = 100 #Max number of send messages / moment of timeout

#Returns one-hot-encoding as a flat list or grouped into issues
def encode_as_one_hot(li: list[float], shape: list[int], flat = True) -> list:
    one_hot = []
    start_index = 0
    for issue_length in shape:
        max_index = 0
        max_value = 0
        for index in range(start_index, start_index + issue_length):
            if li[index] > max_value:
                max_index = index
                max_value = li[index]
        res = [0] * issue_length
        res[max_index - start_index] = 1
        if flat:
            one_hot.extend(res)
        else:
            one_hot.append(res)
        start_index += issue_length
    return one_hot

def calculate_utility(result_one_hot, offer_utilities_a, offer_utilities_b) -> tuple[float, float]:
    utility_a = 0.0
    utility_b = 0.0
    for x in range(len(result_one_hot)):
        utility_a += result_one_hot[x] * offer_utilities_a[x]
        utility_b += result_one_hot[x] * offer_utilities_b[x]
    return utility_a, utility_b

#Negotiation outcome returned the form (result, utility_1, utility_2, time)
def negotiate(agent_a: Agent, agent_b: Agent, negotiation_scenario: Scenario) -> tuple[int, float, float, int]:
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
        ret_b = agent_b.model(offer) # Agent B processes offer
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
            offer_one_hot = encode_as_one_hot(ret_b[0][3:].numpy(), negotiation_scenario.issue_shape)
            offer = tf.constant([[[*offer_one_hot, *offer_utilities_b]]])
            time += 1
            ret_a = agent_a.model(offer) # Agent A processes offer
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
                offer_one_hot = encode_as_one_hot(ret_a[0][3:].numpy(), negotiation_scenario.issue_shape)
                offer = tf.constant([[[*offer_one_hot, *offer_utilities_a]]])
    agent_a.model.layers[1].reset_states()
    agent_b.model.layers[1].reset_states()
    #print(f"Negotiation between {agent_a} and {agent_b} came to the outcome {outcome} at t={time} with utility_a={result_utility_a} and utility_b={result_utility_b}")
    return outcome, result_utility_a, result_utility_b, time

def cross_negotiate(agent_1: Agent, agent_2: Agent, negotiation_scenario: Scenario) -> (float, float, float, int):
    #Negotiate in both constellations to decrease influence of unfair negotiations
    outcome_1_2 = negotiate(agent_1, agent_2, negotiation_scenario)
    outcome_2_1 = negotiate(agent_2, agent_1, negotiation_scenario)
    fitness_1 = agent_1.fitness_function(outcome_1_2, negotiation_scenario.a) + agent_1.fitness_function(outcome_2_1, negotiation_scenario.b)
    fitness_2 = agent_2.fitness_function(outcome_1_2, negotiation_scenario.a) + agent_2.fitness_function(outcome_2_1, negotiation_scenario.b)
    accepts = sum(1 for i in [outcome_1_2, outcome_2_1] if i[0] == 1)
    rejects = sum(1 for i in [outcome_1_2, outcome_2_1] if i[0] == 0)
    total_time = outcome_1_2[3] + outcome_2_1[3]
    return fitness_1, fitness_2, accepts, rejects, total_time

def simulate_negotiations(populations, scenario: Scenario):
    for population_name in populations:
        random.shuffle(populations[population_name])
    negotiations: list[tuple[Agent, Agent, Scenario]] = []
    # Intra-style negotiations
    for population_name in populations:
        for i in range(0, len(populations[population_name]), 2):
            negotiations.append((populations[population_name][i], populations[population_name][i + 1], scenario))
    # Inter-style negotiations
    for population_name in populations:
        active = False
        for population_name_2 in populations:
            if active:
                for i in range(len(populations[population_name])):
                    negotiations.append((populations[population_name][i], populations[population_name_2][i], scenario))
            elif population_name_2 == population_name:
                active = True
    # Simulate negotiations
    with Pool() as p:
        negotiation_results = p.starmap(cross_negotiate, negotiations)
    # Process results (Update fitness values of agent and generate stats)
    fitness_matrix = {}
    for population_name in populations:
        for population_name_2 in populations:
            fitness_matrix[(population_name, population_name_2)] = 0.0
    accepts_matrix = {}
    rejects_matrix = {}
    time_matrix = {}
    for population_name in populations:
        active = False
        for population_name_2 in populations:
            if population_name_2 == population_name:
                active = True
            if active:
                accepts_matrix[frozenset([population_name, population_name_2])] = 0
                rejects_matrix[frozenset([population_name, population_name_2])] = 0
                time_matrix[frozenset([population_name, population_name_2])] = 0
    for negotiation, result in zip(negotiations, negotiation_results):
        negotiation[0].fitness += result[0]
        negotiation[1].fitness += result[1]
        fitness_matrix[(negotiation[0].style, negotiation[1].style)] += result[0]
        fitness_matrix[(negotiation[1].style, negotiation[0].style)] += result[1]
        style_combination = frozenset([negotiation[0].style, negotiation[1].style])
        accepts_matrix[style_combination] += result[2]
        rejects_matrix[style_combination] += result[3]
        time_matrix[style_combination] += result[4]
    return fitness_matrix, accepts_matrix, rejects_matrix, time_matrix