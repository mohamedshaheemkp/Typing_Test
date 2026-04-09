#imports 

import time
import random

from typing_logic import calculate_speed_accuracy
from typing_logic import get_random_sentence

#body

best_speed = 0
while True:
    
    sentence = get_random_sentence()

    print("Type this sentence:\n")
    print(sentence)
    input("\nPress Enter When Ready...")
    print("\nGet Ready...")
    for i in range(3, 0, -1):
        print(i)
        time.sleep(1)
    print("Start!\n")
    start_time = time.time()

    typed = input("\n Start Typing:\n")
    end_time = time.time()
    time_taken = end_time - start_time

    speed, accuracy = calculate_speed_accuracy(sentence, typed, time_taken)

# prints
    print("\n--- Result ---")
    print("Time taken:", round(time_taken, 2), "seconds")
    print("Speed:", round(speed, 2), "WPM")
    print("Accuracy:", round(accuracy, 2), "%")
    print("Best Speed:", round(best_speed, 2), "WPM")

# Again option
    again = input("\nPlay again? (y/n): ")

    if again != "y":
        print("Thanks for playing!")
        break