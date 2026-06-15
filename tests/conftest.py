"""
Pytest shared fixtures for Jaundice Recovery Tracker.
Uses an isolated in-memory SQLite database so the real DB is never touched.
"""
import pytest
from app import create_app
from models.db import db as _db


@pytest.fixture(scope='session')
def app():
    """Create application configured for testing."""
    test_app = create_app()
    test_app.config.update({
        'TESTING': True,
        'SQLALCHEMY_DATABASE_URI': 'sqlite:///:memory:',
        'WTF_CSRF_ENABLED': False,
        'SECRET_KEY': 'test-secret',
    })

    with test_app.app_context():
        _db.create_all()
        yield test_app
        _db.drop_all()


@pytest.fixture(scope='function')
def client(app):
    """Return a test client; each test gets a fresh client."""
    return app.test_client()


@pytest.fixture(scope='function', autouse=True)
def clean_db(app):
    """Wipe all rows before every test so tests are independent."""
    with app.app_context():
        yield
        _db.session.rollback()
        for table in reversed(_db.metadata.sorted_tables):
            _db.session.execute(table.delete())
        _db.session.commit()
