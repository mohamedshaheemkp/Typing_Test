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

# ══════════════════════════════════════════════════════════════════════════════
# TYPING STATE CLASS
# ══════════════════════════════════════════════════════════════════════════════

class TypingState:
    """Manages the state of a typing test session."""
    
    def __init__(self):
        self.start_time = None
        self.words = []
        self.typed_words = []
        self.current_word_idx = 0
        self.scroll_offset = 0
        self.time_remaining = 0
        self.word_timestamps = []
        self.timer_job = None
        self.mode = "words"  # or "time"
        self.word_count = 25
        self.time_limit = 60
        self.best_speed = 0
        
        # Constants
        self.ROLLING_WINDOW = 10  # seconds for rolling WPM
        self.SCROLL_THRESHOLD = 2  # lines before scrolling

    def update_stats(self, sentence):
        """Update rolling WPM and accuracy statistics."""
        if self.start_time is None:
            return 0, 100

        now = time.time()
        time_taken = calculate_time_taken(self.start_time)
        if time_taken < 0.1:
            return 0, 100

        # ── Rolling WPM ───────────────────────────────────────────────────────────
        # Keep only timestamps within the rolling window
        cutoff = now - self.ROLLING_WINDOW
        recent = [ts for ts in self.word_timestamps if ts[0] >= cutoff]

        if len(recent) >= 2:
            window_duration = recent[-1][0] - recent[0][0]
            rolling_wpm = (len(recent) / window_duration) * 60 if window_duration > 0.1 else 0
        elif len(recent) == 1 and time_taken >= 1:
            # Single word typed — fall back to raw so display isn't stuck at 0
            rolling_wpm = (1 / time_taken) * 60
        else:
            rolling_wpm = 0

        # ── Accuracy (always full history) ────────────────────────────────────────
        typed_text = " ".join(self.typed_words)
        _, accuracy = calculate_speed_accuracy(sentence, typed_text, time_taken)

        return int(rolling_wpm), int(accuracy)

    def start_countdown(self, time_limit, timer_label, on_timeout):
        """Start the countdown timer for time mode."""
        self.time_remaining = time_limit
        timer_label.config(text=str(self.time_remaining))
        self._tick(timer_label, on_timeout)

    def _tick(self, timer_label, on_timeout):
        """Internal countdown tick function."""
        if self.start_time is None:
            return
        self.time_remaining -= 1
        color = "#ff4757" if self.time_remaining <= 10 else "#e2b714"
        timer_label.config(text=str(self.time_remaining), fg=color)
        if self.time_remaining <= 0:
            on_timeout()
        else:
            # Note: This would need to be scheduled by the UI layer
            pass

    def cancel_countdown(self):
        """Cancel the countdown timer."""
        if self.timer_job is not None:
            # Note: This would need to be handled by the UI layer
            self.timer_job = None

    def extend_words(self):
        """Extend the word list when running low in time mode."""
        extra = generate_text(50)
        self.words += extra.split()

    def build_line_start_words(self, text_display):
        """Build list of word indices that start each line."""
        line_starts, prev_y, char_col = [], None, 0
        for i in range(self.scroll_offset, len(self.words)):
            try:
                info = text_display.dlineinfo(f"1.{char_col}")
            except Exception:
                break
            if info is None:
                break
            y = info[1]
            if y != prev_y:
                line_starts.append(i)
                prev_y = y
            char_col += len(self.words[i]) + 1
        return line_starts

    def check_and_scroll(self, text_display, window, render_callback):
        """Check if scrolling is needed and update scroll offset."""
        window.update_idletasks()
        line_starts = self.build_line_start_words(text_display)
        if len(line_starts) < 2:
            return
        active_line_idx = None
        for li, first_word in enumerate(line_starts):
            next_first = line_starts[li + 1] if li + 1 < len(line_starts) else len(self.words) + 1
            if first_word <= self.current_word_idx < next_first:
                active_line_idx = li
                break
        if active_line_idx is not None and active_line_idx > self.SCROLL_THRESHOLD:
            self.scroll_offset = line_starts[1]
            render_callback()

    def reset(self, mode="words", word_count=25, time_limit=60):
        """Reset the typing state for a new test."""
        self.start_time = None
        self.current_word_idx = 0
        self.typed_words = []
        self.scroll_offset = 0
        self.time_remaining = time_limit
        self.word_timestamps = []
        self.mode = mode
        self.word_count = word_count
        self.time_limit = time_limit

        count = 200 if mode == "time" else word_count
        sentence = generate_text(count)
        self.words = sentence.split()
        return sentence

    def complete_word(self, word):
        """Complete a word and record the timestamp."""
        import time
        self.typed_words.append(word)
        self.current_word_idx = len(self.typed_words)
        self.word_timestamps.append((time.time(), self.current_word_idx - 1))

    def undo_word(self):
        """Undo the last completed word and return it."""
        if self.typed_words:
            prev = self.typed_words.pop()
            self.current_word_idx = len(self.typed_words)
            return prev
        return ""

    def start(self):
        """Start the typing test timer."""
        if self.start_time is None:
            self.start_time = start_timer()

    def calculate_result(self, sentence):
        """Calculate final typing results."""
        time_taken = calculate_time_taken(self.start_time)
        typed_text = " ".join(self.typed_words)
        speed, accuracy = calculate_speed_accuracy(sentence, typed_text, time_taken)
        return speed, accuracy, time_taken

    def is_time_mode(self):
        """Check if the current mode is time-based."""
        return self.mode == "time"

    def is_words_mode(self):
        """Check if the current mode is word-based."""
        return self.mode == "words"