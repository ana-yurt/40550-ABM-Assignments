#!/usr/bin/env python3
import logging
import os
import sys

# Make sure this matches your batch logging format (optional)
logging.basicConfig(
    filename='single_test.log',
    level=logging.DEBUG,
    format='%(asctime)s - %(processName)s - %(levelname)s - %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)
logger = logging.getLogger()

from model import EthnicViolenceModel

def main():
    # Pick one set of parameters (just like in your batch)
    params = {
        "width":      60,
        "height":     60,
        "majority_pct": 0.5,
        "density":      0.6,
        "alpha":        0.05,
        "beta":         0.05,
        "decay":        0.7,
        "vision":       1,
        "aversion":     0.0,
    }

    logger.debug("Starting single-model test (PID=%d) with params: %s", os.getpid(), params)
    try:
        model = EthnicViolenceModel(**params)
    except Exception:
        logger.exception("Model initialization failed")
        sys.exit(1)

    # Run for up to 50 steps (or until stopped internally)
    max_steps = 50
    for step in range(1, max_steps + 1):
        try:
            model.step()
            logger.debug("Completed step %d/%d", step, max_steps)
        except Exception:
            logger.exception("Error at step %d", step)
            sys.exit(1)

    logger.info("Single-model test finished all %d steps successfully.", max_steps)
    print("Single-model run completed without errors.")

if __name__ == "__main__":
    main()
