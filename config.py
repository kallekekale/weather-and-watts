import os
from dotenv import load_dotenv

load_dotenv()

DB_DSN = os.environ["DATABASE_URL"]
FINGRID_API_KEY = os.environ["FINGRID_API_KEY"]
ENTSO_E_API_KEY = os.environ["ENTSO_E_API_KEY"]
