import os

os.environ["TF_CPP_MIN_LOG_LEVEL"] = "1"

import json
import random
import secrets
import csv
import http

import asyncio
from websockets.asyncio.server import serve
from websockets import ConnectionClosedOK, ConnectionClosedError

from keras import models
import tensorflow as tf

from negotiationGenerator.discreteGenerator import build_negotiation_scenario
from negotiationGenerator.scenario import Scenario
from negotiation import encode_as_one_hot

model_options = ['accommodating', 'collaborating', 'compromising', 'avoiding', 'competing']
negotiation_shape = [5, 5, 5, 5, 5]

def save(filename, content):
    with open(f"csv/{filename}.csv", "a", newline="") as csv_file:
        csv_writer = csv.writer(csv_file, dialect='excel')
        csv_writer.writerow(content)

def build_response_from_model_return(ret, issue_shape, allow_end = True):
    if allow_end:
        # continue_negotiation = ret[0][0].numpy() >= ret[0][1].numpy() and ret[0][0].numpy() >= ret[0][2].numpy() TODO re-enable once models are ready
        continue_negotiation = random.random() < 0.8  # TODO remove
    else:
        continue_negotiation = True
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
        outcome = "accept" if accept else "reject"
        return {
            "message_type": "end",
            "outcome": outcome
        }

async def perform_model_negotiation(websocket, code, model_name, scenario: Scenario, model_role, model_starting = False, delay_max=0):
    model = models.load_model(f"models/{model_name}.keras")
    length = 0
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
        response = build_response_from_model_return(ret, scenario.issue_shape, allow_end = False)
        if delay_max > 0:
            delay = random.triangular(5, delay_max, 50)
            await asyncio.sleep(delay)
        await websocket.send(json.dumps(response))
        length += 1
        if response["message_type"] == "end":
            return response["outcome"], "model"
    async for message_json in websocket:
        message = json.loads(message_json)
        print(f"{code}: New message in model negotiation: {message}")
        length += 1
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
                delay = random.triangular(5, delay_max, 30)
                await asyncio.sleep(delay)
            await websocket.send(json.dumps(response))
            length += 1
            if response["message_type"] == "end":
                return response["outcome"], "model", length
        elif message["message_type"] == "end":
            outcome = message["outcome"]
            return outcome, "self", length
    return "error", "", length

async def handle_model_negotiation(websocket, code, model_name):
    scenario: Scenario = build_negotiation_scenario(negotiation_shape)
    model_role = random.choice("ab")
    print(f"{code}: Negotiation against model {model_name} with model_role {model_role}")
    await websocket.send(json.dumps({
        "message_type": "init",
        "issues": scenario.get_perspective("b" if model_role == "a" else "a").get_issues(),
        "timeout": None,
        "start": True
    }))
    return await perform_model_negotiation(websocket, code, model_name, scenario, model_role)

turing_wait = []
turing_pairs = {}
seconds = 100 #Timelimit for each offer

async def handle_turing(websocket, code):
    if turing_wait:
         pairing_code, role = turing_wait.pop()
         print(f"{code} connected to waiting pairing {pairing_code}")
         turing_pairs[pairing_code][role] = websocket
         opponent_role = "b" if role == "a" else "a"
         await websocket.send(json.dumps({
             "message_type": "init",
             "issues": turing_pairs[pairing_code]["scenario"].get_perspective(role).get_issues(),
             "timeout": seconds,
             "start": role == turing_pairs[pairing_code]["starting_role"]
         }))
         await turing_pairs[pairing_code][opponent_role].send(json.dumps({
             "message_type": "init",
             "issues": turing_pairs[pairing_code]["scenario"].get_perspective(opponent_role).get_issues(),
             "timeout": seconds,
             "start": opponent_role == turing_pairs[pairing_code]["starting_role"]
         }))
    else:
        pairing_code = secrets.token_urlsafe()
        role = random.choice("ab")
        opponent_role = "b" if role == "a" else "a"
        print(f"{code} waits for connection with pairing code {pairing_code}")
        turing_wait.append((pairing_code, opponent_role))
        turing_pairs[pairing_code] = {
            "scenario": build_negotiation_scenario(negotiation_shape),
            role: websocket,
            "starting_role": random.choice("ab"),
            "models_as_opponents": random.choice([True, False]),
            # Only for human-human case
            "exchanged_offers": 0
        }
    #Make sure to wait for the init_ack before starting negotiations
    try:
        message_json = await websocket.recv()
    except ConnectionClosedOK:
        return
    message = json.loads(message_json)
    if message["message_type"] == "init_ack":
        print(f"{code} in pairing {pairing_code}: Init acknowledged")
        if turing_pairs[pairing_code]["models_as_opponents"]:
            #Case separate against a model
            model_name = random.choice(model_options)
            print(f"{code} in pairing {pairing_code} has role {role} and is model negotiation against {model_name}")
            outcome, ending_party, length = await perform_model_negotiation(websocket, code, model_name, turing_pairs[pairing_code]["scenario"], opponent_role, model_starting=opponent_role == turing_pairs[pairing_code]["starting_role"], delay_max = seconds)
            print(f"{code} in pairing {pairing_code} negotiation end: Concluded by {ending_party} with the outcome {outcome}")
            try:
                judgement_message_json = await websocket.recv()
            except ConnectionClosedOK:
                return
            judgement_message = json.loads(judgement_message_json)
            judgement = judgement_message["judgement"]
            return outcome, ending_party, length, "AI", judgement
        else:
            # Case human vs. human
            print(f"{code} in pairing {pairing_code} in human-human negotiation")
            async for message_json in websocket:
                message = json.loads(message_json)
                print(f"{code} in pairing {pairing_code}: New turing message {message}")
                turing_pairs[pairing_code]["exchanged_offers"] += 1
                if message["message_type"] == "offer":
                    await turing_pairs[pairing_code][opponent_role].send(json.dumps({
                        "message_type": "offer",
                        "values": message["values"]
                    }))
                elif message["message_type"] == "end":
                    outcome = message["outcome"]
                    turing_pairs[pairing_code]["outcome"] = outcome
                    turing_pairs[pairing_code]["ending_party"] = role
                    await turing_pairs[pairing_code][opponent_role].send(json.dumps({
                        "message_type": "end",
                        "outcome": outcome
                    }))
                    print(f"{code} in pairing {pairing_code}: {role} ended with {outcome}")
                elif message["message_type"] == "judgement":
                    return turing_pairs[pairing_code]["outcome"], "self" if turing_pairs[pairing_code]["ending_party"] == role else "opponent", turing_pairs[pairing_code]["exchanged_offers"], "Person", message["judgement"]
            return "Error", "Error", turing_pairs[pairing_code]["exchanged_offers"], "Error", "Error"
    else:
        await websocket.send(json.dumps({
            "message_type": "error",
            "error": "Missing init_ack"
        }))
        return "AI" if turing_pairs[pairing_code]["models_as_opponents"] else "Person", "Failed init"

