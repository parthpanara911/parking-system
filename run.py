from app import create_app
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

app = create_app()