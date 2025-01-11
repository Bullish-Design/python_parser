import os

from dotenv import load_dotenv

load_dotenv()


MD_MODEL_DIR = os.getenv("MD_MODEL_DIR")
TEST_DIR = os.getenv("TEST_DIR")
logdir = "python_parser/logs/Log"
