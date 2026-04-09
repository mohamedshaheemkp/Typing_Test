import tkinter as tk
from typing_logic import calculate_speed_accuracy, generate_text, start_timer, calculate_time_taken

# ── Global state ──────────────────────────────────────────────────────────────
start_time       = None
best_speed       = 0
sentence         = ""
words            = []
current_word_idx = 0   # index into words[]
typed_words      = []  # list of completed (submitted) words
mode             = "words"
word_count       = 25

# ── Window ────────────────────────────────────────────────────────────────────
window = tk.Tk()
window.title("monkeytype")
window.geometry("1200x700")
window.configure(bg="#323437")
window.resizable(False, False)

main_frame = tk.Frame(window, bg="#323437")
main_frame.pack(expand=True, fill="both")

# ── Header ────────────────────────────────────────────────────────────────────
header = tk.Frame(main_frame, bg="#323437")
header.pack(pady=(40, 20))
tk.Label(header, text="monkeytype", font=("Roboto", 16),
         fg="#d1d0c5", bg="#323437").pack()

# ── Mode buttons ──────────────────────────────────────────────────────────────
mode_frame = tk.Frame(main_frame, bg="#323437")
mode_frame.pack(pady=(0, 20))

def set_mode(selected_mode):
    global mode
    mode = selected_mode
    if mode == "words":
        word_frame.pack(pady=(0, 30))
    else:
        word_frame.pack_forget()

for m in ["time", "words", "quote", "zen", "custom"]:
    tk.Button(mode_frame, text=m, font=("Roboto", 12),
              fg="#d1d0c5", bg="#323437",
              activebackground="#2c2e31", activeforeground="#d1d0c5",
              relief="flat", bd=0, padx=15, pady=5,
              command=lambda md=m: set_mode(md)).pack(side="left", padx=5)

# ── Word-count buttons ────────────────────────────────────────────────────────
word_frame = tk.Frame(main_frame, bg="#323437")
word_frame.pack(pady=(0, 30))

def set_word_count(count):
    global word_count
    word_count = int(count)
    restart_test()

for wc in ["10", "25", "50", "100"]:
    tk.Button(word_frame, text=wc, font=("Roboto", 12),
              fg="#d1d0c5", bg="#323437",
              activebackground="#2c2e31", activeforeground="#d1d0c5",
              relief="flat", bd=0, padx=12, pady=3,
              command=lambda c=wc: set_word_count(c)).pack(side="left", padx=3)

# ── Stats display ─────────────────────────────────────────────────────────────
stats_frame = tk.Frame(main_frame, bg="#323437")
stats_frame.pack(pady=(0, 20))

wpm_label = tk.Label(stats_frame, text="0", font=("Roboto", 24, "bold"),
                     fg="#e2b714", bg="#323437")
wpm_label.pack(side="left", padx=20)
tk.Label(stats_frame, text="wpm", font=("Roboto", 12),
         fg="#646669", bg="#323437").pack(side="left")

accuracy_label = tk.Label(stats_frame, text="100", font=("Roboto", 24, "bold"),
                           fg="#d1d0c5", bg="#323437")
accuracy_label.pack(side="left", padx=20)
tk.Label(stats_frame, text="%", font=("Roboto", 12),
         fg="#646669", bg="#323437").pack(side="left")

# ── Typing area ───────────────────────────────────────────────────────────────
typing_frame = tk.Frame(main_frame, bg="#323437")
typing_frame.pack(pady=(0, 30))

text_display = tk.Text(
    typing_frame, height=3, width=80,
    font=("Roboto Mono", 18), bg="#323437", fg="#d1d0c5",
    relief="flat", bd=0, wrap="word", state="disabled",
    cursor="none"          # hide the text-widget's own cursor
)
text_display.pack()

# Hidden input box – invisible but captures keystrokes
input_box = tk.Text(
    typing_frame, height=1, width=80,
    font=("Roboto Mono", 18), bg="#323437",
    fg="#323437",           # same as bg → invisible text
    insertbackground="#323437",  # invisible caret
    relief="flat", bd=0
)
input_box.pack()
input_box.focus_set()

