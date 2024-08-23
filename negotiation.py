from agent import Agent
from negotiationGenerator.scenario import Scenario

import tensorflow as tf

#This file contains the logic to simulate the negotiation between two agents

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
        utility_a += result_one_hot[x] * offer_utilities_a[x]
        utility_b += result_one_hot[x] * offer_utilities_b[x]
    return utility_a, utility_b

#Negotiation outcome returned the form (result, utility_1, utility_2, time)
def negotiate(agent_a: Agent, agent_b: Agent, negotiation_scenario: Scenario, timeout: int) -> tuple[int, float, float, int]:
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
    while ongoing and time <= timeout:
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
            offer_one_hot = encode_as_one_hot(ret_b[0][3:].numpy())
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
                offer_one_hot = encode_as_one_hot(ret_a[0][3:].numpy())
                offer = tf.constant([[[*offer_one_hot, *offer_utilities_a]]])
    agent_a.model.layers[1].reset_states()
    agent_b.model.layers[1].reset_states()
    #print(f"Negotiation between {agent_a} and {agent_b} came to the outcome {outcome} at t={time} with utility_a={result_utility_a} and utility_b={result_utility_b}")
    return outcome, result_utility_a, result_utility_b, time