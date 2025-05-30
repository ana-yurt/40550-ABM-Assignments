import os
import itertools
import multiprocessing as mp
import pandas as pd
import logging
from model import EthnicViolenceModel

# Configure file logger
logging.basicConfig(
    filename='ethnic_violence_batch_3.log',
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)
logger = logging.getLogger(__name__)

# Configuration
WIDTH = 80
HEIGHT = 80
MAJORITY_PCT = [0.7]
DENSITY = [0.7]
ALPHA = [round(v / 100, 2) for v in range(5, 51, 5)]           # 0.05 to 0.50
RATIOS =  [0.5]+ list(range(1, 26, 3))   # 0.5, 1, 3, 5, ..., 25
DECAY = [round(v / 100, 2) for v in range(50, 100, 10)]
VISION = [1]
AVERSION = [round(v / 100, 2) for v in range(0, 51, 10)]
ITERATIONS = 2
MAX_STEPS = 50
NUM_PROCESSES = 99

# Worker function
def run_model(task):
    params, iteration = task
    pid = os.getpid()
    logger.debug(f"[PID {pid}] Starting iteration {iteration} with params {params}")

    model = EthnicViolenceModel(**params)
    step = 0
    while step < MAX_STEPS and model.running:
        model.step()
        step += 1

    # Extract final metrics
    try:
        df = model.datacollector.get_model_vars_dataframe()
        final_data = df.iloc[-1].to_dict()
    except Exception:
        final_data = {'step_count': step}

    result = {**params, 'iteration': iteration, 'step_count': step, **final_data}
    logger.debug(f"[PID {pid}] Finished iteration {iteration}")
    return result

if __name__ == '__main__':
    # Build task list using alpha/beta ratios
    param_grid = []
    for mpct, den, alp, ratio, dec, vis, avr in itertools.product(
        MAJORITY_PCT, DENSITY, ALPHA, RATIOS, DECAY, VISION, AVERSION
    ):
        beta = round(alp / ratio, 12)
        # skip unrealistic beta values
        if beta <= 0 or beta > 1:
            continue
        param_grid.append({
            'width': WIDTH,
            'height': HEIGHT,
            'majority_pct': mpct,
            'density': den,
            'alpha': alp,
            'beta': beta,
            'decay': dec,
            'vision': vis,
            'aversion': avr
        })

    tasks = [(params, it) for params in param_grid for it in range(ITERATIONS)]
    total_tasks = len(tasks)
    logger.info(f"Total tasks to run (alpha/beta ratios applied): {total_tasks}")

    # Use spawn context to avoid fork issues on HPC
    ctx = mp.get_context('spawn')
    pool = ctx.Pool(processes=NUM_PROCESSES)

    results = []
    completed = 0
    next_pct = 1
    # Track progress as tasks complete and log every 1%
    for res in pool.imap_unordered(run_model, tasks):
        completed += 1
        results.append(res)
        logger.info(
            f"Completed: iteration={res['iteration']}, "
            #f"params={{" + ", ".join(f"{k}={v}" for k, v in res.items() if k not in ['iteration', 'step_count']) + "}}, "
            f"steps={res['step_count']}"
        )
        pct = int(completed * 100 / total_tasks)
        if pct >= next_pct:
            logger.info(f"Progress: {pct}% ({completed}/{total_tasks}) tasks completed")
            next_pct = pct + 1

    pool.close()
    pool.join()

    # Save aggregated results
    df = pd.DataFrame(results)
    timestamp = pd.Timestamp.now().strftime('%Y%m%d_%H%M%S')
    output_file = f"ethnic_violence_batch_results_{total_tasks}_{timestamp}.csv"
    df.to_csv(output_file, index=False)
    logger.info(f"All tasks done. Results saved to {output_file}")
