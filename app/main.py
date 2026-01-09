from fastapi import FastAPI, HTTPException
from fastapi.responses import FileResponse
from datetime import datetime
from collections import defaultdict
from bson import ObjectId
import matplotlib
matplotlib.use("Agg")

from .schemas import EntryStart, Entry, ProjectCreate, Project, EntryUpdate
from .models import entry_helper, project_helper
from .configurations import db, entries_collection, projects_collection
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from pathlib import Path
app = FastAPI(title="Time Tracker Graph")

#******************************Graphing functions****************************************

@app.get("/graph/proj/{project_id}", status_code=200)
def get_graph_by_project(project_id: str):
    if not ObjectId.is_valid(project_id):
        raise HTTPException(status_code=400, detail="Invalid project id")

    project = projects_collection.find_one({"_id": ObjectId(project_id)})
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")

    totals = defaultdict(int)

    pid = project["_id"]
    entries = entries_collection.find({
        "project_group_id": {"$in": [pid, str(pid)]}
    })

    for e in entries:
        entry = entry_helper(e)
        # If starttime is sometimes a string, handle that:
        st = entry["starttime"]
        if isinstance(st, str):
            st = datetime.fromisoformat(st)

        date_key = st.strftime("%Y-%m-%d")
        totals[date_key] += int(entry.get("duration") or 0)

    if not totals:
        raise HTTPException(status_code=404, detail="No entries found for this project")

    sort_entries = sorted(totals.items())
    dates = [d for d, _ in sort_entries]
    durations = [v for _, v in sort_entries]

    plt.figure(figsize=(10, 4))
    plt.plot(dates, durations)
    plt.grid(True)
    plt.xticks(rotation=45, ha="right")
    plt.tight_layout()
    plt.savefig("graph.png")
    plt.close()

    image_path = Path("graph.png")
    if not image_path.is_file():
        return {"error": "Image not found on the server"}
    return FileResponse(image_path)

@app.get("/graph/user/{user_id}", status_code=200)
def get_graph_by_user(user_id: str):
    # Choose ONE depending on how owner_id is stored in Mongo:

    # If owner_id is stored as STRING:
    projects = projects_collection.find({"owner_id": user_id})

    # If owner_id is stored as ObjectId, use instead:
    # if not ObjectId.is_valid(user_id):
    #     raise HTTPException(status_code=400, detail="Invalid user id")
    # projects = projects_collection.find({"owner_id": ObjectId(user_id)})

    totals = defaultdict(int)

    for project in projects:
        pid = project["_id"]
        entries = entries_collection.find({
            "project_group_id": {"$in": [pid, str(pid)]}
        })

        for e in entries:
            entry = entry_helper(e)
            st = entry["starttime"]
            if isinstance(st, str):
                st = datetime.fromisoformat(st)

            date_key = st.strftime("%Y-%m-%d")
            totals[date_key] += int(entry.get("duration") or 0)

    if not totals:
        raise HTTPException(status_code=404, detail="No entries found for this user")

    sort_entries = sorted(totals.items())
    dates = [d for d, _ in sort_entries]
    durations = [v for _, v in sort_entries]

    plt.figure(figsize=(10, 4))
    plt.plot(dates, durations)
    plt.grid(True)
    plt.xticks(rotation=45, ha="right")
    plt.tight_layout()
    plt.savefig("graph.png")
    plt.close()

    image_path = Path("graph.png")
    if not image_path.is_file():
        return {"error": "Image not found on the server"}
    return FileResponse(image_path)


# python -m uvicorn app.main:app --reload