from dotenv import load_dotenv
import os
# Load .env file
load_dotenv()

SECRET_KEY = os.getenv("SECRET_KEY", "mydefaultsecret")
ALGORITHM = os.getenv("ALGORITHM", "HS256")

SMTP_SERVER = os.getenv("SMTP_SERVER")
SMTP_PORT = int(os.getenv("SMTP_PORT"))
SMTP_EMAIL = os.getenv("SMTP_EMAIL")
SMTP_PASSWORD = os.getenv("SMTP_PASSWORD")