from helpers import measure_time
from llama_cpp import Llama
import random

llm = Llama.from_pretrained(
    repo_id="TheBloke/Llama-2-7B-GGUF",
    filename="llama-2-7b.Q2_K.gguf",
    verbose=False
)

@measure_time
def get_answer_from_llm(prompt):
    
    output = llm(
        prompt,
        max_tokens=32, # Generate up to 32 tokens, set to None to generate up to the end of the context window
        #stop=["Q:", "\n"], # Stop generating just before the model would generate a new question
        echo=False # Echo the prompt back in the output
    ) # Generate a completion, can also call create_completion
    print(output["choices"])
    return output["choices"][0]["text"]

@measure_time
def get_random_ice_break():
    icebreaker_phrases = [
        "Начать беседу",
        "Поприветствовать собеседника",
        "Задать открытый вопрос"
    ]
    
    return get_answer_from_llm(random.choice(icebreaker_phrases))