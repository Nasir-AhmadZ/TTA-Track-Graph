import pytest
from fastapi.testclient import TestClient
from app.main import app
from app import configurations

@pytest.fixture
def client():

    # clear the collections before the test
    configurations.entries_collection.delete_many({})
    configurations.projects_collection.delete_many({})
    
    with TestClient(app) as c:
        yield c
        # clear the collections after the test
        configurations.entries_collection.delete_many({})
        configurations.projects_collection.delete_many({})