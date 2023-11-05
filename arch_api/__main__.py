import logging
import os

import uvicorn
from dotenv import load_dotenv

if __name__ == "__main__":
    load_dotenv()
    logging.basicConfig(level=os.environ.get("LOG_LEVEL", logging.DEBUG))
    uvicorn.run("app:app", host=os.environ["UVICORN_HOST"], port=8000, reload=True)
