import os
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
import pandas as pd
from app.simulator import generate_datasets
from app.stats import analyze_spc_and_capability

app = FastAPI(
    title="SENTINEL SPC - Emergency Response Quality & Reliability API",
    version="1.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

DATA_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../data"))

# Ensure datasets exist on startup
if not os.path.exists(os.path.join(DATA_DIR, "dataset_1_in_control.csv")):
    generate_datasets(DATA_DIR)

DATASETS = {
    "dataset_1_in_control.csv": "Station Alpha (In-Control Baseline)",
    "dataset_2_out_of_control.csv": "Downtown Core (Fat-Tail Special Causes)",
    "dataset_3_systemic_shift.csv": "Sector 4 (Bridge Closure Shift)"
}

@app.get("/api/datasets")
def list_datasets():
    return [{"filename": k, "label": v} for k, v in DATASETS.items()]

@app.get("/api/analyze/{filename}")
def analyze_dataset(filename: str):
    if filename not in DATASETS:
        raise HTTPException(status_code=404, detail="Dataset not found")
    filepath = os.path.join(DATA_DIR, filename)
    df = pd.read_csv(filepath)
    return analyze_spc_and_capability(df)