"""
Runs the detector on the 20 test questions and saves every answer.

    python evaluation/run_evaluation.py

Text questions are run once per prompt style, so the styles can be compared.
Image questions use BLIP, which has no prompt style. Results are written to
evaluation/results/raw_results.json, then score.py turns them into tables.
"""

import json
import sys
import time
from pathlib import Path

import torch
from PIL import Image

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent))

import config  # noqa: E402
import detector  # noqa: E402
from questions import IMAGE_QUESTIONS, TEXT_QUESTIONS  # noqa: E402

SEED = 52
IMAGES = HERE / "images"
RESULTS = HERE / "results"


def record(item, result, prompt_name, seconds):
    return {
        "kind": item["kind"],
        "question": item["question"],
        "prompt": prompt_name,
        "answers": result["answers"],
        "best": result["answers"][result["best"]],
        "agreement": round(result["agreement"], 4),
        "confidence": [round(value, 4) for value in result["confidence"]],
        "group_sizes": [len(group) for group in result["groups"]],
        "seconds": round(seconds, 2),
    }


def main():
    RESULTS.mkdir(exist_ok=True)
    rows = []

    for prompt_name in config.PROMPTS:
        torch.manual_seed(SEED)
        for item in TEXT_QUESTIONS:
            start = time.time()
            result = detector.check_text(item["question"], prompt_name)
            rows.append(record(item, result, prompt_name, time.time() - start))
            print("%-9s %.2f  %s" % (prompt_name, rows[-1]["agreement"], item["question"]))

    torch.manual_seed(SEED)
    for item in IMAGE_QUESTIONS:
        image = Image.open(IMAGES / item["file"])
        start = time.time()
        result = detector.check_image(image, item["question"])
        rows.append(record(item, result, "BLIP", time.time() - start))
        print("%-9s %.2f  %s" % ("BLIP", rows[-1]["agreement"], item["question"]))

    (RESULTS / "raw_results.json").write_text(json.dumps(rows, indent=2), encoding="utf-8")
    print("Saved %d rows" % len(rows))


if __name__ == "__main__":
    main()
