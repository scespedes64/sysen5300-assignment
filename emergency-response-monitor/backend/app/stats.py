import numpy as np
import pandas as pd

USL_MINUTES = 8.0  # NFPA 1710 ALS Response Target (8.0 min)
D2_CONSTANT = 1.128  # Shewhart constant for n=2 moving range

def analyze_spc_and_capability(df: pd.DataFrame) -> dict:
    times = df["total_response_min"].to_numpy(dtype=float)
    n = len(times)

    # 1. Moving Range (MR)
    mr = np.abs(np.diff(times))
    mr_padded = np.insert(mr, 0, 0.0)

    # 2. Control Chart Parameters (I-MR)
    mean_val = float(np.mean(times))
    mr_bar = float(np.mean(mr)) if len(mr) > 0 else 0.0

    # Within-process sigma estimate
    sigma_hat = mr_bar / D2_CONSTANT if mr_bar > 0 else 1.0

    unpl = mean_val + 2.66 * mr_bar
    lnpl = max(0.0, mean_val - 2.66 * mr_bar)
    ucl_mr = 3.267 * mr_bar

    # 3. Process Capability (Cp, Cpk)
    cp = USL_MINUTES / (6.0 * sigma_hat)
    cpk = (USL_MINUTES - mean_val) / (3.0 * sigma_hat)

    # 4. Percentiles & Failure Probability
    p50 = float(np.percentile(times, 50))
    p90 = float(np.percentile(times, 90))
    p95 = float(np.percentile(times, 95))
    prob_failure_usl = float(np.mean(times > USL_MINUTES) * 100.0)
    prob_severe_15m = float(np.mean(times > 15.0) * 100.0)

    # 5. Evaluate Nelson Rule 1 (above UNPL) & Rule 2 (8+ consecutive above CL)
    records = []
    consec_above = 0
    rule1_count = 0
    rule2_count = 0

    for idx, row in df.iterrows():
        val = float(row["total_response_min"])
        if val > mean_val:
            consec_above += 1
        else:
            consec_above = 0

        r1 = val > unpl
        r2 = consec_above >= 8
        if r1:
            rule1_count += 1
        if r2:
            rule2_count += 1

        # Fault Tree Classification
        intake = float(row["intake_min"])
        turnout = float(row["turnout_min"])
        travel = float(row["travel_min"])
        cross = bool(row["cross_coverage"])

        if r1 or val > USL_MINUTES:
            if cross and travel > 10.0:
                fault = "Cross-Coverage Depletion (Boundary Penalty)"
            elif travel > 6.5:
                fault = "Transit Obstruction / Route Shift"
            elif turnout > 2.0:
                fault = "Station Turnout Bottleneck"
            elif intake > 1.8:
                fault = "911 Queue / Triage Lag"
            else:
                fault = "High Call Volume Variance"
        else:
            fault = "In-Control (Common Cause)"

        records.append({
            **row.to_dict(),
            "mr": round(float(mr_padded[idx]), 2),
            "rule1_violation": bool(r1),
            "rule2_violation": bool(r2),
            "consecutive_above_cl": consec_above,
            "fault_tree_mode": fault
        })

    return {
        "summary": {
            "sample_size": n,
            "mean": round(mean_val, 2),
            "median_p50": round(p50, 2),
            "p90": round(p90, 2),
            "p95": round(p95, 2),
            "mr_bar": round(mr_bar, 2),
            "sigma_within": round(sigma_hat, 2),
            "cl": round(mean_val, 2),
            "unpl": round(unpl, 2),
            "lnpl": round(lnpl, 2),
            "ucl_mr": round(ucl_mr, 2),
            "usl": USL_MINUTES,
            "cp": round(cp, 2),
            "cpk": round(cpk, 2),
            "prob_exceed_usl_pct": round(prob_failure_usl, 1),
            "prob_severe_15m_pct": round(prob_severe_15m, 1),
            "rule1_violations": rule1_count,
            "rule2_violations": rule2_count,
            "capable": bool(cpk >= 1.0 and rule1_count == 0 and rule2_count == 0)
        },
        "series": records
    }