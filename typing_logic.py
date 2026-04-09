import random

sentences = [
    "Python makes automation easy",
    "Coding everyday improves problem solving",
    "Artificial intelligence is the future",
    "Practice makes programming easier",
    "Simple projects build strong foundations"
]

def get_random_sentence():
    return random.choice(sentences)
    
def calculate_speed_accuracy(sentence, typed, time_taken):
    words = len(typed.split())
    speed = words / (time_taken / 60)

    correct_words = 0
    original_words = sentence.split()
    typed_words = typed.split()

    for i in range(min(len(original_words), len(typed_words))):
        if original_words[i] == typed_words[i]:
            correct_words += 1

    accuracy = (correct_words / len(original_words)) * 100

    return speed, accuracy