"""
Decides how much the sampled answers agree, using RoBERTa-MNLI (U3).

RoBERTa-MNLI reads two sentences and gives three probabilities: the first
sentence entails the second, contradicts it, or neither. Two answers mean the
same thing only if each one entails the other, so every pair is checked in both
directions and the weaker direction is kept as the pair score.
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

ENTAILMENT = model.config.label2id.get("ENTAILMENT", 2)
CONTRADICTION = model.config.label2id.get("CONTRADICTION", 0)


def entailment_matrix(sentences):
    """Return an n x n list where cell [i][j] is P(sentence i entails sentence j)."""
    count = len(sentences)
    pairs = [(i, j) for i in range(count) for j in range(count) if i != j]
    inputs = tokenizer(
        [sentences[i] for i, _ in pairs],
        [sentences[j] for _, j in pairs],
        return_tensors="pt", padding=True, truncation=True, max_length=128,
    ).to(model.device)

    with torch.no_grad():
        probabilities = model(**inputs).logits.softmax(dim=-1)

    matrix = [[1.0] * count for _ in range(count)]
    for (i, j), row in zip(pairs, probabilities):
        matrix[i][j] = row[ENTAILMENT].item()
    return matrix


def pair_scores(matrix):
    """Keep the weaker direction of each pair, so one-way entailment scores low."""
    count = len(matrix)
    return [[min(matrix[i][j], matrix[j][i]) for j in range(count)] for i in range(count)]


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


def judge(sentences):
    """
    Score a set of answers.

    Returns:
        matrix       entailment probability for every ordered pair
        confidence   per answer: mean pair score against the other answers
        agreement    mean of the per-answer confidence, from 0 to 1
        groups       answer indexes grouped by the claim they make
        best         index of the answer the others support most
    """
    matrix = entailment_matrix(sentences)
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


def attention_map(first, second):
    """
    Show which words the judge looked at when comparing two sentences.

    Takes the last layer, averages its heads, and reads the row of the <s>
    token, because that is the position the classifier makes its decision from.
    Returns the words and one weight for each.
    """
    inputs = tokenizer(first, second, return_tensors="pt", truncation=True, max_length=64).to(model.device)
    with torch.no_grad():
        attention = model(**inputs, output_attentions=True).attentions[-1]
    row = attention[0].mean(dim=0)[0].float().cpu().tolist()
    ids = inputs["input_ids"][0].tolist()

    tokens, weights = [], []
    for token_id, weight in zip(ids, row):
        if token_id in tokenizer.all_special_ids:
            continue
        tokens.append(tokenizer.decode([token_id]).strip())
        weights.append(weight)
    return tokens, weights


def weakest_pair_attention(sentences, matrix):
    """Attention for the pair of answers that agree least."""
    scores = pair_scores(matrix)
    count = len(sentences)
    first, second = min(
        ((i, j) for i in range(count) for j in range(i + 1, count)),
        key=lambda pair: scores[pair[0]][pair[1]],
    )
    tokens, weights = attention_map(sentences[first], sentences[second])
    return {"pair": (first, second), "tokens": tokens, "weights": weights}
