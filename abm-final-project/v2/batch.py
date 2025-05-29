from mesa.batchrunner import batch_run
from model import EthnicViolenceModel
import pandas as pd

params = {
    "width": 60,
    "height": 60,
    "majority_pct": [round(v / 100, 2) for v in range(50, 100, 5)],   # 0.50 to 0.95
    "density":      [round(v / 100, 2) for v in range(40, 90, 10)],   # 0.40 to 0.80
    "alpha":        [round(v / 100, 2) for v in range(5, 40)],        # 0.05 to 0.39
    "beta":         [round(v / 100, 2) for v in range(5, 40)],        # 0.05 to 0.39
    "decay":        [round(v / 100, 2) for v in range(70, 100)],      # 0.70 to 0.99
    "vision":       list(range(1, 10)),                               # 1 to 9
    "aversion":     [round(v / 100, 2) for v in range(0, 51, 5)],     # 0.00 to 0.50
}

if __name__ == '__main__':
    print("Starting batch run with parameters:")
    for key, value in params.items():
        print(f"{key}: {value}")
    print("This may take a while depending on the number of parameters and iterations...")
    results = batch_run(
        EthnicViolenceModel,
        parameters=params,
        iterations=1,
        max_steps=50,
        number_processes=4,  # Adjust based on CPU
        data_collection_period=1,
        display_progress=True,
    )

    df = pd.DataFrame(results)
    df.to_csv("ethnic_violence_batch_results.csv", index=False)
