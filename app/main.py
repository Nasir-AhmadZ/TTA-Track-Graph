from fastapi import FastAPI, HTTPException
from fastapi.responses import FileResponse
from datetime import datetime
from collections import defaultdict
from bson import ObjectId

from .schemas import EntryStart, Entry, ProjectCreate, Project, EntryUpdate
from .models import entry_helper, project_helper
from .configurations import db, entries_collection, projects_collection
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from pathlib import Path
app = FastAPI(title="Time Tracker Graph")

#******************************Graphing functions****************************************

@app.get("/graph/proj/{project_id}",status_code=200)
def get_graph_by_project(project_id: str):
    #validate ObjectId format
    if not ObjectId.is_valid(project_id):
        raise HTTPException(status_code=400, detail="Invalid project id")

    #check if the project exists
    project = projects_collection.find_one({"_id": ObjectId(project_id)})
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")

    totals = defaultdict(int) 
    date = [] 
    duration = []

    entries = entries_collection.find({"project_group_id": project["_id"]})
    for e in entries:
        entry = entry_helper(e)
        date_time = entry["starttime"].strftime("%Y-%m-%d")
        totals[date_time] += int(entry["duration"] or 0)

    sort_entries = sorted(totals.items())
    date = [d for d, _ in sort_entries]
    duration = [v for _, v in sort_entries]   
    plt.plot(date, duration)
    plt.grid(True)
    plt.savefig("graph.png")
    image_path = Path("graph.png")
    if not image_path.is_file():
        return {"error": "Image not found on the server"}
    return FileResponse(image_path)

@app.get("/graph/user/{user_id}",status_code=200)
def get_graph_by_user(user_id: str):
    projects = projects_collection.find({"owner_id": ObjectId(user_id)})
    totals = defaultdict(int) 

    date = [] 
    duration = []

    for project in projects:
        entries = entries_collection.find({"project_group_id": project["_id"]})
        for e in entries:
            entry = entry_helper(e)
            date_time = entry["starttime"].strftime("%Y-%m-%d")
            totals[date_time] += int(entry["duration"] or 0)

    sort_entries = sorted(totals.items())
    date = [d for d, _ in sort_entries]
    duration = [v for _, v in sort_entries]    

    plt.plot(date, duration)
    plt.grid(True)
    plt.savefig("graph.png")
    image_path = Path("graph.png")
    if not image_path.is_file():
        return {"error": "Image not found on the server"}
    return FileResponse(image_path)

# python -m uvicorn app.main:app --reload