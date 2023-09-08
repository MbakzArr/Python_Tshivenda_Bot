# import wikipedia_histories

# def venda_history():
#     print("The bot ")
#     wiki = wikipedia_histories.get_history("Venda")
#     return wiki[200].content

import os
import json

# Get the current working directory
current_dir = os.getcwd()

# Path to the "history" directory
dataset_dir = os.path.join(current_dir, 'history')

# Path to the "venda.json" file within the "history" directory
file = os.path.join(dataset_dir, 'venda.json')

# Load responses from the JSON file
with open(file, 'r', encoding='utf-8') as json_file:
    responses = json.load(json_file)

# Get the headers from the json
headers = responses['headers']


# Function to generate a response
def venda_history():
    return f"""
    Village: {headers['title']}
    Location: {headers['location']}
    Founded: {headers['founded_as']}
    Declaration: {headers['declaration_dates']}
    First president: {headers['leadership']['first_president']}
    Education: {headers['educational_institution']}
    About: {responses['text']}
    """


# Sub headers for the geography
sub_headers = headers['geography']


def geography():
    return f"""
    Territories: {sub_headers['territories']}
    Capital: {sub_headers['capital']}
    Area: {sub_headers['land_area_km2']}
    Population[1991]: Estimated of {sub_headers['population_1991']}
    Areas: {headers['geographical_features']['areas']}
    Wildlife: {headers['geographical_features']['wildlife']}
    """