# ── Text tags ─────────────────────────────────────────────────────────────────
text_display.tag_configure("correct",   foreground="#d1d0c5")   # typed correctly → white
text_display.tag_configure("incorrect", foreground="#ff4757",
                            background="#3d1f24")               # wrong char → red + tint
text_display.tag_configure("cursor",    foreground="#d1d0c5",
                            background="#e2b714")               # current char → yellow bg
text_display.tag_configure("untyped",   foreground="#646669")   # not yet reached → grey
text_display.tag_configure("extra",     foreground="#ff4757",
                            background="#3d1f24")               # extra chars beyond word → red

# ── Cursor blink state ────────────────────────────────────────────────────────
cursor_visible = True
cursor_blink_job = None

def blink_cursor():
    """Toggle the cursor highlight on the current character every 530 ms."""
    global cursor_visible, cursor_blink_job
    if start_time is None and len(typed_words) == 0:
        # not started yet – always show cursor
        _paint_cursor(True)
        cursor_blink_job = window.after(530, blink_cursor)
        return
    cursor_visible = not cursor_visible
    _paint_cursor(cursor_visible)
    cursor_blink_job = window.after(530, blink_cursor)

def _paint_cursor(visible):
    """Add or remove the cursor highlight without redrawing everything."""
    text_display.tag_remove("cursor", "1.0", tk.END)
    if not visible:
        return
    pos = _cursor_position()
    if pos is not None:
        text_display.tag_add("cursor", pos, f"{pos}+1c")

def _cursor_position():
    """
    Return the tkinter index of the character the cursor sits ON.
    The cursor sits on the next character to be typed inside current_word_idx.
    """
    char_offset = 0
    current_typed_in_word = input_box.get("1.0", tk.END).strip()

    for i, word in enumerate(words):
        if i == current_word_idx:
            # cursor lives at char_offset + len(already typed in this word)
            col = char_offset + len(current_typed_in_word)
            # clamp to end of word (for over-type)
            col = min(col, char_offset + len(word))
            line = 1
            return f"{line}.{col}"
        char_offset += len(word) + 1  # +1 for the space
    return None

# ── Core display update ───────────────────────────────────────────────────────
def update_text_display():
    """
    Rebuild the full character-level display.

    For completed words (typed_words):
        each character is tagged correct / incorrect / extra.
    For the active word (current_word_idx):
        typed portion → correct / incorrect, remainder → untyped.
    For future words:
        all characters → untyped.
    Spaces between words are always untyped.
    """
    text_display.config(state="normal")
    text_display.delete("1.0", tk.END)

    current_input = input_box.get("1.0", tk.END).strip()

    for word_i, word in enumerate(words):

        if word_i < len(typed_words):
            # ── Completed word ────────────────────────────────────────────────
            typed = typed_words[word_i]
            max_len = max(len(word), len(typed))

            for c_i in range(max_len):
                if c_i < len(word) and c_i < len(typed):
                    tag = "correct" if typed[c_i] == word[c_i] else "incorrect"
                    text_display.insert(tk.END, word[c_i], tag)
                elif c_i < len(word):
                    # character in word but not typed (shouldn't happen after submit, but safe)
                    text_display.insert(tk.END, word[c_i], "incorrect")
                else:
                    # extra character typed beyond word length → show as red underline
                    # we show the typed extra char (but word is shorter, so display word char if exists)
                    pass  # extra chars are silently dropped in display; word boundary is fixed

        elif word_i == current_word_idx:
            # ── Active word ───────────────────────────────────────────────────
            for c_i, ch in enumerate(word):
                if c_i < len(current_input):
                    tag = "correct" if current_input[c_i] == ch else "incorrect"
                    text_display.insert(tk.END, ch, tag)
                else:
                    text_display.insert(tk.END, ch, "untyped")

            # Extra characters typed beyond the word
            if len(current_input) > len(word):
                extra = current_input[len(word):]
                text_display.insert(tk.END, extra, "extra")

        else:
            # ── Future word ───────────────────────────────────────────────────
            text_display.insert(tk.END, word, "untyped")

        # Space between words
        if word_i < len(words) - 1:
            text_display.insert(tk.END, " ", "untyped")

    text_display.config(state="disabled")
    # Repaint cursor immediately after redraw
    _paint_cursor(cursor_visible)

