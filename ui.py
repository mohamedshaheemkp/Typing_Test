import tkinter as tk
import time
import random

#import logic

from typing_logic import calculate_speed_accuracy
from typing_logic import get_random_sentence

#window creation
window = tk.Tk()
window.title("Typing Test")
window.geometry("700x450")
window.configure(bg="#1e1f22")

#Title
title_label = tk.Label(
    window,
    text="Typing Test",
    font=("Segoe UI", 20, "bold"),
    fg="#f5f5f5",
    bg="#1e1f22"
)
title_label.pack(pady=20)

#settings 

selected_mode = tk.StringVar(value="25")

def set_mode(mode):
    selected_mode.set(mode)

settings_frame = tk.Frame(window, bg="#1e1f22")
settings_frame.pack(pady=5)

settings = ["10", "25", "50", "100", "time"]

for s in settings:
    btn = tk.Button(
        settings_frame,
        text=s,
        font=("Segoe UI", 10),
        fg="#aaa",
        bg="#1e1f22",
        activebackground="#1e1f22",
        activeforeground="white",
        relief="flat",
        command=lambda m=s: set_mode(m)
    )
    btn.pack(side="left", padx=8)

#functions 

best_speed = 0

start_time = None

#-------------------UI ELEMENTS--------------------
def submit_on_enter(event):
    global start_time

    if start_time is None:
        start_test()
    else:
        calculate_result()

    return "break"

def start_test():
    global sentence, start_time
    
    sentence = get_random_sentence()
    sentence_label.config(text=sentence)
    
    text_box.delete("1.0", tk.END)
    result_label.config(text="")

    start_time = time.time()

def calculate_result():
    global best_speed, start_time

    if start_time is None:
        return

    end_time = time.time()
    time_taken = end_time - start_time

    typed = text_box.get("1.0", tk.END).strip()

    speed, accuracy = calculate_speed_accuracy(sentence, typed, time_taken)

    if speed > best_speed:
        best_speed = speed

    result = f"Time: {round(time_taken,2)}s | Speed: {round(speed,2)} WPM | Accuracy: {round(accuracy,2)}% | Best: {round(best_speed,2)} WPM"

    result += "\nPress Enter to restart"
    result_label.config(text=result)

    start_time = None

def on_typing(event):
    global sentence, start_time

    if start_time is None:
        sentence = get_random_sentence()
        sentence_label.config(text=sentence)
        start_time = time.time()

def check_typing(event):
    typed = text_box.get("1.0", tk.END).strip()

    if typed == sentence:
        calculate_result()

#card

card = tk.Frame(
    window,
    bg="#2c2f33",
    padx=30,
    pady=25
)

card.pack(pady=30, fill="x", padx=40)
#sentences 

sentence_label = tk.Label(
    card,
    text="Press any key to start",
    wraplength=650,
    justify="center",
    font=("Segoe UI", 14),
    fg="#888",
    bg="#2c2f33"
)

sentence_label.pack(pady=15)

#text box

text_box = tk.Text(
    card,
    height=2,
    width=60,
    font=("Consolas", 14),
    bg="#1e1f22",
    fg="#ffffff",
    insertbackground="#00ff9c",
    relief="flat",
    bd=0
)

text_box.pack(pady=15)
text_box.bind("<Return>", submit_on_enter)
text_box.bind("<KeyPress>", on_typing)
text_box.bind("<KeyRelease>", check_typing)

#result label

result_label = tk.Label(
    window,
    text="",
    font=("Segoe UI", 11),
    fg="#00ff9c",
    bg="#1e1f22"
)

result_label.pack(pady=15)

#close loop
window.mainloop()