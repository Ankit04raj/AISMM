"""Database initialization and migration utilities."""

import asyncio
import sys
from pathlib import Path

from backend.app.db.session import init_db, create_tables, drop_tables, close_db, check_db_connection
from backend.app.config import get_settings


async def init_database(drop_existing: bool = False) -> None:
    """Initialize database with tables."""
    settings = get_settings()

    print(f"Initializing database: {settings.DATABASE_URL}")

    if drop_existing:
        print("Dropping existing tables...")
        await drop_tables()
        print("Tables dropped.")

    print("Creating tables...")
    await create_tables()
    print("Tables created successfully.")


async def verify_connection() -> bool:
    """Verify database connection."""
    connected = await check_db_connection()
    if connected:
        print("✓ Database connection successful")
    else:
        print("✗ Database connection failed")
    return connected


async def main():
    """Main entry point for database initialization."""
    import argparse

    parser = argparse.ArgumentParser(description="Database initialization")
    parser.add_argument("--drop", action="store_true", help="Drop existing tables first")
    parser.add_argument("--verify", action="store_true", help="Verify connection only")
    args = parser.parse_args()

    init_db()

    if args.verify:
        success = await verify_connection()
        sys.exit(0 if success else 1)

    await init_database(drop_existing=args.drop)
    await close_db()


if __name__ == "__main__":
    asyncio.run(main())