# Import the necessary module
from dotenv import load_dotenv
import os

# Load environment variables from the .env file (if present)
load_dotenv()

# Access environment variables as if they came from the actual environment
GOOGLE_API_KEY = os.getenv('GOOGLE_API_KEY')
#DATABASE_URL = os.getenv('DATABASE_URL')

# Example usage
print(f'GOOGLE_API_KEY: {GOOGLE_API_KEY}')


if __name__ == '__main__':
    #  test.run()
    print("running")
    