# ── Stats update ──────────────────────────────────────────────────────────────
def update_stats():
    if start_time is None:
        return
    time_taken = calculate_time_taken(start_time)
    if time_taken < 0.1:
        return
    typed_text = " ".join(typed_words)
    speed, accuracy = calculate_speed_accuracy(sentence, typed_text, time_taken)
    wpm_label.config(text=str(int(speed)))
    accuracy_label.config(text=str(int(accuracy)))

# ── Key handler ───────────────────────────────────────────────────────────────
def on_key_press(event):
    global start_time, current_word_idx, typed_words

    # Start timer on first keystroke
    if start_time is None and event.keysym not in ("Tab", "Return", "Escape"):
        start_time = start_timer()

    current_input = input_box.get("1.0", tk.END).strip()

    if event.keysym == "space":
        # ── Space: submit current word ────────────────────────────────────────
        if current_input:  # only if something was typed
            typed_words.append(current_input)
            current_word_idx = len(typed_words)

            if current_word_idx >= len(words):
                window.after(10, calculate_final_result)
                return "break"

            # Clear input box for next word
            input_box.delete("1.0", tk.END)
            update_text_display()
            update_stats()
        return "break"   # always swallow space so it doesn't appear in input_box

    elif event.keysym == "BackSpace":
        # ── Backspace: allow going back to previous word if input is empty ────
        if not current_input and typed_words:
            # Restore previous word into input box
            prev = typed_words.pop()
            current_word_idx = len(typed_words)
            input_box.delete("1.0", tk.END)
            input_box.insert("1.0", prev)
        update_text_display()
        update_stats()

    elif event.keysym in ("Tab", "Return"):
        # ── Tab / Enter: restart ──────────────────────────────────────────────
        restart_test()
        return "break"

    elif event.keysym == "Escape":
        restart_test()
        return "break"

    else:
        # Regular character – let tkinter insert it, then refresh display
        window.after(1, _after_keypress)

    update_stats()

def _after_keypress():
    """Called 1 ms after a regular keypress so the char is already in input_box."""
    update_text_display()
    update_stats()

# ── Restart ───────────────────────────────────────────────────────────────────
def restart_test():
    global start_time, current_word_idx, typed_words, sentence, words

    start_time       = None
    current_word_idx = 0
    typed_words      = []
    sentence         = generate_text(word_count)
    words            = sentence.split()

    wpm_label.config(text="0")
    accuracy_label.config(text="100")
    input_box.config(state="normal")
    input_box.delete("1.0", tk.END)
    update_text_display()
    input_box.focus_set()

# ── Final result ──────────────────────────────────────────────────────────────
def calculate_final_result():
    global best_speed, start_time

    if start_time is None:
        return

    time_taken  = calculate_time_taken(start_time)
    typed_text  = " ".join(typed_words)
    speed, accuracy = calculate_speed_accuracy(sentence, typed_text, time_taken)

    if speed > best_speed:
        best_speed = speed

    wpm_label.config(text=str(int(speed)))
    accuracy_label.config(text=str(int(accuracy)))
    input_box.config(state="disabled")

    text_display.config(state="normal")
    text_display.insert(tk.END, "\n\nTest complete! Tab or Restart to go again.", "untyped")
    text_display.config(state="disabled")

    start_time = None

# ── Restart button ────────────────────────────────────────────────────────────
tk.Button(main_frame, text="restart", font=("Roboto", 12),
          fg="#d1d0c5", bg="#323437",
          activebackground="#2c2e31", activeforeground="#d1d0c5",
          relief="flat", bd=0, padx=15, pady=8,
          command=restart_test).pack()

# ── Bind events ───────────────────────────────────────────────────────────────
input_box.bind("<Key>", on_key_press)

# ── Initialise ────────────────────────────────────────────────────────────────
sentence = generate_text(word_count)
words    = sentence.split()
update_text_display()
blink_cursor()   # start the blink loop

window.mainloop()