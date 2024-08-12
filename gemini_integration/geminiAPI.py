from gemini_integration.env_loader import env
import google.generativeai as genai

API_KEY = env('API_KEY')

if not API_KEY:
    raise ValueError("API key not found. Please set the API_KEY environment variable.")

genai.configure(api_key=API_KEY)
