# Solitaire AI 🃏🤖

[![Python](https://img.shields.io/badge/Python-3.10%2B-blue.svg)](https://www.python.org/)
[![Pygame](https://img.shields.io/badge/Pygame-2.5%2B-green.svg)](https://www.pygame.org/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

A modern, animated desktop **Klondike Solitaire** game built with Python and Pygame, featuring an integrated **heuristic AI solver**, real-time move hints, automated bot play, and a Monte Carlo simulation benchmark suite.

---

## ✨ Features

- 🎮 **Interactive Gameplay**:
  - Smooth card and multi-card stack drag-and-drop.
  - Double-click to automatically send eligible cards to Foundation piles.
  - Stock deck draw (3-card draw) with recycling.
  - Full move history and Undo support.
- 🤖 **AI Auto-Play Bot**:
  - Automatically analyzes board states and executes optimal moves turn-by-turn.
  - Adjustable speed multiplier (1x, 2x, 4x) for playback.
  - Visual card sliding animations while the bot plays.
- 💡 **Smart Hint System**:
  - Calculates the highest-priority legal move according to solver heuristics.
  - Highlights source cards in glowing orange and target slots in cyan.
- 🛑 **Stalemate Detection**:
  - Automatically identifies when no valid moves remain across the board and deck, gracefully pausing the AI with a `NO MORE MOVES!` notification.
- 🎨 **Royal Casino Design**:
  - Deep emerald felt table with gold metallic borders and dark velvet toolbar.
  - Crisp, high-contrast playing cards with standard suit symbols (♠ ♥ ♣ ♦).
  - Cubic ease-out sliding animations and victory celebration cascade.
- 📊 **Monte Carlo Benchmarks**:
  - Includes `InternalProcessor.ipynb` for simulating thousands of automated games and analyzing win rates and score distributions.

---

## 📁 Repository Structure

```text
solitaire-ai/
├── main_gui.py              # Main Pygame desktop GUI application
├── solitaire_engine.py      # Core Klondike game engine, rules & AI solver logic
├── card_renderer.py         # Vector-style card graphics, suits & UI slots renderer
├── animator.py              # Eased cubic interpolation animation controller
├── InternalProcessor.ipynb  # Original research notebook & Monte Carlo test suite
├── requirements.txt         # Project dependencies
├── .gitignore               # Git ignore patterns for Python & environments
├── LICENSE                  # MIT Open Source License
└── README.md                # Project documentation
```

---

## 🚀 Quick Start

### 1. Prerequisites
Ensure you have **Python 3.10+** installed on your system.

### 2. Installation
Clone this repository and install the required dependencies:

```bash
git clone https://github.com/<your-username>/solitaire-ai.git
cd solitaire-ai
pip install -r requirements.txt
```

### 3. Launch the Game
Run the main GUI application:

```bash
python3 main_gui.py
```

---

## 🕹️ Controls

| Action | Control |
|---|---|
| **Move Card / Stack** | Click and drag with Left Mouse Button |
| **Quick Foundation Move** | Double-click eligible card |
| **Draw Stock Cards** | Click face-down stock pile |
| **New Game** | Click **New Game** button in toolbar |
| **Undo Move** | Click **Undo** button in toolbar |
| **Get Move Hint** | Click **AI Hint** button |
| **Toggle AI Bot** | Click **AI Auto-Play** / **Pause AI** |
| **Change Bot Speed** | Click **Speed: 1x** button to toggle 1x / 2x / 4x |

---

## 🧠 AI Solver Architecture

The solver uses a tiered heuristic priority system:
1. **Foundation First**: Moves Aces and consecutive suit cards to Foundations to free columns and increase board clearance.
2. **Hidden Card Unlocking**: Prioritizes tableau moves that unblock columns with the highest number of facedown cards.
3. **Mid-Deck & Endgame Reorganization**: Identifies opportunities to split tableau stacks to reveal cards needed by foundations.
4. **Stock Cycling & Stalemate Prevention**: Cycles through the waste pile and terminates automatically if full passes yield no board progress.

---

## 📜 License

This project is licensed under the [MIT License](LICENSE).
