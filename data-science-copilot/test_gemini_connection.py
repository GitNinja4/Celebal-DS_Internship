"""
Step 1 sanity check.
Run this file first to confirm your Gemini API key and LangChain
setup actually work before we build anything on top of it.

Usage:
    1. pip install -r requirements.txt
    2. Create a .env file in this folder with one line:
           GOOGLE_API_KEY=your_actual_key_here
    3. python test_gemini_connection.py
"""

import os
from dotenv import load_dotenv
from langchain_google_genai import ChatGoogleGenerativeAI

load_dotenv()

api_key = os.getenv("GOOGLE_API_KEY")

if not api_key:
    raise ValueError(
        "GOOGLE_API_KEY not found. Create a .env file in this folder "
        "with: GOOGLE_API_KEY=your_actual_key_here"
    )

llm = ChatGoogleGenerativeAI(
    model="gemini-flash-latest",
    google_api_key=api_key,
)

response = llm.invoke("Reply with exactly one sentence: are you working?")

print("\n--- Gemini responded ---")
print(response.content)
print("------------------------\n")
print("If you see a sentence above, your setup is working correctly.")