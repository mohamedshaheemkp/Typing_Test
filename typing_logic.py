import random
import time

sentences = [
    "Python makes automation easy",
    "Coding everyday improves problem solving",
    "Artificial intelligence is the future",
    "Practice makes programming easier",
    "Simple projects build strong foundations"
]

def get_random_sentence():
    return random.choice(sentences)

def generate_text(word_count):
    """Generate text with specified number of words"""
    words = []
    while len(words) < word_count:
        words.extend(get_random_sentence().split())
    return " ".join(words[:word_count])
    
def calculate_speed_accuracy(sentence, typed, time_taken):
    words = len(typed.split())
    speed = words / (time_taken / 60)

    correct_words = 0
    original_words = sentence.split()
    typed_words = typed.split()

    for i in range(min(len(original_words), len(typed_words))):
        if original_words[i] == typed_words[i]:
            correct_words += 1

    accuracy = (correct_words / len(original_words)) * 100 if len(original_words) > 0 else 0

    return speed, accuracy

def start_timer():
    """Start the typing timer"""
    return time.time()

def calculate_time_taken(start_time):
    """Calculate elapsed time since timer started"""
    return time.time() - start_time