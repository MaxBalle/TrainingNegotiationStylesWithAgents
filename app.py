import os
import time

os.environ["TF_CPP_MIN_LOG_LEVEL"] = "1"

import json
import random
import secrets

import asyncio
from websockets.asyncio.server import serve
from websockets import ConnectionClosedOK

from keras import models
import tensorflow as tf

from negotiationGenerator.discreteGenerator import build_negotiation_scenario
from negotiationGenerator.scenario import Scenario
from negotiation import encode_as_one_hot

model_options = ['accommodating', 'collaborating', 'compromising', 'avoiding', 'competing']
negotiation_shape = [5, 5, 5, 5, 5]

def build_response_from_model_return(ret, issue_shape):
    # continue_negotiation = ret[0][0].numpy() >= ret[0][1].numpy() and ret[0][0].numpy() >= ret[0][2].numpy() TODO re-enable once models are ready
    continue_negotiation = random.random() < 0.8  # TODO remove
    if continue_negotiation:
        values = []
        ret_one_hot = encode_as_one_hot(ret[0][3:].numpy(), issue_shape, flat=False)
        # print(ret_one_hot)
        for issue in ret_one_hot:
            values.append(issue.index(1))
        # print(f"Values {values}")
        return {
            "message_type": "offer",
            "values": values
        }
    else:
        accept = ret[0][1].numpy() > ret[0][2].numpy()
        print(f"Ended by model with accept={accept}")
        outcome = "accept" if accept else "reject"
        return {
            "message_type": "end",
            "outcome": outcome
        }

async def perform_model_negotiation(websocket, model_name, scenario: Scenario, model_role, model_starting = False, delay_max=0):
    model = models.load_model(f"models/{model_name}.keras")
    if model_starting:
        #Simulate a perfect utility first offer by client to query model
        client_perspective = scenario.get_perspective("b" if model_role == "a" else "a")
        initial_offer_one_hot = []
        for issue in client_perspective.get_issues():
            for option in issue[1]:
                initial_offer_one_hot.append(1.0 if option == 1 else 0.0)
        offer_utilities_model = scenario.get_perspective(model_role).get_utility_array()
        offer = tf.constant([[[*initial_offer_one_hot, *offer_utilities_model]]])
        ret = model(offer)
        response = build_response_from_model_return(ret, scenario.issue_shape)
        await websocket.send(json.dumps(response))
        if response["message_type"] == "end":
            return response["outcome"], "model"
    async for message_json in websocket:
        message = json.loads(message_json)
        print(f"New message in model negotiation {message}")
        if message["message_type"] == "offer":
            offer_one_hot = []
            for choice in message["values"]:
                choice_one_hot = [0, 0, 0, 0, 0]
                choice_one_hot[choice] = 1
                offer_one_hot.extend(choice_one_hot)
            offer = tf.constant([[[*offer_one_hot, *scenario.get_perspective(model_role).get_utility_array()]]])
            ret = model(offer)
            response = build_response_from_model_return(ret, scenario.issue_shape)
            if delay_max > 0:
                time.sleep(random.uniform(delay_max / 2, delay_max))
            await websocket.send(json.dumps(response))
            if response["message_type"] == "end":
                return response["outcome"], "model"
        elif message["message_type"] == "end":
            outcome = message["outcome"]
            print(f"Client ended with outcome={outcome}")
            return outcome, "client"
    return "error", "client"

async def handle_model_negotiation(websocket, model_name):
    scenario: Scenario = build_negotiation_scenario(negotiation_shape)
    model_role = random.choice("ab")
    await websocket.send(json.dumps({
        "message_type": "init",
        "issues": scenario.get_perspective("b" if model_role == "a" else "a").get_issues(),
        "timeout": None,
        "start": True
    }))
    return await perform_model_negotiation(websocket, model_name, scenario, model_role)

turing_wait = []
turing_pairs = {}
seconds = 60 #Timelimit for each offer

