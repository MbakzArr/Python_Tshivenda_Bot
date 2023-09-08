import os
import random
import json

# Get the current working directory
current_dir = os.getcwd()

# Path to the "dataset" directory
dataset_dir = os.path.join(current_dir, 'dataset')

# Path to the "responses.json" file within the "dataset" directory
file = os.path.join(dataset_dir, 'response.json')

# Load responses from the JSON file
with open(file, 'r', encoding='utf-8') as json_file:
    responses = json.load(json_file)


# Function to generate a response
def translation(_input):
    for key, value in responses.items():
        if key.lower() in _input and key.lower() == _input:
            return random.choice(value)
    return "Thi khou vha pfesesa."