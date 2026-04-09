import tkinter as tk
from typing_logic import calculate_speed_accuracy, generate_text, start_timer, calculate_time_taken, TypingState

# ── Global state ──────────────────────────────────────────────────────────────
state = TypingState()
best_speed = 0

# ── Window ────────────────────────────────────────────────────────────────────
window = tk.Tk()
window.title("Typing Test")
window.geometry("1200x700")
window.configure(bg="#323437")
window.resizable(False, False)

main_frame = tk.Frame(window, bg="#323437")
main_frame.pack(expand=True, fill="both")

# ── Header ────────────────────────────────────────────────────────────────────
header = tk.Frame(main_frame, bg="#323437")
header.pack(pady=(40, 20))
tk.Label(header, text="Typing Test", font=("Roboto", 16),
         fg="#d1d0c5", bg="#323437").pack()

# ── Mode buttons ──────────────────────────────────────────────────────────────
mode_frame = tk.Frame(main_frame, bg="#323437")
mode_frame.pack(pady=(0, 20))

def set_mode(selected_mode):
    state.mode = selected_mode
    _refresh_sub_bar()
    restart_test()

for m in ["time", "words", "quote", "zen", "custom"]:
    tk.Button(mode_frame, text=m, font=("Roboto", 12),
              fg="#d1d0c5", bg="#323437",
              activebackground="#2c2e31", activeforeground="#d1d0c5",
              relief="flat", bd=0, padx=15, pady=5,
              command=lambda md=m: set_mode(md)).pack(side="left", padx=5)

# ── Sub-bar ───────────────────────────────────────────────────────────────────
sub_bar    = tk.Frame(main_frame, bg="#323437")
sub_bar.pack(pady=(0, 30))
word_frame = tk.Frame(sub_bar, bg="#323437")
time_frame = tk.Frame(sub_bar, bg="#323437")

def set_word_count(count):
    state.word_count = int(count)
    restart_test()

def set_time_limit(seconds):
    state.time_limit = seconds
    restart_test()

for wc in ["10", "25", "50", "100"]:
    tk.Button(word_frame, text=wc, font=("Roboto", 12),
              fg="#d1d0c5", bg="#323437",
              activebackground="#2c2e31", activeforeground="#d1d0c5",
              relief="flat", bd=0, padx=12, pady=3,
              command=lambda c=wc: set_word_count(c)).pack(side="left", padx=3)

for t in [15, 30, 60, 120]:
    tk.Button(time_frame, text=str(t), font=("Roboto", 12),
              fg="#d1d0c5", bg="#323437",
              activebackground="#2c2e31", activeforeground="#d1d0c5",
              relief="flat", bd=0, padx=12, pady=3,
              command=lambda s=t: set_time_limit(s)).pack(side="left", padx=3)

def _refresh_sub_bar():
    word_frame.pack_forget()
    time_frame.pack_forget()
    if state.is_words_mode():
        word_frame.pack()
    elif state.is_time_mode():
        time_frame.pack()

word_frame.pack()   # default

# ── Stats bar ─────────────────────────────────────────────────────────────────
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

timer_label = tk.Label(stats_frame, text="", font=("Roboto", 24, "bold"),
                        fg="#e2b714", bg="#323437")

# ── Typing area ───────────────────────────────────────────────────────────────
typing_frame = tk.Frame(main_frame, bg="#323437")
typing_frame.pack(pady=(0, 30))

text_display = tk.Text(
    typing_frame, height=3, width=80,
    font=("Roboto Mono", 18), bg="#323437", fg="#d1d0c5",
    relief="flat", bd=0, wrap="word", state="disabled",
    cursor="none", spacing1=4, spacing3=4,
)
text_display.pack()

input_box = tk.Text(
    typing_frame, height=1, width=80,
    font=("Roboto Mono", 18), bg="#323437",
    fg="#323437", insertbackground="#323437",
    relief="flat", bd=0
)
input_box.pack()
input_box.focus_set()

# ── Text tags ─────────────────────────────────────────────────────────────────
text_display.tag_configure("correct",   foreground="#d1d0c5")
text_display.tag_configure("incorrect", foreground="#ff4757", background="#3d1f24")
text_display.tag_configure("cursor",    foreground="#232628", background="#e2b714")
text_display.tag_configure("untyped",   foreground="#646669")
text_display.tag_configure("extra",     foreground="#ff4757", background="#3d1f24",
                            underline=True)

# ── Restart button ────────────────────────────────────────────────────────────
restart_btn = tk.Button(main_frame, text="restart", font=("Roboto", 12),
                         fg="#d1d0c5", bg="#323437",
                         activebackground="#2c2e31", activeforeground="#d1d0c5",
                         relief="flat", bd=0, padx=15, pady=8,
                         command=lambda: restart_test())
restart_btn.pack()

# ══════════════════════════════════════════════════════════════════════════════
# RESULTS OVERLAY
# ══════════════════════════════════════════════════════════════════════════════
results_frame = tk.Frame(window, bg="#323437")
# (not packed until test ends)

