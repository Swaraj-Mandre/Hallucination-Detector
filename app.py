"""The Gradio app. Run with: python app.py"""

import spaces  # must be imported before torch on ZeroGPU

import json

import gradio as gr

import config
import detector
import ui
import vision

MAX_QUESTION_LENGTH = 300

EXAMPLES = [
    ("A known fact", "What is the capital of Australia?"),
    ("An obscure fact", "Who won the Nobel Prize in Physics in 1962?"),
    ("A book that does not exist", "Who wrote the 1987 novel The Glass Tortoise of Nagpur?"),
]

theme = gr.themes.Base(
    font=[gr.themes.GoogleFont("IBM Plex Sans"), "system-ui", "sans-serif"],
).set(
    body_background_fill="#F6F2E9",
    body_text_color="#1E2320",
    block_background_fill="#FFFDF8",
    block_border_color="#DDD6C6",
    block_label_text_color="#5C625D",
    block_title_text_color="#1E2320",
    input_background_fill="#FFFDF8",
    input_border_color="#CFC7B5",
    input_border_color_focus="#24476B",
    button_primary_background_fill="#24476B",
    button_primary_background_fill_hover="#1B3753",
    button_primary_text_color="#FFFFFF",
    button_secondary_background_fill="#FFFDF8",
    button_secondary_background_fill_hover="#EFE9DB",
    button_secondary_text_color="#1E2320",
    button_secondary_border_color="#CFC7B5",
    slider_color="#24476B",
    checkbox_label_background_fill_selected="#24476B",
    checkbox_label_text_color_selected="#FFFFFF",
)


def clean_question(question):
    question = (question or "").strip()
    if not question:
        raise gr.Error("Please type a question first.")
    if len(question) > MAX_QUESTION_LENGTH:
        raise gr.Error("Please keep the question under %d characters." % MAX_QUESTION_LENGTH)
    return question


@spaces.GPU(duration=30)
def run_text(question, prompt_name, temperature):
    return ui.render(detector.check_text(clean_question(question), prompt_name, temperature))


@spaces.GPU(duration=30)
def run_image(image, question):
    if image is None:
        raise gr.Error("Please add an image first.")
    return ui.render(detector.check_image(image, clean_question(question)))


@spaces.GPU(duration=30)
def run_painter(prompt):
    prompt = (prompt or "").strip()
    if not prompt:
        raise gr.Error("Describe the image you want first.")
    if any(word in prompt.lower() for word in config.BLOCKED_IMAGE_WORDS):
        raise gr.Error("This app only makes everyday test images. Please try another description.")
    return vision.make_test_image(prompt)


with gr.Blocks(title="Crosscheck") as demo:
    gr.HTML(ui.MASTHEAD)

    with gr.Tabs():
        with gr.Tab("Text question"):
            question = gr.Textbox(
                label="Your question", lines=2, max_lines=4,
                placeholder="Ask something with a factual answer",
            )
            with gr.Row():
                example_buttons = [gr.Button(label, size="sm") for label, _ in EXAMPLES]
            with gr.Accordion("Settings", open=False):
                prompt_name = gr.Radio(list(config.PROMPTS), value=config.DEFAULT_PROMPT, label="Prompt style")
                temperature = gr.Slider(0.2, 1.2, value=config.TEMPERATURE, step=0.1, label="Temperature")
            text_button = gr.Button("Check this answer", variant="primary")
            text_result = gr.HTML(ui.STARTER)

        with gr.Tab("Image question"):
            with gr.Row():
                with gr.Column():
                    image = gr.Image(type="pil", label="Image", height=300)
                with gr.Column():
                    image_question = gr.Textbox(
                        label="Your question about the image", lines=2,
                        placeholder="What colour is the car?",
                    )
                    image_button = gr.Button("Check this answer", variant="primary")
                    paint_prompt = gr.Textbox(
                        label="No image? Describe one and generate it",
                        placeholder="A red bus on a rainy street",
                    )
                    paint_button = gr.Button("Generate test image")
            image_result = gr.HTML()

        with gr.Tab("How it works"):
            gr.HTML(ui.HOW_IT_WORKS)

    gr.HTML(ui.CREDIT)

    # Filled in by the browser itself, so the box is ready before the next click.
    for button, (_, text) in zip(example_buttons, EXAMPLES):
        button.click(None, outputs=question, js="() => %s" % json.dumps(text))

    text_inputs = [question, prompt_name, temperature]
    text_button.click(run_text, text_inputs, text_result)
    question.submit(run_text, text_inputs, text_result)
    image_button.click(run_image, [image, image_question], image_result)
    paint_button.click(run_painter, paint_prompt, image)
    demo.load(None, js=ui.FORCE_LIGHT)

if __name__ == "__main__":
    demo.launch(theme=theme, css=ui.CSS, head=ui.HEAD, ssr_mode=False)
