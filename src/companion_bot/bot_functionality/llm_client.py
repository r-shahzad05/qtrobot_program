import os
from openai import OpenAI
from dotenv import load_dotenv




def generate_response(user_text, detected_emotion, conversation_history):

    load_dotenv()
    api_key = os.getenv("openAI_api_key")
    if api_key is None:
        raise ValueError("API key is not set")

    client = OpenAI(api_key=api_key)
    print("Client is ready")

    with open("bot_personality.txt", "r") as f:
        bot_prompt = f.read()

    with open("conversation_history.txt", "r") as f:
        conv_hist = f.read()

    llm_input = f"{bot_prompt}, Conversation history = {conv_hist}"

    user_input = f"Detected Emotion = {detected_emotion},  User input = {user_text}"

    comp = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[{"role":"system","content":llm_input}, {"role":"user", "content":user_input}],

    )

    response = comp.choices[0].message.content

    parts = response.split(",", 3)
    if len(parts) == 4:
        important = parts[0].strip()
        emotion = parts[1].lower().strip()
        gesture = parts[2].lower().strip()
        response = parts[3].strip()
    else:
        raise ValueError(f"Invalid LLM response: {response}")

    if important == "1":
        with open("bot_personality.txt", "a") as f:
            f.write(f"- {user_input}")

    with open(conversation_history, "a") as f:
        f.write(f"- User - {user_input}\n")
        f.write(f"- system - {response}\n")



    match emotion:
        case "happy":
            qt_emotion = "QT/happy"
        case "sad":
            qt_emotion = "QT/sad"
        case "angry":
            qt_emotion = "QT/angry"
        case "suprised":
            qt_emotion = "QT/suprised"
        case "Confused":
            qt_emotion = "QT/confused"
        case "neutral":
            qt_emotion = "QT/neutral"
        case "concerned":
            qt_emotion = "QT/concerned"
        case _:
            qt_emotion = "invalid"


    match gesture:
        case "happy":
            qt_gesture = "QT/happy"
        case "sad":
            qt_gesture = "QT/sad"
        case "angry":
            qt_gesture = "QT/angry"
        case "suprised":
            qt_gesture = "QT/suprised"
        case "Confused":
            qt_gesture = "QT/confused"
        case "neutral":
            qt_gesture = "QT/neutral"
        case "concerned":
            qt_gesture = "QT/concerned"
        case _:
            qt_gesture = "invalid"


    return response, qt_emotion, qt_gesture

def clear_conversaton_history(conversation_history):

    open(conversation_history, "w").close()

    return