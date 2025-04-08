from pymongo import MongoClient, ASCENDING
from datetime import datetime
from langchain_core.messages import AIMessage, SystemMessage,HumanMessage



connection_string = "mongodb+srv://saviamir353:Asfamily786@cluster0.vxo0we6.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0"

def save_chat(data:dict):
    data['timestamp'] = datetime.now()
    with MongoClient(connection_string) as client:
        client['chatbot']['chat'].insert_one(data) 

def fetch_chat(user_id:str):
    with MongoClient(connection_string) as client:
        data = list(client['chatbot']['chat'].find({'user_id':user_id}).sort('timestamp', ASCENDING))

    messages = []

    for message in data:
        if message['role'] == 'assistant':
            messages.append(AIMessage(message['content']))
        elif message['role'] == 'user':
            messages.append(HumanMessage(message['content']))
    
    return messages
