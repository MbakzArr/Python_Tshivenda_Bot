from news.news import get_random_news
from history.history import venda_history, geography
from translation.translate import translation

# Main chat loop
print(
    "ChatBot: Ndaa! Kha vha nwale nga luisimani zwine vha khou toda zwi tshi nwaliwa nga Tshivenda. (Kha vha nwale ("
    "Ndi zwone ), u fhedza nyambedzano)")
while True:
    _input = input("You: ").lower().strip()
    if _input == "ndi zwone":
        print("ChatBot: Zwavhudi!")
        break
    elif _input.startswith("/translate"):
        if _input.replace("/translate", "").strip() == "":
            print("No word found. Try again [e.g /translate Welcome]")
        else:
            print("Translation (English-Tshivenda):", translation(_input.replace("/translate", "").strip()))
    elif _input == "/news":
        print(get_random_news())
    elif _input.startswith("/learn"):
        if _input.replace("/learn", "").strip() == "venda":
            print(venda_history())
        elif _input.replace("/learn", "").strip() == "geography":
            print(geography())
        else:
            print("Custom topic is not yet implemented")
    else:
        print("Command could not be found.")
