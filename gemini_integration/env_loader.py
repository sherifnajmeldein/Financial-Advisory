import os
from dotenv import load_dotenv

class Env:
    def __init__(self):
        load_dotenv()
        
    def __call__(self, key):
        return os.getenv(key)

# Load the environment variables
env = Env()