async def handler(websocket):
    code = secrets.token_urlsafe()
    print(f"New connection with code {code}")
    try:
        message_json = await websocket.recv()
        init_message = json.loads(message_json)
        print(f"{code}: First message: {init_message}")
        if init_message["message_type"] == "init":
            mode = init_message["mode"]
            if mode == "sandbox":
                model_name = init_message["model"]
                outcome, ending_party, length = await handle_model_negotiation(websocket, code, model_name)
                print(f"{code}: {ending_party} ended after {length} messages with outcome={outcome}")
            elif mode == "identification":
                model_name = random.choice(model_options)
                outcome, ending_party, length = await handle_model_negotiation(websocket, code, model_name)
                print(f"{code}: {ending_party} ended after {length} messages with outcome={outcome}")
                judgement_message_json = await websocket.recv()
                judgement_message = json.loads(judgement_message_json)
                judgement = judgement_message["judgement"]
                print(f"{code} judged model as {judgement}, truth is {model_name}")
                await websocket.send(json.dumps({
                    "message_type": "disclosure",
                    "opponent": model_name
                }))
                save("identification", [code,init_message["person_code"], *init_message["personal_information"].values(), outcome, ending_party, length, model_name, judgement])
            elif mode == "turing":
                outcome, ending_party, length, opponent_type, judgement = await handle_turing(websocket, code)
                print(f"{code} judged model as {judgement}, truth is {opponent_type}")
                await websocket.send(json.dumps({
                    "message_type": "disclosure",
                    "opponent": opponent_type
                }))
                save("turing", [code,init_message["person_code"], *init_message["personal_information"].values(), outcome, ending_party, length, opponent_type, judgement])
            else:
                await websocket.send(json.dumps({
                    "message_type": "error",
                    "error": "No such mode"
                }))
        elif init_message["message_type"] == "questionnaire":
            mode = init_message["mode"]
            save(f"{mode}-questionnaire", [init_message["person_code"],*init_message["personal_information"].values(), *init_message["questions"].values()])
        else:
            await websocket.send(json.dumps({
                "message_type": "error",
                "error": "First message must be init or questionnaire"
            }))
    except ConnectionClosedOK:
        print(f"Connection {code} closed ok")
    except ConnectionClosedError:
        print(f"Connection {code} closed error")
    print(f"Closed connection {code}")

def health_check(connection, request):
    if request.path == "/healthz":
        return connection.respond(http.HTTPStatus.OK, "OK\n")

async def main_app():
    #Headers
    person_fields = ["person_code", "person_age_group", "person_gender", "person_education", "person_negotiation_experience"]
    save("identification", ["connection_code", *person_fields, "outcome", "ending_party", "length", "model_name", "judgement"])
    save("turing", ["connection_code", *person_fields, "outcome", "ending_party", "length", "opponent_type", "judgement"])
    save("identification-questionnaire",[*person_fields, "learning_about_styles", "identification_training", "realism", "theory_of_mind"])
    save("turing-questionnaire", [*person_fields, "certain_of_judgement", "outside_influence"])

    async with serve(handler, "", 8001, process_request=health_check):
        await asyncio.get_running_loop().create_future()

if __name__ == '__main__':
    print("Websocket active")
    asyncio.run(main_app())