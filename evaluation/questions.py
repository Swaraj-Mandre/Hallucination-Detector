"""
The 20 test questions, with the correct answers written down in advance.

`accept` lists words that a correct answer must contain, any one of them. For
questions with a false premise, or about something that does not exist, a
correct answer has to reject the question, so `accept` holds rejection words.
Automatic marks are then reviewed by hand, see manual_marks.py.
"""

REJECT = ["not ", "never", "no ", "n't", "does not exist", "fictional", "unknown", "cannot", "unable"]

TEXT_QUESTIONS = [
    # Common facts
    {"kind": "common", "question": "What is the chemical symbol for gold?", "accept": ["Au"]},
    {"kind": "common", "question": "Who wrote the novel Pride and Prejudice?", "accept": ["Austen"]},
    {"kind": "common", "question": "What is the largest planet in our solar system?", "accept": ["Jupiter"]},
    {"kind": "common", "question": "In which country is the Taj Mahal located?", "accept": ["India"]},
    {"kind": "common", "question": "How many bones are in the adult human body?", "accept": ["206"]},
    # Less common facts
    {"kind": "obscure", "question": "Who was the first woman to win a Fields Medal?", "accept": ["Mirzakhani"]},
    {"kind": "obscure", "question": "What is the capital of Burkina Faso?", "accept": ["Ouagadougou"]},
    {"kind": "obscure", "question": "Who was the second Prime Minister of India?", "accept": ["Shastri", "Nanda"]},
    {"kind": "obscure", "question": "Which element has atomic number 74?", "accept": ["Tungsten", "Wolfram"]},
    {"kind": "obscure", "question": "In what year was the Treaty of Tordesillas signed?", "accept": ["1494"]},
    {"kind": "obscure", "question": "Who directed the 1957 Japanese film Throne of Blood?", "accept": ["Kurosawa"]},
    {"kind": "obscure", "question": "What is the highest mountain in Bhutan?", "accept": ["Gangkhar"]},
    # False premise
    {"kind": "false premise", "question": "In which year did Isaac Newton win the Nobel Prize in Physics?", "accept": REJECT},
    {"kind": "false premise", "question": "In which year did Mahatma Gandhi become Prime Minister of India?", "accept": REJECT},
    # Things that do not exist
    {"kind": "made up", "question": "What is the capital of the African country of Zandovia?", "accept": REJECT},
    {"kind": "made up", "question": "Who discovered the chemical element Morvium?", "accept": REJECT},
]

# Images are made with the app's own generator, so there is no copyright issue.
# Their contents were checked by eye before the answers were written down.
IMAGE_QUESTIONS = [
    {"kind": "image", "file": "red_bus.png", "prompt": "a photo of a red double decker bus on a city street",
     "question": "What colour is the bus?", "accept": ["red"]},
    {"kind": "image", "file": "two_dogs.png", "prompt": "a photo of two dogs sitting on a beach",
     "question": "How many dogs are there?", "accept": ["2", "two"]},
    {"kind": "image", "file": "oranges.png", "prompt": "a photo of a white bowl full of oranges on a table",
     "question": "What fruit is in the bowl?", "accept": ["orange"]},
    {"kind": "image", "file": "shop_sign.png", "prompt": "a photo of a small shop with a sign above the door",
     "question": "What is the name of the shop?", "accept": []},
]
