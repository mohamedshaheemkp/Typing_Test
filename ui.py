import tkinter as tk

#import logic

from typing_logic import calculate_speed_accuracy
from typing_logic import generate_text
from typing_logic import start_timer
from typing_logic import calculate_time_taken

start_time = None
best_speed = 0
sentence = ""

mode = "words"
word_count = 25

#window creation
window = tk.Tk()
window.title("Typing Test")
window.geometry("900x500")
window.configure(bg="#1e1f22")
window.resizable(False, False)

header = tk.Frame(window, bg="#1e1f22")
header.pack(pady=10)

title_label = tk.Label(
    header,
    text="TYPING TEST",
    font=("Segoe UI", 18, "bold"),
    fg="#d6d6d6",
    bg="#1e1f22"
)

title_label.pack()

mode_frame = tk.Frame(window, bg="#1e1f22")
mode_frame.pack(pady=5)

modes = ["time", "words", "quote"]

for m in modes:
    btn = tk.Button(
        mode_frame,
        text=m,
        font=("Segoe UI", 10),
        fg="#777",
        bg="#1e1f22",
        relief="flat",
        command=lambda md=m: set_mode(md)
    )
    btn.pack(side="left", padx=12)

selected_mode = tk.StringVar(value="25")

def set_mode(selected_mode):
    global mode
    mode = selected_mode

def set_word_count(count):
    global word_count
    word_count = int(count)

settings_frame = tk.Frame(window, bg="#1e1f22")
settings_frame.pack(pady=10)

settings = ["10", "25", "50", "100"]

for s in settings:
    btn = tk.Button(
        settings_frame,
        text=s,
        font=("Segoe UI", 10),
        fg="#aaa",
        bg="#1e1f22",
        relief="flat",
        command=lambda c=s: set_word_count(c)
    )
    btn.pack(side="left", padx=10)

lang_label = tk.Label(
    window,
    text="english",
    font=("Segoe UI", 10),
    fg="#777",
    bg="#1e1f22"
)

lang_label.pack(pady=10)

#functions 

#-------------------UI ELEMENTS--------------------
def submit_on_enter(event):
    if start_time is None:
        start_test()
    else:
        calculate_result()

    return "break"

def start_test():
    global sentence, start_time

    sentence = generate_text(word_count)
    sentence_label.config(text=sentence)

    text_box.delete("1.0", tk.END)

    start_time = start_timer()

def calculate_result():
    global best_speed, start_time

    if start_time is None:
        return

    time_taken = calculate_time_taken(start_time)

    typed = text_box.get("1.0", tk.END).strip()

    speed, accuracy = calculate_speed_accuracy(sentence, typed, time_taken)

    if speed > best_speed:
        best_speed = speed

    result = f"WPM: {round(speed,2)} | Accuracy: {round(accuracy,2)}% | Best: {round(best_speed,2)}"

    result_label.config(text=result)

    start_time = None

def on_typing(event):
    global start_time

    if start_time is None:
        start_test()

def check_typing(event):
    typed = text_box.get("1.0", tk.END).strip()

    if typed == sentence:
        calculate_result()

#sentence label

sentence_label = tk.Label(
    window,
    text="Press any key to start",
    font=("Consolas", 20),
    fg="#777",
    bg="#1e1f22",
    wraplength=850,
    justify="left"
)

sentence_label.pack(pady=20)

#text box

text_box = tk.Text(
    window,
    height=1,
    width=60,
    font=("Consolas", 18),
    bg="#1e1f22",
    fg="#ffffff",
    insertbackground="#f1c40f",
    relief="flat",
    bd=0
)

text_box.pack()

text_box.bind("<Return>", submit_on_enter)

text_box.bind("<KeyPress>", on_typing)

text_box.focus_set()

hint_label = tk.Label(
    window,
    text="Press Enter to restart",
    font=("Segoe UI", 9),
    fg="#555",
    bg="#1e1f22"
)

hint_label.pack(pady=20)

#result label

result_label = tk.Label(
    window,
    text="",
    font=("Segoe UI", 12),
    fg="#f1c40f",
    bg="#1e1f22"
)

result_label.pack()

#close loop
window.mainloop()