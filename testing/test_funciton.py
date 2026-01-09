from bson import ObjectId
from app import configurations
from app.models import entry_helper, project_helper
from datetime import datetime

def test_entry_helper():
    #Test entry_helper function with complete entry
    entry_doc = {
        "_id": ObjectId(),
        "project_group_id": ObjectId(),
        "name": "Test Entry",
        "starttime": datetime(2024, 1, 1, 10, 0),
        "endtime": datetime(2024, 1, 1, 11, 0),
        "duration": 3600
    }
    result = entry_helper(entry_doc)
    assert result["id"] == str(entry_doc["_id"])
    assert result["project_group_id"] == str(entry_doc["project_group_id"])
    assert result["name"] == "Test Entry"
    assert result["duration"] == 3600

def test_entry_helper_no_endtime():
    #Test entry_helper function with entry missing endtime and duration
    entry_doc = {
        "_id": ObjectId(),
        "project_group_id": ObjectId(),
        "name": "Test Entry",
        "starttime": datetime(2024, 1, 1, 10, 0)
    }
    result = entry_helper(entry_doc)
    assert result["id"] == str(entry_doc["_id"])
    assert result["endtime"] is None
    assert result["duration"] is None

def test_project_helper():
    #Test project_helper function
    project_doc = {
        "_id": ObjectId(),
        "owner_id": ObjectId(),
        "name": "Test Project",
        "description": "Test Description"
    }
    result = project_helper(project_doc)
    assert result["id"] == str(project_doc["_id"])
    assert result["owner_id"] == str(project_doc["owner_id"])
    assert result["name"] == "Test Project"
    assert result["description"] == "Test Description"

def test_proj_graph_success(client):
    #Test successful project graph generation
    project_id = ObjectId()
    configurations.projects_collection.insert_one({
        "_id": project_id,
        "owner_id": ObjectId(),
        "name": "Test Project",
        "description": "Test Description"
    })
    
    configurations.entries_collection.insert_one({
        "_id": ObjectId(),
        "project_group_id": project_id,
        "name": "Test Entry",
        "starttime": datetime(2024, 1, 1, 10, 0),
        "endtime": datetime(2024, 1, 1, 11, 0),
        "duration": 3600
    })
    
    r = client.get(f"/graph/proj/{str(project_id)}")
    assert r.status_code == 200

def test_proj_graph_invalid_id(client):
    r = client.get("/graph/proj/invalid_id")
    assert r.status_code == 400
    assert "Invalid project id" in r.json()["detail"]

def test_proj_graph_not_found(client):
    valid_id = str(ObjectId())
    r = client.get(f"/graph/proj/{valid_id}")
    assert r.status_code == 404
    assert "Project not found" in r.json()["detail"]

def test_user_graph_success(client):
    #Test successful user graph generation
    user_id = str(ObjectId())
    project_id = ObjectId()
    
    configurations.projects_collection.insert_one({
        "_id": project_id,
        "owner_id": user_id,
        "name": "User Project",
        "description": "Test Description"
    })
    
    configurations.entries_collection.insert_one({
        "_id": ObjectId(),
        "project_group_id": project_id,
        "name": "User Entry",
        "starttime": datetime(2024, 1, 1, 10, 0),
        "endtime": datetime(2024, 1, 1, 11, 0),
        "duration": 3600
    })
    
    r = client.get(f"/graph/user/{user_id}")
    assert r.status_code == 200

def test_user_graph_no_projects(client):
    user_id = str(ObjectId())
    r = client.get(f"/graph/user/{user_id}")
    assert r.status_code == 404
    assert "No entries found for this user" in r.json()["detail"]