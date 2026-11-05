"""Image questions with BLIP (U3) and test images with SD-Turbo (Layer IV)."""

import torch
from diffusers import AutoPipelineForText2Image
from transformers import BlipForQuestionAnswering, BlipProcessor

import config

DEVICE = config.VISION_DEVICE


def load_painter(device):
    pipeline = AutoPipelineForText2Image.from_pretrained(
        config.IMAGE_MODEL,
        dtype=torch.float16 if device == "cuda" else torch.float32,
        variant="fp16",
    ).to(device)
    pipeline.set_progress_bar_config(disable=True)
    return pipeline


processor = BlipProcessor.from_pretrained(config.VQA_MODEL)
vqa_model = BlipForQuestionAnswering.from_pretrained(config.VQA_MODEL).to(DEVICE).eval()
painter = load_painter(DEVICE)

# Copies for when the GPU is refused, see config.CPU_FALLBACK.
cpu_vqa_model = cpu_painter = None
if config.CPU_FALLBACK:
    cpu_vqa_model = BlipForQuestionAnswering.from_pretrained(config.VQA_MODEL).eval()
    cpu_painter = load_painter("cpu")


def sample_image_answers(image, question, temperature=config.VQA_TEMPERATURE,
                         num_samples=config.NUM_SAMPLES, device="cuda"):
    """Ask BLIP the same question about an image several times."""
    model = cpu_vqa_model if device == "cpu" and cpu_vqa_model else vqa_model
    inputs = processor(image.convert("RGB"), question, return_tensors="pt").to(model.device)
    answers = []
    with torch.no_grad():
        for _ in range(num_samples):
            # top_p keeps sampling among sensible words. Without it, BLIP's long
            # tail of rare tokens produces junk such as "##ginal".
            output = model.generate(
                **inputs, do_sample=True, temperature=temperature,
                top_p=config.VQA_TOP_P, top_k=0, max_new_tokens=12,
            )
            answers.append(processor.decode(output[0], skip_special_tokens=True).strip())
    return answers


def as_sentence(answer):
    """BLIP gives one or two words. MNLI needs a sentence to compare."""
    return "The answer is %s." % answer


def make_test_image(prompt, device="cuda"):
    """One-step image generation, fast enough to use during a demo."""
    pipeline = cpu_painter if device == "cpu" and cpu_painter else painter
    with torch.no_grad():
        return pipeline(prompt, num_inference_steps=1, guidance_scale=0.0, width=512, height=512).images[0]
