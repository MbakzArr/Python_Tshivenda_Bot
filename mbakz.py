import random


responses = {
    ("How are you?",): ["Hurini?"],
    ("I am fine.", "I'm Good"): ["Ndi hone", "Ndo twa zwavhudi" , "ndo twa zwavhudi"],
    ("How was your night?",): ["No edela hani?"],
    ("I slept well.",): ["Ndo edela zwavhudi"],
    ("What are you doing?",): ["Ni khou itani?"],
    ("I am bored.",): ["Ndi khou borea"],
    ("How was work?",): ["No shuma hani?"],
    ("It was good.",): ["Ndo shuma zwavhudi"],
    ("I'm going to buy bread.",): ["Ndi khou ya u renga vhurotho"],
    ("Yesterday I was ill.",): ["Mulovha ndo vha ndi khou lwala"],
    ("Last year I passed standard ten.",): ["Mahola ndo phasa murole wa fumi"],
    ("I will get married by a Venda.",): ["Ndi do maliwa nga Muvenda"],
    ("I'm a God's messenger.",): ["Nne ndi murunwa wa Mudzimu"],
    ("A tall man beat his child.",): ["Munna mulapfu o rwa nwana wawe"],
    ("My cousin is coming tomorrow.",): ["Muzwala wanga u khou da matshelo"],
    ("We will meet there.",): ["Ri do tangana hanenge"],
    ("Call me when you leave.",): ["Ni foune ni tshi takuwa"],
    ("Today is my birthday.",): ["Namusi ndi duvha langa la mabebo"],
    ("Family",): ["Muta"],
    ("Father",): ["Khotsi"],
    ("Mother",): ["Mme"],
    ("Brother",): ["Mukomana"],
    ("Sister",): ["Khaladzi"],
    ("Grandparents",): ["Makhulu"],
    ("Greetings",): ["U lumelisa"],
    ("Good morning",): ["Ndi Matsheloni"],
    ("Afternoon",): ["Ndi masiari"],
    ("Evening",): ["Ndi madekwana"],
    ("Hello (Male)",): ["Nnda!"],
    ("Hello (Female)",): ["Aa!"],
    ("Day to day words",): ["Maipfi a duvha na duvha"],
    ("Foods", "food"): ["Zwiliwa"],
    ("Water",): ["Madi"],
    ("Hunger",): ["Ndala (I am hungry-Ndi na ndala)"],
    ("House",): ["Nndu"],
    ("Gate",): ["Gethe"],
    ("Love",): ["Lufuno (I love you- Ndi a ni funa)"],
    ("Keep visiting",): ["Ni dale hafhu"],
    ("Lovers words",): ["Maipfi a vhafunani"],
    ("Mufunwa",): ["Love"],
    ("Mufunwawanga",): ["My love"],
    ("Dingalambiluyanga",): ["My sweetheart"],
    ("Muthuwanga",): ["My lover"],
    ("I'm going to buy bread.",): ["Ndi khou ya u renga vhurotho"],
    ("Yesterday I was ill (or sick).",): ["Mulovha ndo vha ndi khou lwala"],
    ("Last year I passed standard ten.",): ["Mahola ndo phasa murole wa fumi"],
    ("I will get married by (or to) a Venda.",): ["Ndi do maliwa nga Muvenda"],
    ("I'm a God's messenger (or angel).",): ["Nne ndi murunwa wa Mudzimu"],
    ("A tall man beat his child.",): ["Munna mulapfu o rwa nwana wawe"],
    ("My cousin is coming tomorrow.",): ["Muzwala wanga u khou da matshelo"],
    ("We will meet there.",): ["Ri do tangana hanenge"],
    ("Call me when you leave.",): ["Ni foune ni tshi takuwa"],
    ("Today is my birthday.",): ["Namusi ndi duvha langa la mabebo"],
    ("Body Parts in Tshivenda",): ["Mirado ya muvhili nga Tshivenda"],
    ("Head",): ["Thoho"],
    ("Hair",): ["Mavhudzi"],
    ("Gray Hair",): ["Mmvi"],
    ("Ears",): ["Ndevhe"],
    ("Eyelashes",): ["Tsie"],
    ("Eyebrow",): ["Tsie"],
    ("Eyes",): ["Mato"],
    ("Nose",): ["Ningo"],
    ("Mouth",): ["Mulomo"],
    ("Cheek",): ["Marama"],
    ("Jaw",): ["Lutaha"],
    ("Forehead",): ["Tshikuma"],
    ("Back of the head",): ["Tshitiko"],
    ("Chin",): ["Tshitefu"],
    ("Beard",): ["Ndebvu"],
    ("Teeth",): ["Mano"],
    ("Tongue",): ["Lulimi"],
    ("Throat",): ["Mukulo"],
    ("Neck",): ["Mutsinga"],
    ("Shoulders",): ["Mahada"],
    ("Chest",): ["Khana"],
    ("Elbow",): ["Tshikudavhavha"],
    ("Arm & Hand",): ["Tshanda"],
    ("Fingers",): ["Minwe"],
    ("Nails",): ["Nala"],
    ("Stomach",): ["Thumbu"],
    ("Back",): ["Mutana"],
    ("Waist/Hips",): ["Khundu"],
    ("Reproductive organs",): ["Vhudzimu"],
    ("Buttocks.",): ["Maraho"],
    ("Thighs",): ["Zwirumbi"],
    ("Calves",): ["Thafu"],
    ("Knee",): ["Gona"],
    ("Leg & Foot",): ["Mulendzhe"],
    ("Toes",): ["Zwikunwane"],
    ("Heel",): ["Tshirethe"],
    ("Skin",): ["Lukanda"],
    ("Table",): ["Tafula"]  



}



# Function to generate a response
def get_response(user_input):
    user_input = user_input.lower()
    for key_tuple, value in responses.items():
        for key in key_tuple:
            if key.lower() in user_input:
                return random.choice(value)
    return "Thi khou vha pfesesa."

# Main chat loop
print("ChatBot: Ndaa! Kha vha nwale nga luisimani zwine vha khou toda zwi tshi nwaliwa nga Tshivenda. (Kha vha nwale (Ndi zwone ), u fhedza nyambedzano)")
while True:
    user_input = input("You: ")
    if user_input.lower() == "ndi zwone":
        print("ChatBot: Zwavhudi!")
        break
    response = get_response(user_input.lower())
    print("Translation (Eng-Tshiv):", response)
