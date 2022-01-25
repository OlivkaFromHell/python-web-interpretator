import os

from dotenv import load_dotenv

load_dotenv()

TIMEOUT = int(os.getenv("TIMEOUT"))
HOST = str(os.getenv("HOST"))
PORT = str(os.getenv("PORT"))
