from app import create_app
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

app = create_app()

if __name__ == '__main__':
    # Force debug mode for development
    app.run(debug=True, host='127.0.0.1')