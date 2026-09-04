"""
Shared pytest configuration and fixtures for backend tests.
Initializes the database schema before running any tests.
"""

import pytest
from src.db.database import Base, engine


@pytest.fixture(scope="session", autouse=True)
def setup_test_database():
    """
    Creates all tables in the test SQLite database before any tests run.
    """
    # Import all models to ensure they are registered with Base.metadata
    from src.models.meal import Meal  # noqa: F401

    Base.metadata.create_all(bind=engine)
    yield


@pytest.fixture(autouse=True)
def reset_singletons():
    """
    Clears cached client and provider singletons between tests to prevent leakage.
    """
    import src.providers.vision.factory as factory
    factory._client = None
    factory._provider = None
    yield
