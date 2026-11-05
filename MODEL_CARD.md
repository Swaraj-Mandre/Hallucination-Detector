# Model card: Crosscheck

Crosscheck is a system built from four existing models. No model was trained or
fine-tuned for this project. This card describes how they are used together.

## What it does

It estimates whether a language model's answer is likely to be a hallucination. The
same question is asked five times and the answers are compared. If they disagree, the
user is warned.

## Models used

| Role | Model | Licence |
|---|---|---|
| Writes the five answers | Qwen/Qwen2.5-3B-Instruct | Qwen Research Licence, non-commercial |
| Judges agreement between answers | FacebookAI/roberta-large-mnli | MIT |
| Answers questions about images | Salesforce/blip-vqa-base | BSD-3-Clause |
| Makes test images | stabilityai/sd-turbo | Stability AI licence, see stability.ai/license |

The project's own code is MIT licensed. The Qwen licence limits this app to research and
study. Using it commercially would need a different language model.

## Intended use

- Teaching people that a fluent answer is not always a correct one
- A first check on short factual questions

## Not intended for

- Medical, legal, financial or safety decisions
- Fact-checking people or news stories
- Long answers, opinions or creative writing

## How the score works

Five answers are sampled at temperature 0.8. RoBERTa-MNLI compares every pair in both
directions, and the stronger direction is kept as the pair score, because a detailed
answer entails a shorter one but not the reverse. Each answer's confidence is its mean
pair score. The agreement score is the mean of those five values. Below 0.5 the app
warns the user.

## Limitations

- It measures consistency, not truth. A model that repeats the same wrong answer five
  times passes the check.
- Correct answers that are worded with different extra details can score low, which
  causes false alarms.
- RoBERTa-MNLI and the question set are English only.
- BLIP gives very short answers and can be weak on text, counting and fine detail.
- A 20-question test is small, so the results show a trend and not a precise rate.

## Bias and fairness

The language model and BLIP learned from large internet datasets and carry their biases.
Facts about well documented places and people may look more consistent than facts about
less documented ones, so the app may raise more warnings on topics from under-represented
regions and languages. This was not measured in this project.

## Privacy and safety

- Questions are processed in memory. The app has no database and keeps no history.
- No outside API is called, so questions do not leave the hosted app.
- Generated images are limited by a small list of blocked words. This is a basic filter
  and it will not stop every misuse.
- Images uploaded by users are used for that one check only.

## Results

See the [README](README.md#results) and `evaluation/results/`.
