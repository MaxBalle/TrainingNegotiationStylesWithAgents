import os

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

async def handle_model_negotiation(websocket, model_name):
    scenario: Scenario = build_negotiation_scenario(negotiation_shape)
    #Model plays as a, websocket client as b
    await websocket.send(json.dumps({
        "message_type": "init",
        "issues": scenario.b.get_issues(),
        "timeout": None,
        "start": True
    }))
    model = models.load_model(f"models/{model_name}.keras")
    async for message_json in websocket:
        message = json.loads(message_json)
        print(f"New message in model negotiation {message}")
        if message["message_type"] == "offer":
            offer_one_hot = []
            for choice in message["values"]:
                choice_one_hot = [0, 0, 0, 0, 0]
                choice_one_hot[choice] = 1
                offer_one_hot.extend(choice_one_hot)
            offer = tf.constant([[[*offer_one_hot, *scenario.a.get_utility_array()]]])
            ret = model(offer)
            print(f"Ret {ret}")
            # continue_negotiation = ret[0][0].numpy() >= ret[0][1].numpy() and ret[0][0].numpy() >= ret[0][2].numpy() TODO re-enable once models are ready
            continue_negotiation = random.random() < 0.8  # TODO remove
            if continue_negotiation:
                values = []
                ret_one_hot = encode_as_one_hot(ret[0][3:].numpy(), scenario.issue_shape, flat=False)
                print(ret_one_hot)
                for issue in ret_one_hot:
                    values.append(issue.index(1))
                print(f"Values {values}")
                await websocket.send(json.dumps({
                    "message_type": "offer",
                    "values": values
                }))
            else:
                accept = ret[0][1].numpy() > ret[0][2].numpy()
                print(f"Ended by model with accept={accept}")
                outcome = "accept" if accept else "reject"
                await websocket.send(json.dumps({
                    "message_type": "end",
                    "outcome": outcome
                }))
                return outcome, "model"
        elif message["message_type"] == "end":
            outcome = message["outcome"]
            print(f"Client ended with outcome={outcome}")
            return outcome, "client"

turing_wait = []
turing_pairs = {}
seconds = 60 #Timelimit for each offer

async def handle_turing(websocket):
    if turing_wait:
         code = turing_wait.pop()
         print(f"Connected to waiting {code}")
         turing_pairs[code]["b"] = websocket
         role = "b"
         opponent_role = "a"
    else:
        code = secrets.token_urlsafe()
        print(f"Wait for connection with {code}")
        turing_wait.append(code)
        turing_pairs[code] = {
            "scenario": build_negotiation_scenario(negotiation_shape),
            "a": websocket,
            "starting_role": random.choice("ab")
        }
        role = "a"
        opponent_role = "b"
    # Random 50-50 negotiate against model here
    await websocket.send(json.dumps({
        "message_type": "init",
        "issues": turing_pairs[code]["scenario"].get_perspective(role).get_issues(),
        "timeout": seconds,
        "start": role == turing_pairs[code]["starting_role"]
    }))
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
        elif mode == "turing":
            opponent_type, judgment = await handle_turing(websocket)
            print(f"Client judged model as {judgment}, truth is {opponent_type}")
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