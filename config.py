import os
from dotenv import load_dotenv
load_dotenv(".env.keys")

CORE_API_KEY = os.getenv("CORE_API_KEY")
S2_API_KEY = os.getenv("S2_API_KEY")
NCBI_API_KEY = os.getenv("NCBI_API_KEY")
USER_EMAIL = os.getenv("USER_EMAIL")