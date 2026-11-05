"""Asks the language model the same question several times (U1, U2)."""

import torch
from transformers import AutoModelForCausalLM, AutoTokenizer

import config

tokenizer = AutoTokenizer.from_pretrained(config.LLM_MODEL)
model = AutoModelForCausalLM.from_pretrained(config.LLM_MODEL, dtype=torch.bfloat16).to("cuda")


def build_messages(question, prompt_name):
    prompt = config.PROMPTS[prompt_name]
    messages = [{"role": "system", "content": prompt["system"]}]
    for example_question, example_answer in prompt["examples"]:
        messages.append({"role": "user", "content": example_question})
        messages.append({"role": "assistant", "content": example_answer})
    messages.append({"role": "user", "content": question})
    return messages


def sample_answers(question, prompt_name=config.DEFAULT_PROMPT,
                   temperature=config.TEMPERATURE, num_samples=config.NUM_SAMPLES):
    """Return num_samples independent answers to one question."""
    text = tokenizer.apply_chat_template(
        build_messages(question, prompt_name), tokenize=False, add_generation_prompt=True
    )
    inputs = tokenizer(text, return_tensors="pt").to(model.device)

    # One call produces all the answers side by side, which is much faster
    # than five separate calls and gives each one its own random path.
    with torch.no_grad():
        output = model.generate(
            **inputs,
            do_sample=True,
            temperature=temperature,
            top_p=config.TOP_P,
            top_k=0,
            max_new_tokens=config.MAX_NEW_TOKENS,
            num_return_sequences=num_samples,
            pad_token_id=tokenizer.eos_token_id,
        )

    new_tokens = output[:, inputs["input_ids"].shape[1]:]
    return [answer.strip() for answer in tokenizer.batch_decode(new_tokens, skip_special_tokens=True)]
