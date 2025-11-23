import os
from pydantic_settings import BaseSettings
from dotenv import load_dotenv, find_dotenv

# Debug .env loading
env_file = find_dotenv()
print(f"Loading .env from: {env_file}")
load_dotenv(env_file)

class Settings(BaseSettings):
    PROJECT_NAME: str = "LangGraph Agentic App"
    API_V1_STR: str = "/api/v1"
    OPENAI_API_KEY: str = os.getenv("OPENAI_API_KEY", "")
    print("OPENAI_API_KEY: ", OPENAI_API_KEY)
    UPLOAD_DIR: str = os.path.join(os.getcwd(), "uploads")

    class Config:
        case_sensitive = True

settings = Settings()

if not settings.OPENAI_API_KEY:
    print("WARNING: OPENAI_API_KEY is not set. The agent will fail to run.")

if not os.path.exists(settings.UPLOAD_DIR):
    os.makedirs(settings.UPLOAD_DIR)
