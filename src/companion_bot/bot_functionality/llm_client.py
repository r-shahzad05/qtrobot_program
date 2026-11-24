import os
from pathlib import Path
from openai import OpenAI
from dotenv import load_dotenv


class llm_client:
    def __init__(self):
        self.module_dir = Path(__file__).resolve().parent
        load_dotenv(self.module_dir / ".env")
        self.api_key = os.getenv("openAI_api_key")
        if self.api_key is None:
            raise ValueError("API key is not set")
        
        self.client = OpenAI(api_key=self.api_key)


# when caling this use self.latest_emotion to get the detected emotion.
    def generate_response(self,user_text, detected_emotion, conversation_history):


        with open(self.module_dir / "bot_personality.txt", "r") as f:
            bot_prompt = f.read()

        history_path = Path(conversation_history)
        if not history_path.is_absolute():
            history_path = self.module_dir / history_path

        with open(history_path, "r") as f:
            conv_hist = f.read()

        with open(self.module_dir / "important_memories.txt","r") as f:
            important = f.read()

        llm_input = f"{bot_prompt}, Conversation history = {conv_hist}, Important memories = {important}"

        user_input = f"Detected Emotion = {detected_emotion},  User input = {user_text}"

        comp = self.client.chat.completions.create(
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
            with open(self.module_dir / "important_memories.txt", "a") as f:
                f.write(f"- {user_input}")

        with open(history_path, "a") as f:
            f.write(f"- User - {user_input}\n")
            f.write(f"- system - {response}\n")



        return response, emotion, gesture

    def clear_conversaton_history(self,conversation_history):
        history_path = Path(conversation_history)
        if not history_path.is_absolute():
            history_path = self.module_dir / history_path
        history_path.write_text("", encoding="utf-8")

        return