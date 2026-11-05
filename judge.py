"""
Decides how much the sampled answers agree, using RoBERTa-MNLI (U3).

RoBERTa-MNLI reads two sentences and gives three probabilities: the first
sentence entails the second, contradicts it, or neither. Every pair of answers is
checked in both directions and the stronger direction is kept as the pair score.

Why the stronger one: a longer answer entails a shorter one but not the other way
round. "He did not win, as the prize came later" implies "He did not win", so the
two support the same claim even though only one direction holds. Requiring both
directions treated such pairs as disagreement and caused false alarms. See
evaluation/compare_scoring.py for the measurement.
"""

import torch
from transformers import AutoModelForSequenceClassification, AutoTokenizer

import config

tokenizer = AutoTokenizer.from_pretrained(config.NLI_MODEL)
model = AutoModelForSequenceClassification.from_pretrained(
    config.NLI_MODEL,
    dtype=torch.float16,
    attn_implementation="eager",   # needed so the attention weights can be read
).to("cuda").eval()

# A float32 copy for when the GPU is refused. CPUs are slow at float16.
cpu_model = None
if config.CPU_FALLBACK:
    cpu_model = AutoModelForSequenceClassification.from_pretrained(
        config.NLI_MODEL, attn_implementation="eager"
    ).eval()

ENTAILMENT = model.config.label2id.get("ENTAILMENT", 2)
CONTRADICTION = model.config.label2id.get("CONTRADICTION", 0)


def pick(device):
    return cpu_model if device == "cpu" else model


def entailment_matrix(sentences, device="cuda"):
    """Return an n x n list where cell [i][j] is P(sentence i entails sentence j)."""
    judge_model = pick(device)
    count = len(sentences)
    pairs = [(i, j) for i in range(count) for j in range(count) if i != j]
    inputs = tokenizer(
        [sentences[i] for i, _ in pairs],
        [sentences[j] for _, j in pairs],
        return_tensors="pt", padding=True, truncation=True, max_length=128,
    ).to(judge_model.device)

    with torch.no_grad():
        probabilities = judge_model(**inputs).logits.float().softmax(dim=-1)

    matrix = [[1.0] * count for _ in range(count)]
    for (i, j), row in zip(pairs, probabilities):
        matrix[i][j] = row[ENTAILMENT].item()
    return matrix


def pair_scores(matrix):
    """Keep the stronger direction of each pair."""
    count = len(matrix)
    return [[max(matrix[i][j], matrix[j][i]) for j in range(count)] for i in range(count)]


def group_answers(scores):
    """Put answers that make the same claim into groups. Largest group first."""
    count = len(scores)
    group_of = list(range(count))
    for i in range(count):
        for j in range(i + 1, count):
            if scores[i][j] >= config.SAME_CLAIM_SCORE:
                old, new = group_of[j], group_of[i]
                group_of = [new if group == old else group for group in group_of]

    groups = {}
    for index, group in enumerate(group_of):
        groups.setdefault(group, []).append(index)
    return sorted(groups.values(), key=len, reverse=True)


def judge(sentences, device="cuda"):
    """
    Score a set of answers.

    Returns:
        matrix       entailment probability for every ordered pair
        confidence   per answer: mean pair score against the other answers
        agreement    mean of the per-answer confidence, from 0 to 1
        groups       answer indexes grouped by the claim they make
        best         index of the answer the others support most
    """
    matrix = entailment_matrix(sentences, device)
    scores = pair_scores(matrix)
    others = len(sentences) - 1
    confidence = [
        sum(scores[i][j] for j in range(len(sentences)) if j != i) / others
        for i in range(len(sentences))
    ]
    groups = group_answers(scores)
    best = max(groups[0], key=lambda index: confidence[index])
    return {
        "matrix": matrix,
        "confidence": confidence,
        "agreement": sum(confidence) / len(confidence),
        "groups": groups,
        "best": best,
    }


def attention_map(first, second, device="cuda"):
    """
    Show which words the judge looked at when comparing two sentences.

    Takes the last layer, averages its heads, and reads the row of the <s>
    token, because that is the position the classifier makes its decision from.
    Returns the words and one weight for each.
    """
    judge_model = pick(device)
    inputs = tokenizer(first, second, return_tensors="pt", truncation=True, max_length=64).to(judge_model.device)
    with torch.no_grad():
        attention = judge_model(**inputs, output_attentions=True).attentions[-1]
    row = attention[0].mean(dim=0)[0].float().cpu().tolist()
    ids = inputs["input_ids"][0].tolist()

    tokens, weights = [], []
    for token_id, weight in zip(ids, row):
        if token_id in tokenizer.all_special_ids:
            continue
        tokens.append(tokenizer.decode([token_id]).strip())
        weights.append(weight)
    return tokens, weights


def weakest_pair_attention(sentences, matrix, device="cuda"):
    """Attention for the pair of answers that agree least."""
    scores = pair_scores(matrix)
    count = len(sentences)
    first, second = min(
        ((i, j) for i in range(count) for j in range(i + 1, count)),
        key=lambda pair: scores[pair[0]][pair[1]],
    )
    tokens, weights = attention_map(sentences[first], sentences[second], device)
    return {"pair": (first, second), "tokens": tokens, "weights": weights}
