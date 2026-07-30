from langchain_groq import ChatGroq
from dotenv import load_dotenv
from groq import Groq
import os
import streamlit as st

load_dotenv()


def _get_api_key():
    return os.getenv("GROQ_API_KEY") or st.secrets.get("GROQ_API_KEY", "")


def get_llm():

    return ChatGroq(
        model="llama-3.3-70b-versatile",
        temperature=0,
        api_key=_get_api_key()
    )


def get_groq_client():

    return Groq(
        api_key=_get_api_key()
    )