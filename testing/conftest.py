import pytest
from fastapi.testclient import TestClient
import mongomock
from app import configurations

# Create a single shared mock database for all tests
mock_client = mongomock.MongoClient()
mock_db = mock_client.user_db

# Set it globally before any test runs  
configurations.db = mock_db
configurations.entries_collection = mock_db["entries"]
configurations.projects_collection = mock_db["projects"]

@pytest.fixture
def client():
    # Clear collections before each test
    configurations.entries_collection.delete_many({})
    configurations.projects_collection.delete_many({})
    
    from app.main import app
    with TestClient(app) as c:
        yield c