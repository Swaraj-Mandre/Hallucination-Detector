"""
Turns raw_results.json into the tables used in the report.

    python evaluation/score.py

"Flagged" means the agreement score fell below the warning line. "Wrong" means
the app's best supported answer is actually incorrect. A good detector flags the
wrong answers and leaves the right ones alone.
"""

import csv
import json
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent))

import config  # noqa: E402
from manual_marks import MANUAL_MARKS  # noqa: E402
from questions import IMAGE_QUESTIONS, TEXT_QUESTIONS  # noqa: E402

RESULTS = HERE / "results"
ACCEPT = {item["question"]: item["accept"] for item in TEXT_QUESTIONS + IMAGE_QUESTIONS}


def is_wrong(row):
    """Mark by the accepted words first, then apply any hand review."""
    manual = MANUAL_MARKS.get((row["prompt"], row["question"]))
    if manual is not None:
        return manual == "wrong"
    answer = row["best"].lower()
    return not any(word.lower() in answer for word in ACCEPT[row["question"]])


def summarise(rows, threshold):
    caught = sum(1 for r in rows if r["wrong"] and r["agreement"] < threshold)
    missed = sum(1 for r in rows if r["wrong"] and r["agreement"] >= threshold)
    alarms = sum(1 for r in rows if not r["wrong"] and r["agreement"] < threshold)
    clean = sum(1 for r in rows if not r["wrong"] and r["agreement"] >= threshold)
    total = len(rows)
    return {
        "caught": caught, "missed": missed, "false_alarms": alarms, "clean": clean,
        "precision": caught / (caught + alarms) if caught + alarms else 0.0,
        "recall": caught / (caught + missed) if caught + missed else 0.0,
        "accuracy": (caught + clean) / total,
        "wrong": caught + missed,
        "total": total,
    }


def main():
    rows = json.loads((RESULTS / "raw_results.json").read_text(encoding="utf-8"))
    for row in rows:
        row["wrong"] = is_wrong(row)

    threshold = config.AGREEMENT_THRESHOLD
    main_rows = [r for r in rows if r["prompt"] in (config.DEFAULT_PROMPT, "BLIP")]

    with open(RESULTS / "flagged_vs_wrong.csv", "w", newline="", encoding="utf-8") as handle:
        writer = csv.writer(handle)
        writer.writerow(["No", "Type", "Question", "Best answer", "Agreement", "Flagged", "Actually wrong", "Outcome"])
        for number, row in enumerate(main_rows, 1):
            flagged = row["agreement"] < threshold
            outcome = {(True, True): "Caught", (True, False): "False alarm",
                       (False, True): "Missed", (False, False): "Correct pass"}[(flagged, row["wrong"])]
            writer.writerow([number, row["kind"], row["question"], row["best"], "%.2f" % row["agreement"],
                             "Yes" if flagged else "No", "Yes" if row["wrong"] else "No", outcome])

    summary = {"main": summarise(main_rows, threshold), "threshold": threshold}

    summary["threshold_check"] = {
        "%.1f" % value: summarise(main_rows, value) for value in (0.3, 0.4, 0.5, 0.6, 0.7, 0.8)
    }
    summary["prompts"] = {}
    for name in config.PROMPTS:
        subset = [r for r in rows if r["prompt"] == name]
        result = summarise(subset, threshold)
        result["answered_right"] = sum(1 for r in subset if not r["wrong"])
        result["mean_agreement"] = sum(r["agreement"] for r in subset) / len(subset)
        summary["prompts"][name] = result
    summary["seconds_per_check"] = sum(r["seconds"] for r in main_rows) / len(main_rows)

    # How the three labels the user actually sees lined up with the truth.
    bands = {"Likely hallucination": [0, 0], "Unsure": [0, 0], "Consistent": [0, 0]}
    for row in main_rows:
        if row["agreement"] < threshold:
            band = "Likely hallucination"
        elif row["agreement"] < config.STRONG_AGREEMENT:
            band = "Unsure"
        else:
            band = "Consistent"
        bands[band][1 if row["wrong"] else 0] += 1
    summary["bands"] = {name: {"right": value[0], "wrong": value[1]} for name, value in bands.items()}
    print("bands (right, wrong):", bands)
    print("threshold check:")
    for value, result in summary["threshold_check"].items():
        print("  %s caught %d missed %d alarms %d clean %d" % (
            value, result["caught"], result["missed"], result["false_alarms"], result["clean"]))

    (RESULTS / "summary.json").write_text(json.dumps(summary, indent=2), encoding="utf-8")
    (RESULTS / "marked_results.json").write_text(json.dumps(rows, indent=2), encoding="utf-8")
    print(json.dumps(summary["main"], indent=2))
    for name, result in summary["prompts"].items():
        print("%-9s right %d/%d  mean agreement %.2f  recall %.2f  precision %.2f" % (
            name, result["answered_right"], result["total"], result["mean_agreement"],
            result["recall"], result["precision"]))


if __name__ == "__main__":
    main()
