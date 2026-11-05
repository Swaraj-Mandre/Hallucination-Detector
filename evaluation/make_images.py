"""Creates the test images with the app's own generator, using fixed seeds."""

import sys
from pathlib import Path

import torch

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent))

import vision  # noqa: E402
from questions import IMAGE_QUESTIONS  # noqa: E402

(HERE / "images").mkdir(exist_ok=True)
for number, item in enumerate(IMAGE_QUESTIONS):
    generator = torch.Generator(vision.DEVICE).manual_seed(52 + number)
    with torch.no_grad():
        image = vision.painter(item["prompt"], num_inference_steps=1, guidance_scale=0.0,
                               width=512, height=512, generator=generator).images[0]
    image.save(HERE / "images" / item["file"])
    print("saved", item["file"])
