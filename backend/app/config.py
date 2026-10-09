import os
from dotenv import load_dotenv

load_dotenv()

DATABASE_URL=os.environ["DATABASE_URL"]
JWT_SECRET=os.environ["JWT_SECRET"]
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 240