import os
from pathlib import Path

from dotenv import load_dotenv
from starlette.templating import Jinja2Templates

load_dotenv()

USER = os.getenv("MYSQL_USER")
PASSWORD = os.getenv("MYSQL_PASSWORD")
HOST = os.getenv("MYSQL_HOST")
DB = os.getenv("MYSQL_DB")

SECRET_KEY = os.getenv("SECRET_KEY")
ALGORITHM = "HS256"
DATABASE_URL = os.getenv("DATABASE_URL")

SMTP2GO_KEY = os.getenv("SMTP2GO_KEY")
SMTP2GO_URL = "https://api.smtp2go.com/v3/email/send"

TEMPLATES_PATH = Path(__file__).parent.parent / 'templates'
TEMPLATES = Jinja2Templates(directory=str(TEMPLATES_PATH))
