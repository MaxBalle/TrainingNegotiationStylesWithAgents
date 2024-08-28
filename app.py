import os

os.environ["TF_CPP_MIN_LOG_LEVEL"] = "1"

import json
import random

import asyncio
from websockets.asyncio.server import serve
from websockets import ConnectionClosedOK

from keras import models
import tensorflow as tf

from negotiationGenerator.discreteGenerator import build_negotiation_scenario
from negotiationGenerator.scenario import Scenario
from negotiation import encode_as_one_hot

model_options = ['accommodating', 'collaborating', 'compromising', 'avoiding', 'competing']

async def handler(websocket):
    initialized = False
    async for message_json in websocket:
        message = json.loads(message_json)
        print(f"New message {message}")
        if message["message_type"] == "init":
            mode = message["mode"]
            if mode == "sandbox":
                model_name = message["model"]
            elif mode == "identification":
                model_name = random.choice(model_options)
            else:
                await websocket.send(json.dumps({
                    "message_type": "error",
                    "error": "No such mode"
                }))
                return
            model = models.load_model(f"models/{model_name}.keras")
            scenario: Scenario = build_negotiation_scenario([5, 5, 5, 5, 5])
            # Websocket client plays as b
            await websocket.send(json.dumps({
                "message_type": "perspective",
                "issues": scenario.b.get_issues()
            }))
            initialized = True
        else:
            if not initialized:
                await websocket.send(json.dumps({
                    "message_type": "error",
                    "error": "Not initialized"
                }))
                return
            if message["message_type"] == "offer":
                offer_one_hot = []
                for choice in message["values"]:
                    choice_one_hot = [0,0,0,0,0]
                    choice_one_hot[choice] = 1
                    offer_one_hot.extend(choice_one_hot)
                offer = tf.constant([[[*offer_one_hot, *scenario.a.get_utility_array()]]])
                ret = model(offer)
                print(f"Ret {ret}")
                #continue_negotiation = ret[0][0].numpy() >= ret[0][1].numpy() and ret[0][0].numpy() >= ret[0][2].numpy() TODO re-enable once models are ready
                continue_negotiation = random.random() < 0.8 #TODO remove
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
                    await websocket.send(json.dumps({
                        "message_type": "accept" if accept else "reject"
                    }))
                    return
            elif message["message_type"] == "end":
                outcome = message["outcome"]
                print(f"Client ended with outcome={outcome}")
                if mode == "identification":
                    judgment = message["judgment"]
                    print(f"Client judged model as {judgment}, truth is {model_name}")
                return
            else:
                await websocket.send(json.dumps({
                    "message_type": "error",
                    "error": "Unknown message_type"
                }))
                return

async def main_app():
    async with serve(handler, "", 8001):
        await asyncio.get_running_loop().create_future()  # run forever

if __name__ == '__main__':
    print("Websocket active")
    asyncio.run(main_app())