# Python Wordle GUI

A Wordle clone built using Python and Tkinter with Object-Oriented Programming. Features a real-time grid interface, smart word validation using Zipf frequency, and simple animations for feedback.

> If anything is incorrect or something seems unclear, please let me know!

---

## Features

* GUI built with Tkinter
* 5-letter word validation using Zipf frequency
* Real-time feedback with color-coded tiles
* Shake animation on invalid guesses
* Clean OOP structure

---

## Requirements

* Python 3.12.9  
* Anaconda (recommended for environment management)  
* Visual Studio Code  

All required packages are listed in `imports.txt`.

---

## Installation & Run

1. Clone this repo:
    ```bash
    git clone https://github.com/yourusername/python-wordle-gui.git
    cd python-wordle-gui
    
    ```

2. Create and activate the environment:
    ```bash
    conda create -n wordle-env python=3.12.9
    conda activate wordle-env

    ```

3. Install dependencies:

    ```bash
    pip install -r imports.txt

    ```
    
4. Run the game:
    ```bash
    python wordle_gui.py

    ```