# ── Large WPM display ─────────────────────────────────────────────────────────
res_top = tk.Frame(results_frame, bg="#323437")
res_top.pack(pady=(60, 10))

tk.Label(res_top, text="wpm", font=("Roboto", 13),
         fg="#646669", bg="#323437").grid(row=0, column=0, padx=40)
tk.Label(res_top, text="acc", font=("Roboto", 13),
         fg="#646669", bg="#323437").grid(row=0, column=1, padx=40)
tk.Label(res_top, text="time", font=("Roboto", 13),
         fg="#646669", bg="#323437").grid(row=0, column=2, padx=40)
tk.Label(res_top, text="best", font=("Roboto", 13),
         fg="#646669", bg="#323437").grid(row=0, column=3, padx=40)

res_wpm_val  = tk.Label(res_top, text="0",  font=("Roboto", 64, "bold"),
                         fg="#e2b714", bg="#323437")
res_wpm_val.grid(row=1, column=0, padx=40)

res_acc_val  = tk.Label(res_top, text="0%", font=("Roboto", 64, "bold"),
                         fg="#d1d0c5", bg="#323437")
res_acc_val.grid(row=1, column=1, padx=40)

res_time_val = tk.Label(res_top, text="0s", font=("Roboto", 64, "bold"),
                         fg="#d1d0c5", bg="#323437")
res_time_val.grid(row=1, column=2, padx=40)

res_best_val = tk.Label(res_top, text="0",  font=("Roboto", 64, "bold"),
                         fg="#d1d0c5", bg="#323437")
res_best_val.grid(row=1, column=3, padx=40)

# ── Divider ───────────────────────────────────────────────────────────────────
tk.Frame(results_frame, bg="#2c2e31", height=2, width=700).pack(pady=30)

# ── Restart prompt ────────────────────────────────────────────────────────────
res_bottom = tk.Frame(results_frame, bg="#323437")
res_bottom.pack(pady=10)

tk.Button(res_bottom, text="restart",
          font=("Roboto", 14),
          fg="#d1d0c5", bg="#2c2e31",
          activebackground="#646669", activeforeground="#d1d0c5",
          relief="flat", bd=0, padx=24, pady=10,
          command=lambda: restart_test()).pack(side="left", padx=15)

tk.Label(res_bottom, text="or press  Tab",
         font=("Roboto", 12), fg="#646669", bg="#323437").pack(side="left")

# ── New-best banner ───────────────────────────────────────────────────────────
res_newbest = tk.Label(results_frame, text="🏆  New best!",
                        font=("Roboto", 14, "bold"),
                        fg="#e2b714", bg="#323437")
# (packed only when new best is achieved)

def show_results(speed, accuracy, time_taken):
    """Hide the typing UI and show the results overlay."""
    global best_speed

    is_new_best = speed > best_speed
    if is_new_best:
        best_speed = speed

    # Fill in values
    res_wpm_val.config(text=str(int(speed)))
    res_acc_val.config(text=f"{int(accuracy)}%")
    res_time_val.config(text=f"{int(time_taken)}s")
    res_best_val.config(text=str(int(best_speed)),
                        fg="#e2b714" if is_new_best else "#d1d0c5")

    if is_new_best:
        res_newbest.pack(pady=(0, 10))
    else:
        res_newbest.pack_forget()

    # Swap frames
    main_frame.pack_forget()
    results_frame.pack(expand=True, fill="both")

    # Bind Tab on the results frame too
    window.bind("<Tab>",    lambda e: restart_test())
    window.bind("<Return>", lambda e: restart_test())
    window.bind("<Escape>", lambda e: restart_test())

def hide_results():
    results_frame.pack_forget()
    main_frame.pack(expand=True, fill="both")
    window.unbind("<Tab>")
    window.unbind("<Return>")
    window.unbind("<Escape>")

# ── Cursor blink ──────────────────────────────────────────────────────────────
cursor_visible   = True
cursor_blink_job = None

def blink_cursor():
    global cursor_visible, cursor_blink_job
    cursor_visible = not cursor_visible
    _paint_cursor(cursor_visible)
    cursor_blink_job = window.after(530, blink_cursor)

def _paint_cursor(visible):
    text_display.tag_remove("cursor", "1.0", tk.END)
    if not visible:
        return
    pos = _cursor_tk_index()
    if pos:
        text_display.tag_add("cursor", pos, f"{pos}+1c")

def _cursor_tk_index():
    current_input = input_box.get("1.0", tk.END).strip()
    char_col = 0
    for i in range(state.scroll_offset, len(state.words)):
        word = state.words[i]
        if i == state.current_word_idx:
            if not word:
                return None
            typed_len = len(current_input)
            col = char_col + (min(typed_len, len(word) - 1) if typed_len >= len(word) else typed_len)
            return f"1.{col}"
        char_col += len(word) + 1
    return None

# ── Countdown ─────────────────────────────────────────────────────────────────
def _start_countdown():
    state.start_countdown(state.time_limit, timer_label, calculate_final_result)
    _tick()

