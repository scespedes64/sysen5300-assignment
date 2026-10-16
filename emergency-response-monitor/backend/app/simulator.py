import os
import random
from datetime import datetime, timedelta
import pandas as pd

def generate_datasets(output_dir: str = "../data"):
    os.makedirs(output_dir, exist_ok=True)
    random.seed(42)  # Reproducible for judges

    base_time = datetime(2026, 10, 16, 8, 0, 0)

    # 1. Dataset 1: In Statistical Control (Station Alpha)
    rows_1 = []
    for i in range(60):
        t_call = base_time + timedelta(minutes=i * 18)
        intake = round(random.uniform(0.5, 1.1), 2)
        turnout = round(random.uniform(0.8, 1.4), 2)
        travel = round(max(2.0, random.gauss(3.5, 0.5)), 2)
        total = round(intake + turnout + travel, 2)
        rows_1.append({
            "incident_id": f"CAD-10{i:02d}",
            "timestamp": t_call.strftime("%Y-%m-%dT%H:%M:%SZ"),
            "zone_id": "Station_Alpha_Suburb",
            "priority": "Delta",
            "intake_min": intake,
            "turnout_min": turnout,
            "travel_min": travel,
            "total_response_min": total,
            "cross_coverage": False,
            "apot_hospital_delay_min": round(random.uniform(4.0, 9.0), 1),
            "unit_id": f"MEDIC-0{(i % 3) + 1}"
        })
    pd.DataFrame(rows_1).to_csv(os.path.join(output_dir, "dataset_1_in_control.csv"), index=False)

    # 2. Dataset 2: Out of Control / Fat-Tail Outliers (Downtown Core)
    rows_2 = []
    outlier_indices = {6, 14, 23, 31, 39, 47, 54}
    for i in range(60):
        t_call = base_time + timedelta(minutes=i * 15)
        is_outlier = i in outlier_indices
        if is_outlier:
            intake = round(random.uniform(1.2, 2.5), 2)
            turnout = round(random.uniform(1.3, 2.2), 2)
            travel = round(random.uniform(19.0, 27.5), 2)
            cross = True
            apot = round(random.uniform(38.0, 62.0), 1)
        else:
            intake = round(random.uniform(0.6, 1.2), 2)
            turnout = round(random.uniform(0.9, 1.5), 2)
            travel = round(max(2.2, random.gauss(4.2, 0.7)), 2)
            cross = False
            apot = round(random.uniform(8.0, 15.0), 1)

        total = round(intake + turnout + travel, 2)
        rows_2.append({
            "incident_id": f"CAD-20{i:02d}",
            "timestamp": t_call.strftime("%Y-%m-%dT%H:%M:%SZ"),
            "zone_id": "Downtown_Core",
            "priority": "Echo" if is_outlier else "Delta",
            "intake_min": intake,
            "turnout_min": turnout,
            "travel_min": travel,
            "total_response_min": total,
            "cross_coverage": cross,
            "apot_hospital_delay_min": apot,
            "unit_id": "MEDIC-09 (Cross-Zone)" if cross else f"MEDIC-0{(i % 4) + 1}"
        })
    pd.DataFrame(rows_2).to_csv(os.path.join(output_dir, "dataset_2_out_of_control.csv"), index=False)

    # 3. Dataset 3: Systemic Process Shift / Bridge Closure (Sector 4)
    rows_3 = []
    for i in range(60):
        t_call = base_time + timedelta(minutes=i * 16)
        shifted = i >= 28  # Bridge closes at call #28
        intake = round(random.uniform(0.7, 1.3), 2)
        turnout = round(random.uniform(0.9, 1.5), 2)
        if shifted:
            travel = round(max(6.5, random.gauss(9.8, 0.9)), 2)
        else:
            travel = round(max(2.0, random.gauss(3.8, 0.5)), 2)

        total = round(intake + turnout + travel, 2)
        rows_3.append({
            "incident_id": f"CAD-30{i:02d}",
            "timestamp": t_call.strftime("%Y-%m-%dT%H:%M:%SZ"),
            "zone_id": "Sector_4_Industrial",
            "priority": "Delta",
            "intake_min": intake,
            "turnout_min": turnout,
            "travel_min": travel,
            "total_response_min": total,
            "cross_coverage": False,
            "apot_hospital_delay_min": round(random.uniform(10.0, 18.0), 1),
            "unit_id": f"MEDIC-0{(i % 3) + 5}"
        })
    pd.DataFrame(rows_3).to_csv(os.path.join(output_dir, "dataset_3_systemic_shift.csv"), index=False)
    print("✅ Generated all 3 CSV test datasets in /data!")

if __name__ == "__main__":
    generate_datasets()