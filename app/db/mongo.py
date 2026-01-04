"""
MongoDB database connection and utilities.
"""
from motor.motor_asyncio import AsyncIOMotorClient
from typing import Optional
from app.core.config import settings

# Global database client
client: Optional[AsyncIOMotorClient] = None
database = None


async def connect_to_mongo():
    """Create database connection."""
    global client, database
    client = AsyncIOMotorClient(settings.MONGODB_URL)
    database = client[settings.MONGODB_DB_NAME]
    # Test connection
    await client.admin.command('ping')


async def close_mongo_connection():
    """Close database connection."""
    global client
    if client:
        client.close()


def get_database():
    """Get database instance."""
    return database


async def get_user_by_username(username: str) -> Optional[dict]:
    """Get user by username from database."""
    db = get_database()
    if db is None:
        return None
    user = await db.users.find_one({"username": username})
    return user


async def create_default_user():
    """Create a default user for testing if it doesn't exist."""
    db = get_database()
    if db is None:
        return
    
    from app.core.security import get_password_hash
    
    default_user = {
        "username": "admin",
        "email": "admin@docflow.com",
        "hashed_password": get_password_hash("admin123"),
        "is_active": True
    }
    
    existing = await db.users.find_one({"username": "admin"})
    if not existing:
        await db.users.insert_one(default_user)

