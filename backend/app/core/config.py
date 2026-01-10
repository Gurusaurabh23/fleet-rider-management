import os
from dotenv import load_dotenv

load_dotenv()  # loads .env file if exists

DATABASE_URL = os.getenv(
    "DATABASE_URL", 
    "postgresql://postgres:Advanced%40123@localhost:5432/fleet_db"
)

