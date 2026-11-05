"""Every setting for the detector, kept in one place."""

import os

# Models
LLM_MODEL = "Qwen/Qwen2.5-3B-Instruct"
NLI_MODEL = "FacebookAI/roberta-large-mnli"
VQA_MODEL = "Salesforce/blip-vqa-base"
IMAGE_MODEL = "stabilityai/sd-turbo"

# The hosted GPU fits everything. An 8 GB laptop GPU does not, so a local run
# can move the image models to the CPU with VISION_DEVICE=cpu.
VISION_DEVICE = os.getenv("VISION_DEVICE", "cuda")

# Sampling (U1). Five answers at a fixed temperature. Hot enough for an unsure
# model to wander, cool enough for a sure model to repeat itself.
NUM_SAMPLES = 5
TEMPERATURE = 0.8
TOP_P = 0.95
MAX_NEW_TOKENS = 64

# BLIP answers in one or two words, so it gets its own sampling settings.
VQA_TEMPERATURE = 0.8
VQA_TOP_P = 0.9

# The image generator has no safety filter of its own, and the app is public.
BLOCKED_IMAGE_WORDS = {
    "nude", "naked", "nsfw", "porn", "sexual", "sex", "gore", "blood", "beheading",
    "child abuse", "suicide", "self-harm", "nazi",
}

# Below this agreement score the app warns the user (U5).
AGREEMENT_THRESHOLD = 0.5

# At or above this the answers are called consistent. In between is "unsure".
STRONG_AGREEMENT = 0.8

# Two answers count as "the same claim" above this pair score.
SAME_CLAIM_SCORE = 0.5

# The prompt styles that are compared in the evaluation.
PROMPTS = {
    "Direct": {
        "system": "Answer the question in one short sentence.",
        "examples": [],
    },
    "Few-shot": {
        "system": "Answer the question in one short sentence.",
        "examples": [
            ("What is the capital of Japan?", "The capital of Japan is Tokyo."),
            ("Who painted the Mona Lisa?", "Leonardo da Vinci painted the Mona Lisa."),
            ("How many legs does a spider have?", "A spider has eight legs."),
        ],
    },
    "Cautious": {
        "system": (
            "Answer the question in one short sentence. Only state what you are "
            "sure of. If you are not sure, or the question has a wrong "
            "assumption, say so instead of guessing."
        ),
        "examples": [],
    },
}
DEFAULT_PROMPT = "Direct"
