import os 

from langchain_community.document_loaders import PyPDFLoader
from langchain_community.document_loaders.csv_loader import CSVLoader   
from langchain_community.document_loaders import WebBaseLoader

from langchain_core.vectorstores import InMemoryVectorStore
from langchain_openai import OpenAIEmbeddings


def pdf_database(question):
    file_path = "files/pdf/"
    pdf = []
    for file in os.listdir(file_path):
        if file.endswith(".pdf"):
            pdf.append(file)
    
    pages = []
    for file in pdf:
        loader = PyPDFLoader(file_path + file)
        pages.extend(loader.load())

    vector_store = InMemoryVectorStore.from_documents(pages, OpenAIEmbeddings())
    documents = vector_store.similarity_search(question)
    return  " ".join([page.page_content for page in documents]) 


def csv_database(question):
    file_path = "files/csv/"
    csv = []
    for file in os.listdir(file_path):
        if file.endswith(".csv"):
            csv.append(file)
    
    pages = []
    for file in csv:
        loader = CSVLoader(file_path + file)
        pages.extend(loader.load())

    vector_store = InMemoryVectorStore.from_documents(pages, OpenAIEmbeddings())
    documents = vector_store.similarity_search(question)
    return  " ".join([page.page_content for page in documents]) 


def web_database(question):
    pages = [
    "https://www.dawn.com/",
    "https://www.bbc.com/"   
    ]

    docs = []
    for page in pages:
        loader = WebBaseLoader(page)
        docs.extend(loader.load())

    vector_store = InMemoryVectorStore.from_documents(docs, OpenAIEmbeddings())
    documents = vector_store.similarity_search(question)
    return  " ".join([page.page_content for page in documents])