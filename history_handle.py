# ====== Import library ======
from langchain_community.chat_message_histories import StreamlitChatMessageHistory
from langchain.memory import ConversationBufferWindowMemory

from utils import get_timestamp, get_keyword_name

import yaml
import json
import os
# ====== Load configuration ======
with open("history_config.yml","r") as f:
    history_config = yaml.safe_load(f)
    
# ====== History Retrieve ======
def get_chat_memory(chat_history):
    return ConversationBufferWindowMemory(memory_key="history", chat_memory=chat_history, k=history_config["history_k_retrieve"])

# ====== History Create ======
def get_new_history(key="history"):
    return StreamlitChatMessageHistory(key=key)

def create_history_with_json(history_json):
    history = StreamlitChatMessageHistory(key="history")
    for message in history_json:
        if message["type"] == "human":
            history.add_user_message(message["content"])
        elif message["type"] == "ai":
            history.add_ai_message(message["content"])
    return history

# ====== Get List Names ======
def get_list_names():
    list_names = []
    folder_path = history_config["history_path"]
    for filepath in os.listdir(folder_path):
        if filepath.endswith(".json"):
            with open(folder_path+filepath, 'r') as f:
                save_pattern = json.load(f)
                list_names.append(save_pattern["history_name"])
    return list_names

# ====== Get History ID ======
def get_history_id(history_name):
    folder_path = history_config["history_path"]
    for filepath in os.listdir(folder_path):
        if filepath.endswith(".json"):
            with open(folder_path+filepath, 'r') as f:
                save_pattern = json.load(f)
                if save_pattern["history_name"] == history_name:
                    return save_pattern["history_id"] 
    return None

# ====== Custom history class ======
class CustomHistory:
    def __init__(self):
        self.history = get_new_history(key="history")
        self.history_name = "New Session"
        self.history_id = get_timestamp()
        
    def update_name(self):
        if len(self.history.messages) > 0 and self.history_name=="New Session":
            new_name = get_keyword_name(self.history.messages[0].content)
            list_names = get_list_names()
            if new_name in list_names:
                new_name += " #"
                i=2
                while True:
                    name = new_name + str(i)
                    if name not in list_names:
                        self.history_name = name
                        break
                    i+=1
            else:
                self.history_name = new_name
            
    def add_a_conversation(self, user_message:str, ai_message:str):
        self.history.add_user_message(user_message)
        self.history.add_ai_message(ai_message)
        self.update_name()
        self.save()
        
    def load(self, history_id):
        filepath = history_config["history_path"] + history_id + ".json"
        if os.path.exists(filepath):
            with open(filepath, 'r') as f:
                save_pattern = json.load(f)
                self.history = create_history_with_json(save_pattern['history_conversations'])
                self.history_name = save_pattern['history_name']
                self.history_id = save_pattern['history_id']
        else:
            raise ValueError("Không tồn tại lịch sử trò chuyện này!")
            
    def save(self):
        history_json = [message.dict() for message in self.history.messages]
        save_pattern = {
            "history_name": self.history_name,
            "history_id": self.history_id,
            "history_conversations": history_json
        }
        filepath = history_config["history_path"] + self.history_id + ".json"
        with open(filepath, 'w') as f:
            json.dump(save_pattern, f, indent=4)
        





