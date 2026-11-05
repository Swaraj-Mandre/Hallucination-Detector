"""Image questions with BLIP (U3) and test images with SD-Turbo (Layer IV)."""

import torch
from diffusers import AutoPipelineForText2Image
from transformers import BlipForQuestionAnswering, BlipProcessor

import config

DEVICE = config.VISION_DEVICE

processor = BlipProcessor.from_pretrained(config.VQA_MODEL)
vqa_model = BlipForQuestionAnswering.from_pretrained(config.VQA_MODEL).to(DEVICE).eval()

painter = AutoPipelineForText2Image.from_pretrained(
    config.IMAGE_MODEL,
    torch_dtype=torch.float16 if DEVICE == "cuda" else torch.float32,
    variant="fp16",
).to(DEVICE)
painter.set_progress_bar_config(disable=True)


def sample_image_answers(image, question, temperature=config.VQA_TEMPERATURE,
                         num_samples=config.NUM_SAMPLES):
    """Ask BLIP the same question about an image several times."""
    inputs = processor(image.convert("RGB"), question, return_tensors="pt").to(DEVICE)
    answers = []
    with torch.no_grad():
        for _ in range(num_samples):
            # top_p keeps sampling among sensible words. Without it, BLIP's long
            # tail of rare tokens produces junk such as "##ginal".
            output = vqa_model.generate(
                **inputs, do_sample=True, temperature=temperature,
                top_p=config.VQA_TOP_P, top_k=0, max_new_tokens=12,
            )
            answers.append(processor.decode(output[0], skip_special_tokens=True).strip())
    return answers


def as_sentence(answer):
    """BLIP gives one or two words. MNLI needs a sentence to compare."""
    return "The answer is %s." % answer


def make_test_image(prompt):
    """One-step image generation, fast enough to use during a demo."""
    with torch.no_grad():
        return painter(prompt, num_inference_steps=1, guidance_scale=0.0, width=512, height=512).images[0]
