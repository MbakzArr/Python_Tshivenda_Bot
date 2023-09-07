import random
import json
import os

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
def get_response(_input):
    for key, value in responses.items():
        if key.lower() in _input.lower():
            return random.choice(value)
    return "Thi khou vha pfesesa."


# Main chat loop
print(
    "ChatBot: Ndaa! Kha vha nwale nga luisimani zwine vha khou toda zwi tshi nwaliwa nga Tshivenda. (Kha vha nwale (Ndi zwone ), u fhedza nyambedzano)")
while True:
    _input = input("You: ")
    if _input.lower() == "ndi zwone":
        print("ChatBot: Zwavhudi!")
        break
    response = get_response(_input)
    print("Translation (English-Tshivenda):", response)
