import random
import tkinter as tk
from wordfreq import top_n_list, zipf_frequency

# --- Constants -------------------------------------------------------------
TILE_SIZE = 60
TILE_PADDING = 5
GRID_ROWS = 6
GRID_COLS = 5
ANIM_DELAY = 150 
MIN_ZIPF = 3.0
WORDS_SAMPLE = 100_000

#--Game-----------------------------------------------------------------------
class WordleGUI(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Python Wordle")
        self.configure(bg="#121213")
        self.resizable(False, False)
        self.words = self.load_words()
        self._create_widgets()
        self._start_game()

    def load_words(self):
        """
        Return a list **and** a set of 5-letter words that all satisfy the
        *same* rules you’ll use for validating guesses.
        """
        top_words = top_n_list("en", WORDS_SAMPLE)

        words = [
            w.lower() for w in top_words
            if len(w) == 5
            and w.isalpha()
            and zipf_frequency(w, "en") >= MIN_ZIPF 
        ]
        self.word_set = set(words)
        return words
    
    def _create_widgets(self):
        """
        Set up the GUI elements: title, grid canvas, entry box, control buttons, and message label.
        """
        tk.Label(self, text="PYTHON WORDLE", font=('Helvetica', 24, 'bold'),
                 fg='white', bg="#121213").pack(pady=(10,0))
        width = GRID_COLS*(TILE_SIZE + TILE_PADDING) + TILE_PADDING
        height = GRID_ROWS*(TILE_SIZE + TILE_PADDING) + TILE_PADDING
        self.canvas = tk.Canvas(self, width=width, height=height,
                                bg="#121213", highlightthickness=0)
        self.canvas.pack(pady=10)

        self.tiles = []
        for r in range(GRID_ROWS):
            row = []
            for c in range(GRID_COLS):
                x1 = TILE_PADDING + c*(TILE_SIZE + TILE_PADDING)
                y1 = TILE_PADDING + r*(TILE_SIZE + TILE_PADDING)
                rect = self.canvas.create_rectangle(
                    x1, y1, x1+TILE_SIZE, y1+TILE_SIZE,
                    fill="#3a3a3c", outline="")
                text = self.canvas.create_text(
                    x1+TILE_SIZE/2, y1+TILE_SIZE/2,
                    text="", font=('Helvetica', 32, 'bold'), fill='white')
                row.append({'rect': rect, 'text': text})
            self.tiles.append(row)

        self.entry = tk.Entry(self, font=('Helvetica', 18), width=6,
                              justify='center')
        self.entry.pack()
        self.entry.bind("<Return>", lambda e: self._submit_guess())
        self.entry.bind("<KeyRelease>", self._on_key)

        ctrl = tk.Frame(self, bg="#121213")
        ctrl.pack(pady=10)
        tk.Button(ctrl, text="New Game", font=('Helvetica', 12),
                  bg="#538d4e", fg='white', command=self._start_game).grid(row=0, column=0, padx=5)
        tk.Button(ctrl, text="Quit", font=('Helvetica', 12),
                  bg="#d3d6da", command=self.destroy).grid(row=0, column=1, padx=5)

        self.message = tk.Label(self, text="", font=('Helvetica', 14),
                                fg='white', bg="#121213")
        self.message.pack()

    def _start_game(self):
        """
        Pick a new secret word, reset grid and message, and enable entry for guesses.
        """
        self.secret = random.choice(self.words)
        self.current_row = 0
        self.message.config(text="")
        self.entry.config(state='normal')
        self.entry.delete(0, tk.END)
        self.entry.focus_set()

        for r in range(GRID_ROWS):
            for c in range(GRID_COLS):
                self.canvas.itemconfigure(self.tiles[r][c]['rect'], fill="#3a3a3c")
                self.canvas.itemconfigure(self.tiles[r][c]['text'], text="")

    def _on_key(self, event):
        """
        Handle key releases in the entry: update tile letters and enforce length limit.
        """
        word = self.entry.get().upper()
        if len(word) > GRID_COLS:
            word = word[:GRID_COLS]
            self.entry.delete(0, tk.END)
            self.entry.insert(0, word)
        for i, ch in enumerate(word):
            self.canvas.itemconfigure(self.tiles[self.current_row][i]['text'], text=ch)
        for i in range(len(word), GRID_COLS):
            self.canvas.itemconfigure(self.tiles[self.current_row][i]['text'], text="")

    def _submit_guess(self):
        """
        Validate the current guess, reject if invalid, otherwise color tiles and proceed.
        """
        guess = self.entry.get().lower()
        if len(guess) != GRID_COLS:
            self._reject_guess("Enter exactly 5 letters"); return
        if not guess.isalpha():
            self._reject_guess("Letters only, please"); return
        # check if real word by zipf frequency and presence in word list
        if guess not in self.word_set:
            self._reject_guess("Not a valid word"); return

        colors = self._feedback(guess)
        for i, col in enumerate(colors):
            self.after(i * ANIM_DELAY, lambda i=i, col=col:
                       self.canvas.itemconfigure(self.tiles[self.current_row][i]['rect'], fill=col))
        self.entry.config(state='disabled')
        self.after(len(colors)*ANIM_DELAY + 200, lambda: self._after_guess(guess))

    def _reject_guess(self, msg):
        """
        Display rejection message and shake window for invalid guess.
        """
        self.message.config(text=msg)
        self._shake()

    def _after_guess(self, guess):
        """
        Check win/loss after a guess and either end game or move to next row.
        """
        self.message.config(text="")
        if guess == self.secret:
            self.message.config(text=f"You won in {self.current_row+1} tries!")
            self.entry.config(state='disabled')
            return
        self.current_row += 1
        if self.current_row >= GRID_ROWS:
            self.message.config(text=f"Out of tries! Word was {self.secret.upper()}")
            self.entry.config(state='disabled')
            return
        self.entry.config(state='normal')
        self.entry.delete(0, tk.END)
        self.entry.focus_set()

    def _feedback(self, guess):
        """
        Return a list of 5 color codes for a guess against the secret (green/yellow/gray).
        """
        fb = ['#3a3a3c'] * GRID_COLS
        secret_chars = list(self.secret)
        for i, ch in enumerate(guess):
            if ch == self.secret[i]:
                fb[i] = '#538d4e'
                secret_chars[i] = None
        for i, ch in enumerate(guess):
            if fb[i] == '#3a3a3c' and ch in secret_chars:
                fb[i] = '#b59f3b'
                secret_chars[secret_chars.index(ch)] = None
        return fb

    def _shake(self):
        """
        Perform a quick shake animation on the window to indicate error.
        """
        x, y = self.winfo_x(), self.winfo_y()
        for dx in (-10,10,-6,6,-2,2,0):
            self.geometry(f"+{x+dx}+{y}")
            self.update()
        self.after(100, lambda: self.geometry(f"+{x}+{y}"))

if __name__ == "__main__":
    app = WordleGUI()
    app.update_idletasks()
    w, h = app.winfo_width(), app.winfo_height()
    x = (app.winfo_screenwidth()//2) - (w//2)
    y = (app.winfo_screenheight()//2) - (h//2)
    app.geometry(f"{w}x{h}+{x}+{y}")
    app.mainloop()
