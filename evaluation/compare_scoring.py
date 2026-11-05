"""
Compares ways of turning RoBERTa-MNLI's output into a pair score.

The method is chosen on the 8 development questions, which are kept apart from
the 20 test questions. Saves development answers to results/dev_results.json.
"""

import json
import sys
from pathlib import Path

import torch

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent))

import judge  # noqa: E402

RESULTS = HERE / "results"
THRESHOLD = 0.5

# Each item: question, and words that mark a right answer.
DEV_QUESTIONS = [
    ("What is the capital of Australia?", ["Canberra"]),
    ("Who wrote the play Romeo and Juliet?", ["Shakespeare"]),
    ("Who won the Nobel Prize in Physics in 1962?", ["Landau"]),
    ("In which year was the Battle of Talikota fought?", ["1565"]),
    ("What is the name of the longest river in Bhutan?", ["Manas", "Drangme"]),
    ("In which year did Albert Einstein win the Nobel Prize in Chemistry?", ["not ", "never"]),
    ("Who was the first Indian astronaut to walk on the Moon?", ["no Indian", "No Indian", "not ", "never", "None"]),
    ("Who wrote the 1987 novel The Glass Tortoise of Nagpur?", ["not ", "no such", "unknown"]),
]


def probabilities(sentences):
    """Entailment and contradiction for every ordered pair."""
    count = len(sentences)
    pairs = [(i, j) for i in range(count) for j in range(count) if i != j]
    inputs = judge.tokenizer([sentences[i] for i, _ in pairs], [sentences[j] for _, j in pairs],
                             return_tensors="pt", padding=True, truncation=True,
                             max_length=128).to(judge.model.device)
    with torch.no_grad():
        output = judge.model(**inputs).logits.float().softmax(dim=-1)
    entail, contradict = {}, {}
    for (i, j), row in zip(pairs, output):
        entail[i, j] = row[judge.ENTAILMENT].item()
        contradict[i, j] = row[judge.CONTRADICTION].item()
    return entail, contradict


METHODS = {
    "Both must entail (min)": lambda e, c, i, j: min(e[i, j], e[j, i]),
    "Average entailment": lambda e, c, i, j: (e[i, j] + e[j, i]) / 2,
    "Stronger entailment (max)": lambda e, c, i, j: max(e[i, j], e[j, i]),
    "No contradiction": lambda e, c, i, j: 1 - max(c[i, j], c[j, i]),
}


def agreement(sentences, method):
    entail, contradict = probabilities(sentences)
    count = len(sentences)
    scores = [METHODS[method](entail, contradict, i, j) for i in range(count) for j in range(i + 1, count)]
    return sum(scores) / len(scores)


def report(name, cases):
    print("\n%s (%d questions)" % (name, len(cases)))
    print("%-27s caught missed alarms clean" % "method")
    for method in METHODS:
        counts = {"caught": 0, "missed": 0, "alarm": 0, "clean": 0}
        for sentences, wrong in cases:
            flagged = agreement(sentences, method) < THRESHOLD
            counts[{(True, True): "caught", (False, True): "missed",
                    (True, False): "alarm", (False, False): "clean"}[flagged, wrong]] += 1
        print("%-27s %6d %6d %6d %5d" % (method, counts["caught"], counts["missed"], counts["alarm"], counts["clean"]))


def main():
    path = RESULTS / "dev_results.json"
    if path.exists():
        rows = json.loads(path.read_text(encoding="utf-8"))
    else:
        import sampler

        torch.manual_seed(52)
        rows = []
        for question, accept in DEV_QUESTIONS:
            answers = sampler.sample_answers(question)
            best = answers[judge.judge(answers)["best"]]
            rows.append({"question": question, "answers": answers, "best": best,
                         "auto_wrong": not any(word in best for word in accept)})
        path.write_text(json.dumps(rows, indent=2), encoding="utf-8")

    for row in rows:
        print("%-5s %s\n      best: %s" % ("WRONG" if row["auto_wrong"] else "right", row["question"],
                                           row["best"].encode("ascii", "replace").decode()[:90]))
    report("Development set", [(row["answers"], row["auto_wrong"]) for row in rows])

    # The same comparison on the 20 test questions, for the record. This is not
    # used to choose the method.
    marked = RESULTS / "marked_results.json"
    if marked.exists():
        test = [r for r in json.loads(marked.read_text(encoding="utf-8")) if r["prompt"] in ("Direct", "BLIP")]
        report("Test set", [
            (["The answer is %s." % a for a in r["answers"]] if r["prompt"] == "BLIP" else r["answers"], r["wrong"])
            for r in test
        ])


if __name__ == "__main__":
    main()
