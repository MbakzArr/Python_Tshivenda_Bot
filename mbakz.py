import random

# Define a dictionary of responses
responses = {

    "ndaa hurini": ["eksee vhari mini?"],
    "nne ndi right, vhone?": ["Na nne ndi right mah"],
    "hello": ["Hi there!", "Hello!", "Hey!"],
    "how are you": ["I'm good, thanks!", "I'm doing well.", "I'm just a bot, but thanks for asking!"],
    "what's your name": ["My Name is Arrhenius Bot."],
    "bye": ["Goodbye!", "See you later!", "Have a great day!"]
}

# Function to generate a response
def get_response(user_input):
    user_input = user_input.lower()
    for key in responses:
        if key in user_input:
            return random.choice(responses[key])
    return "Thi khou vha pfesesa."

# Main chat loop
print("ChatBot: Hello! Type 'bye' to exit.")
while True:
    user_input = input("You: ")
    if user_input.lower() == "ndi zwone":
        print("ChatBot: Zwavhudi!")
        break
    response = get_response(user_input)
    print("ChatBot:", response)
