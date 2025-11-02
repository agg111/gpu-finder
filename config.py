"""
Shared configuration and client initialization.
Initialize Metorial and OpenAI clients once and reuse across modules.
"""
import os
import ssl
from metorial import Metorial, MetorialOpenAI
from openai import AsyncOpenAI
import dotenv

# Load environment variables once
dotenv.load_dotenv()

# Configure SSL certificates for Nivara (and other HTTP libraries)
# This ensures SSL verification uses the certifi bundle from the virtual environment
try:
    import certifi
    cert_path = certifi.where()
    # Set environment variables that urllib/requests will use
    os.environ.setdefault('SSL_CERT_FILE', cert_path)
    os.environ.setdefault('REQUESTS_CA_BUNDLE', cert_path)
    os.environ.setdefault('CURL_CA_BUNDLE', cert_path)
    
    # Also configure default SSL context to use certifi certificates
    # This helps if libraries create SSL contexts directly
    try:
        default_context = ssl.create_default_context(cafile=cert_path)
        ssl._create_default_https_context = lambda: default_context
    except Exception:
        # If modifying default context fails, environment variables above should suffice
        pass
except ImportError:
    # certifi not installed, use default SSL
    pass

# Initialize clients once - these will be reused everywhere
metorial = Metorial(api_key=os.getenv("METORIAL_API_KEY"))
openai = AsyncOpenAI(api_key=os.getenv("OPENAI_API_KEY"))
