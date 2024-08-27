import os

os.environ["TF_CPP_MIN_LOG_LEVEL"] = "1"

import json

import asyncio
from websockets.asyncio.server import serve
from websockets import ConnectionClosedOK

from keras import models
import tensorflow as tf

from negotiationGenerator.discreteGenerator import build_negotiation_scenario
from negotiationGenerator.scenario import Scenario
from negotiation import encode_as_one_hot



async def handler(websocket):
    try:
        model_name = await websocket.recv()
    except ConnectionClosedOK:
        return
    if model_name in ['accommodating', 'collaborating', 'compromising', 'avoiding', 'competing']:
        model = models.load_model(f"models/{model_name}.keras")
        scenario: Scenario = build_negotiation_scenario([5,5,5,5,5])
        # Websocket client plays as b
        await websocket.send(json.dumps({
            "message_type": "perspective",
            "issues": scenario.b.get_issues()
        }))
        #Dummy loop to extend negotiation length, TODO remove when models ready
        for i in range(3):
            await websocket.recv()
            await websocket.send(json.dumps({
                "message_type": "offer",
                "values": [i,i,i,i,i]
            }))
        async for message_json in websocket:
            message = json.loads(message_json)
            print(f"New message {message}")
            if message["type"] == "offer":
                offer_one_hot = []
                for choice in message["values"]:
                    choice_one_hot = [0,0,0,0,0]
                    choice_one_hot[choice] = 1
                    offer_one_hot.extend(choice_one_hot)
                offer = tf.constant([[[*offer_one_hot, *scenario.a.get_utility_array()]]])
                ret = model(offer)
                print(f"Ret {ret}")
                continue_negotiation = ret[0][0].numpy() >= ret[0][1].numpy() and ret[0][0].numpy() >= ret[0][2].numpy()
                if continue_negotiation:
                    values = []
                    ret_one_hot = encode_as_one_hot(scenario.a.get_utility_array())
                    print(ret_one_hot)
                    issue_length = 5
                    for i in range(0, len(ret_one_hot), issue_length):
                        values.append(ret_one_hot[i:i+issue_length].index(1))
                    print(f"Values {values}")
                    await websocket.send(json.dumps({
                        "message_type": "offer",
                        "values": values
                    }))
                else:
                    accept = ret[0][1].numpy() > ret[0][2].numpy()
                    print(f"End with accept {accept}")
                    await websocket.send(json.dumps({
                        "message_type": "accept" if accept else "reject"
                    }))
                    return
            else:
                return

async def main_app():
    async with serve(handler, "", 8001):
        await asyncio.get_running_loop().create_future()  # run forever

if __name__ == '__main__':
    print("Websocket active")
    asyncio.run(main_app())