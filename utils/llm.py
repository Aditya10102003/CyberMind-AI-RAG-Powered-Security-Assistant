from langchain_groq import ChatGroq
from dotenv import load_dotenv
from groq import Groq
import os


load_dotenv()

def get_llm():

    return ChatGroq(
        model="llama-3.3-70b-versatile",
        temperature=0,
        api_key=os.getenv("GROQ_API_KEY")
    )

    

def get_groq_client():

    return Groq(
        api_key=os.getenv("GROQ_API_KEY")
    )