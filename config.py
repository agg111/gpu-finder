"""
Shared configuration and client initialization.
Initialize Metorial and OpenAI clients once and reuse across modules.
"""
import os
from metorial import Metorial, MetorialOpenAI
from openai import AsyncOpenAI
import dotenv

# Load environment variables once
dotenv.load_dotenv()

# Initialize clients once - these will be reused everywhere
metorial = Metorial(api_key=os.getenv("METORIAL_API_KEY"))
openai = AsyncOpenAI(api_key=os.getenv("OPENAI_API_KEY"))