async def handle_turing(websocket):
    if turing_wait:
         code, role = turing_wait.pop()
         print(f"Connected to waiting {code}")
         turing_pairs[code][role] = websocket
         opponent_role = "b" if role == "a" else "a"
         await websocket.send(json.dumps({
             "message_type": "init",
             "issues": turing_pairs[code]["scenario"].get_perspective(role).get_issues(),
             "timeout": seconds,
             "start": role == turing_pairs[code]["starting_role"]
         }))
         await turing_pairs[code][opponent_role].send(json.dumps({
             "message_type": "init",
             "issues": turing_pairs[code]["scenario"].get_perspective(opponent_role).get_issues(),
             "timeout": seconds,
             "start": opponent_role == turing_pairs[code]["starting_role"]
         }))
    else:
        code = secrets.token_urlsafe()
        role = random.choice("ab")
        opponent_role = "b" if role == "a" else "a"
        print(f"Wait for connection with {code}")
        turing_wait.append((code, opponent_role))
        turing_pairs[code] = {
            "scenario": build_negotiation_scenario(negotiation_shape),
            role: websocket,
            "starting_role": random.choice("ab"),
            "models_as_opponents": random.choice([True, False])
        }
    if turing_pairs[code]["models_as_opponents"]:
        #Case separate against a model
        model_name = random.choice(model_options)
        print(f"{code} role {role} is model negotiation against {model_name}")
        outcome, ending_party = await perform_model_negotiation(websocket, model_name, turing_pairs[code]["scenario"], opponent_role, model_starting=opponent_role == turing_pairs[code]["starting_role"], delay_max = seconds)
        try:
            judgment_message_json = await websocket.recv()
        except ConnectionClosedOK:
            return
        judgment_message = json.loads(judgment_message_json)
        judgment = judgment_message["judgment"]
        return "AI", judgment
    else:
        # Case human vs. human
        async for message_json in websocket:
            message = json.loads(message_json)
            print(f"New turing message {message}")
            if message["message_type"] == "offer":
                await turing_pairs[code][opponent_role].send(json.dumps({
                    "message_type": "offer",
                    "values": message["values"]
                }))
            elif message["message_type"] == "end":
                outcome = message["outcome"]
                await turing_pairs[code][opponent_role].send(json.dumps({
                    "message_type": "end",
                    "outcome": outcome
                }))
                print(f"{role} ended with {outcome}")
            elif message["message_type"] == "judgment":
                return "Person", message["judgment"]
        return "Person", "Missing Judgment"

async def handler(websocket):
    try:
        message_json = await websocket.recv()
    except ConnectionClosedOK:
        return
    message = json.loads(message_json)
    print(f"New message {message}")
    if message["message_type"] == "init":
        mode = message["mode"]
        if mode == "sandbox":
            model_name = message["model"]
            outcome, ending_party = await handle_model_negotiation(websocket, model_name)
        elif mode == "identification":
            model_name = random.choice(model_options)
            outcome, ending_party = await handle_model_negotiation(websocket, model_name)
            try:
                judgment_message_json = await websocket.recv()
            except ConnectionClosedOK:
                return
            judgment_message = json.loads(judgment_message_json)
            judgment = judgment_message["judgment"]
            print(f"Client judged model as {judgment}, truth is {model_name}")
            await websocket.send(json.dumps({
                "message_type": "disclosure",
                "model": model_name
            }))
        elif mode == "turing":
            opponent_type, judgment = await handle_turing(websocket)
            print(f"Client judged model as {judgment}, truth is {opponent_type}")
            await websocket.send(json.dumps({
                "message_type": "disclosure",
                "opponent": opponent_type
            }))
        else:
            await websocket.send(json.dumps({
                "message_type": "error",
                "error": "No such mode"
            }))
            return
    else:
        await websocket.send(json.dumps({
            "message_type": "error",
            "error": "First message must be init"
        }))

async def main_app():
    async with serve(handler, "", 8001):
        await asyncio.get_running_loop().create_future()  # run forever

if __name__ == '__main__':
    print("Websocket active")
    asyncio.run(main_app())