"""
Tests for user profile schema migrations using Alembic.
Runs migrations programmatically against a throwaway SQLite database.
"""

import os
import tempfile
from alembic.config import Config
from alembic import command
from sqlalchemy import create_engine, inspect


def test_profile_migration_execution():
    """
    Executes Alembic migrations against an isolated temporary database,
    verifying that both meals and user_profiles tables are successfully created.
    """
    # Create temporary SQLite database path
    fd, db_path = tempfile.mkstemp(suffix=".db")
    os.close(fd)
    
    try:
        # Setup Alembic configuration pointing to the test DB with absolute paths
        base_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
        alembic_cfg = Config(os.path.join(base_dir, "alembic.ini"))
        alembic_cfg.set_main_option("script_location", os.path.join(base_dir, "migrations"))
        
        db_url = f"sqlite:///{db_path}"
        alembic_cfg.set_main_option("sqlalchemy.url", db_url)
        
        # Run upgrade programmatically
        command.upgrade(alembic_cfg, "head")
        
        # Check database schema state
        engine = create_engine(db_url)
        inspector = inspect(engine)
        tables = inspector.get_table_names()
        
        assert "meals" in tables, "Table 'meals' was not created by migrations."
        assert "user_profiles" in tables, "Table 'user_profiles' was not created by migrations."
        
        # Check columns of 'user_profiles'
        columns = {c["name"]: c["type"].__class__.__name__ for c in inspector.get_columns("user_profiles")}
        
        assert "user_id" in columns
        assert "dietary_goal" in columns
        assert "allergies" in columns
        assert "created_at" in columns
        
    finally:
        # Cleanup temporary test database
        if os.path.exists(db_path):
            try:
                os.remove(db_path)
            except Exception:
                pass
