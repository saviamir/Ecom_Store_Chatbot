import os
from dotenv import load_dotenv
load_dotenv()

from langchain_openai import ChatOpenAI
from langchain_core.messages import AIMessage, SystemMessage,HumanMessage,ToolMessage
from langchain_core.tools import tool
from datetime import datetime
from weather import get_weather
from data_retriever import pdf_database,csv_database,web_database
from mongo_service import save_chat,fetch_chat
from typesense_service import search_products


@tool
def get_latest_datetime():
    """
    Returns the latest date and time as a formatted string.
    Format: YYYY-MM-DD HH:MM:SS
    """
    current_datetime = datetime.now()
    return current_datetime.strftime("%Y-%m-%d %H:%M:%S")

@tool
def get_latest_weather(location_name):
    """
    Returns the latest weather information for a given location.
    """
    return get_weather(location_name)


@tool
def search_store_products(question: str):
    """
    Search for products in the store using a question string.
    Useful when the user is looking for a specific product.
    """
    results = search_products(question)
    return results


@tool
def get_pdf_data(question):
    """
    Returns the data from the pdf files : data is about EMR records
    """
    return pdf_database(question)

@tool
def get_csv_data(question):
    """
    Returns the data from the csv files : data is about product database for buysavvy.co ecom store.
    """
    return csv_database(question)

@tool
def get_web_data(question):
    """
    Returns the data from the web pages : data is about news
    """
    return web_database(question)


tools = [
    get_latest_datetime,
    get_latest_weather,
    get_pdf_data,
    get_csv_data,
    get_web_data,
    search_store_products 
    ]

llm = ChatOpenAI(
    temperature=0.5,
).bind_tools(tools)

PROMPT = """You are a smart and helpful AI chatbot for an ecommerce store: https://buysavvy.co/

Your goal is to assist users in finding the right products, answering their queries, and improving their shopping experience. You should always:
- Be polite, engaging, and helpful.
- Recommend products based on user input.
- Retrieve product details, prices, and availability from the store database.
- Answer frequently asked questions related to orders, payments, and delivery.
- If a user asks about a discount, mention: "Sign up on our store to get 5% off!"
- If a user asks for product recommendations, suggest 2-3 relevant items from the store.
- If the user abandons a cart, remind them about it and offer assistance.
- If you do not know an answer, politely redirect them to customer support.

Follow a conversational style to engage users and keep responses relevant to shopping. Avoid discussing unrelated topics.
"""

def chat(user_id, question):
    messages = [SystemMessage(PROMPT)]

    messages.extend(fetch_chat(user_id))

    messages.append(HumanMessage(question))

    response = llm.invoke(messages)
    messages.append(response)

    if response.tool_calls:
        for tool_call in response.tool_calls:
            if tool_call['name'] == 'get_latest_datetime':
                messages.append(ToolMessage(get_latest_datetime.invoke(input=""),tool_call_id=tool_call['id']))
            elif tool_call['name'] == 'get_latest_weather':
                location_name = tool_call['args']['location_name']
                messages.append(ToolMessage(get_latest_weather.invoke(input=location_name),tool_call_id=tool_call['id']))
            elif tool_call['name'] == 'get_pdf_data':
                question = tool_call['args']['question']
                messages.append(ToolMessage(get_pdf_data.invoke(input=question),tool_call_id=tool_call['id']))
            elif tool_call['name'] == 'get_csv_data':
                question = tool_call['args']['question']
                messages.append(ToolMessage(get_csv_data.invoke(input=question),tool_call_id=tool_call['id']))
            elif tool_call['name'] == 'get_web_data':
                question = tool_call['args']['question']
                messages.append(ToolMessage(get_web_data.invoke(input=question),tool_call_id=tool_call['id']))
            elif tool_call['name'] == 'search_store_products':
                question = tool_call['args']['question']
                messages.append(ToolMessage(search_store_products.invoke(input=question), tool_call_id=tool_call['id']))

                
        response = llm.invoke(messages)
        messages.append(response)

    # save user chat
    save_chat({
        'user_id': user_id,
        'role': 'user',
        'content': question
    })
     
    # save ai chat
    save_chat({
        'user_id': user_id,
        'role': 'assistant',
        'content': response.content
    })
    return response.content

if __name__ == "__main__":
    user_id = "test_user"
    print("🛍️ Welcome to BuySavvy! I Will Be Your AI Assistant, Echo!")
    print("💬 Ask me anything about products, orders, or deals.")
    print("🛑 Type 'end' to finish the conversation.\n")

    while True:
        question = input("You: ").strip()
        if question.lower() == 'end':
            print("👋 Goodbye! Thanks for visiting BuySavvy. Come back soon!")
            break
        response = chat(user_id, question)
        print("Echo:", response)
