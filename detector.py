"""Joins the steps: sample the answers, judge them, turn the score into a verdict."""

import config
import judge
import sampler
import vision


def verdict_for(agreement):
    """Turn the agreement score into what the user is told (U5)."""
    if agreement < config.AGREEMENT_THRESHOLD:
        return {
            "level": "low",
            "title": "Likely hallucination",
            "advice": "The model keeps changing its story. Do not rely on this answer.",
        }
    if agreement < config.STRONG_AGREEMENT:
        return {
            "level": "mixed",
            "title": "Unsure",
            "advice": "Some answers agree and some do not. Check a trusted source first.",
        }
    return {
        "level": "high",
        "title": "Consistent",
        "advice": "The model gave the same answer each time. "
                  "That is a good sign, but a model can repeat the same mistake.",
    }


def package(question, answers, sentences, mode):
    result = judge.judge(sentences)
    result.update({
        "question": question,
        "answers": answers,
        "sentences": sentences,
        "mode": mode,
        "verdict": verdict_for(result["agreement"]),
        "focus": judge.weakest_pair_attention(sentences, result["matrix"]),
    })
    return result


def check_text(question, prompt_name=config.DEFAULT_PROMPT, temperature=config.TEMPERATURE):
    answers = sampler.sample_answers(question, prompt_name, temperature)
    return package(question, answers, answers, "text")


def check_image(image, question, temperature=config.VQA_TEMPERATURE):
    answers = vision.sample_image_answers(image, question, temperature)
    sentences = [vision.as_sentence(answer) for answer in answers]
    return package(question, answers, sentences, "image")
