from mesa.batchrunner import batch_run
from model import EthnicViolenceModel
import pandas as pd

params = {
    "width": 60,
    "height": 60,
    "majority_pct": [round(v, 2) for v in list(range(50, 100, 5))],  # 0.50 to 0.95
    "density":      [round(v, 2) for v in list(range(40, 90, 10))],  # 0.40 to 0.80
    "alpha":        [round(v, 2) for v in [0.05, 0.10, 0.15, 0.20, 0.25]],
    "beta":         [round(v, 2) for v in [0.01, 0.05, 0.10]],
    "decay":        [round(v, 2) for v in [0.80, 0.90, 1.00]],
    "vision":       range(1, 4),  # 1 to 3
}

if __name__ == '__main__':
    results = batch_run(
        EthnicViolenceModel,
        parameters=params,
        iterations=3,           # You can increase this for statistical stability
        max_steps=50,
        number_processes=None,  # Or set = number of CPU cores
        data_collection_period=1,
        display_progress=True,
    )

    # Convert to DataFrame and save
    df = pd.DataFrame(results)
    df.to_csv("ethnic_violence_batch_results.csv", index=False)
