from motor.motor_asyncio import AsyncIOMotorClient
from pymongo import MongoClient
from dotenv import load_dotenv
import os

load_dotenv()

# Async database connection for FastAPI
async def get_async_database():
    client = AsyncIOMotorClient(os.getenv("MONGODB_URI"))
    return client[os.getenv("DATABASE_NAME")]

# Sync database connection for potential utility functions
def get_sync_database():
    client = MongoClient(os.getenv("MONGODB_URI"))
    return client[os.getenv("DATABASE_NAME")]
