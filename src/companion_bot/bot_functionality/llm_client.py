import os
from openai import OpenAI
from dotenv import load_dotenv



# when caling this use self.latest_emotion to get the detected emotion.
def generate_response(user_text, detected_emotion, conversation_history):

    load_dotenv()
    api_key = os.getenv("openAI_api_key")
    if api_key is None:
        raise ValueError("API key is not set")

    client = OpenAI(api_key=api_key)
    print("Client is ready")

    with open("bot_personality.txt", "r") as f:
        bot_prompt = f.read()

    with open(conversation_history, "r") as f:
        conv_hist = f.read()

    with open("important_memories.txt","r") as f:
        important = f.read()

    llm_input = f"{bot_prompt}, Conversation history = {conv_hist}, Important memories = {important}"

    user_input = f"Detected Emotion = {detected_emotion},  User input = {user_text}"

    comp = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[{"role":"system","content":llm_input}, {"role":"user", "content":user_input}],

    )

    response = comp.choices[0].message.content

    if not response:
        raise ValueError("LLM returned an empty response")

    parts = response.split(",", 3)
    if len(parts) == 4:
        important = parts[0].strip()
        emotion = parts[1].lower().strip()
        gesture = parts[2].lower().strip()
        response = parts[3].strip()
    else:
        raise ValueError(f"Invalid LLM response: {response}")

    if important == "1":
        with open("important_memories.txt", "a") as f:
            f.write(f"- {user_input}")

    with open(conversation_history, "a") as f:
        f.write(f"- User - {user_input}\n")
        f.write(f"- system - {response}\n")



    return response, emotion, gesture

def clear_conversaton_history(conversation_history):

    open(conversation_history, "w").close()

    return