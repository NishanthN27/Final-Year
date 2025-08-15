# src/interview_system/services/llm_clients.py

import os
from langchain_google_genai import ChatGoogleGenerativeAI
from google.generativeai.types import HarmCategory, HarmBlockThreshold

# A dictionary to cache initialized LLM clients.
_llm_clients = {}

def get_llm(model_type: str = "flash"):
    """
    Initializes and returns a cached LLM client.

    Args:
        model_type (str): The type of model to return, either "flash" or "pro".

    Returns:
        An instance of ChatGoogleGenerativeAI configured for the project.
    """
    if model_type in _llm_clients:
        return _llm_clients[model_type]

    api_key = os.getenv("GOOGLE_API_KEY")
    if not api_key:
        raise ValueError("GOOGLE_API_KEY not found in environment variables.")

    model_name = "gemini-1.5-flash-latest" if model_type == "flash" else "gemini-1.5-pro-latest"

    safety_settings = {
        HarmCategory.HARM_CATEGORY_HARASSMENT: HarmBlockThreshold.BLOCK_NONE,
        HarmCategory.HARM_CATEGORY_HATE_SPEECH: HarmBlockThreshold.BLOCK_NONE,
        HarmCategory.HARM_CATEGORY_SEXUALLY_EXPLICIT: HarmBlockThreshold.BLOCK_NONE,
        HarmCategory.HARM_CATEGORY_DANGEROUS_CONTENT: HarmBlockThreshold.BLOCK_NONE,
    }

    # Initialize the Gemini model with all necessary configurations
    llm = ChatGoogleGenerativeAI(
        model=model_name,
        google_api_key=api_key,
        safety_settings=safety_settings,
        response_mime_type="application/json",
        convert_system_message_to_human=True,
        # --- ADD THIS LINE TO DISABLE RETRIES ---
        max_retries=0,
    )

    _llm_clients[model_type] = llm
    return llm