def _tick():
    if state.start_time is None:
        return
    state.time_remaining -= 1
    color = "#ff4757" if state.time_remaining <= 10 else "#e2b714"
    timer_label.config(text=str(state.time_remaining), fg=color)
    if state.time_remaining <= 0:
        calculate_final_result()
    else:
        state.timer_job = window.after(1000, _tick)

def _cancel_countdown():
    state.cancel_countdown()
    if state.timer_job is not None:
        window.after_cancel(state.timer_job)
        state.timer_job = None

def _show_timer_label():
    timer_label.pack(side="left", padx=20)
    timer_label.config(text=str(state.time_limit), fg="#e2b714")

def _hide_timer_label():
    timer_label.pack_forget()

# ── Scroll helpers ────────────────────────────────────────────────────────────
def _build_line_start_words():
    return state.build_line_start_words(text_display)

def _check_and_scroll():
    state.check_and_scroll(text_display, window, _render_visible)

# ── Rendering ─────────────────────────────────────────────────────────────────
def _insert_completed_word(word_i):
    word, typed = state.words[word_i], state.typed_words[word_i]
    for c_i, ch in enumerate(word):
        tag = "correct" if c_i < len(typed) and typed[c_i] == ch else "incorrect"
        text_display.insert(tk.END, ch, tag)

def _insert_active_word(current_input):
    word = state.words[state.current_word_idx]
    for c_i, ch in enumerate(word):
        if c_i < len(current_input):
            text_display.insert(tk.END, ch,
                                "correct" if current_input[c_i] == ch else "incorrect")
        else:
            text_display.insert(tk.END, ch, "untyped")
    if len(current_input) > len(word):
        text_display.insert(tk.END, current_input[len(word):], "extra")

def _render_visible():
    text_display.config(state="normal")
    text_display.delete("1.0", tk.END)
    current_input = input_box.get("1.0", tk.END).strip()
    for word_i in range(state.scroll_offset, len(state.words)):
        if word_i < len(state.typed_words):
            _insert_completed_word(word_i)
        elif word_i == state.current_word_idx:
            _insert_active_word(current_input)
        else:
            text_display.insert(tk.END, state.words[word_i], "untyped")
        if word_i < len(state.words) - 1:
            text_display.insert(tk.END, " ", "untyped")
    text_display.config(state="disabled")
    _paint_cursor(cursor_visible)

def update_text_display():
    _render_visible()
    window.after(10, _check_and_scroll)

# ── Stats update ──────────────────────────────────────────────────────────────
def update_stats():
    rolling_wpm, accuracy = state.update_stats(sentence)
    wpm_label.config(text=str(rolling_wpm))
    accuracy_label.config(text=str(accuracy))

# ── Key handler ───────────────────────────────────────────────────────────────
def on_key_press(event):
    if event.keysym in ("Tab", "Return", "Escape"):
        restart_test()
        return "break"

    if state.start_time is None:
        state.start()
        if state.is_time_mode():
            _start_countdown()

    current_input = input_box.get("1.0", tk.END).strip()

    if event.keysym == "space":
        if current_input:
            state.complete_word(current_input)

            if state.is_words_mode() and state.current_word_idx >= len(state.words):
                window.after(10, calculate_final_result)
                return "break"

            if state.is_time_mode() and state.current_word_idx >= len(state.words) - 10:
                state.extend_words()

            input_box.delete("1.0", tk.END)
            update_text_display()
            update_stats()
        return "break"

    elif event.keysym == "BackSpace":
        if not current_input and state.typed_words:
            prev = state.undo_word()
            input_box.delete("1.0", tk.END)
            input_box.insert("1.0", prev)
        update_text_display()
        update_stats()

    else:
        window.after(1, _after_keypress)

    update_stats()

def _after_keypress():
    _render_visible()
    update_stats()

def _extend_words():
    state.extend_words()

# ── Restart ───────────────────────────────────────────────────────────────────
def restart_test():
    global sentence

    _cancel_countdown()
    hide_results()

    sentence = state.reset(state.mode, state.word_count, state.time_limit)

    wpm_label.config(text="0")
    accuracy_label.config(text="100")

    if state.is_time_mode():
        _show_timer_label()
        timer_label.config(text=str(state.time_limit), fg="#e2b714")
    else:
        _hide_timer_label()

    input_box.config(state="normal")
    input_box.delete("1.0", tk.END)
    update_text_display()
    input_box.focus_set()

# ── Final result ──────────────────────────────────────────────────────────────
def calculate_final_result():
    _cancel_countdown()

    if state.start_time is None:
        return

    speed, accuracy, time_taken = state.calculate_result(sentence)

    state.start_time = None
    input_box.config(state="disabled")

    # Final result uses true average WPM (full test), not the rolling window
    show_results(speed, accuracy, time_taken)

# ── Bind & initialise ─────────────────────────────────────────────────────────
input_box.bind("<Key>", on_key_press)

sentence = state.reset()
update_text_display()
blink_cursor()

window.mainloop()