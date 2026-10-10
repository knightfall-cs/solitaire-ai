# Solitaire AI

Solitaire AI is an animated desktop Klondike Solitaire game built with Python and Pygame, featuring an integrated heuristic AI solver, real-time move hints, automated bot play, and Monte Carlo win-rate simulation benchmarks.

## Table of Contents

- [Usage](#usage)
- [Features](#features)
- [Installation](#installation)
- [Notes](#notes)
- [Authors](#authors)
- [License](#license)
- [Acknowledgments](#acknowledgments)

## Usage

To play the game and use the AI solver, follow these steps:

1. Clone or download this repository.

2. Open a terminal in the repository directory.

3. Run the following command:

   ```bash
   python3 main_gui.py
   ```

### In-Game Controls

- **Move Cards**: Click and drag any face-up card or card stack with the left mouse button.
- **Auto-Move to Foundation**: Double-click any eligible card to automatically send it to its suit's Foundation pile.
- **Draw Cards**: Click the face-down Stock pile to draw 3 cards (or recycle the Waste pile back to Stock).
- **New Game**: Click the `New Game` button on the top toolbar to deal a fresh hand.
- **Undo Move**: Click the `Undo` button to revert the previous card move.
- **Get AI Hint**: Click `AI Hint` to highlight the best candidate move (source card glows in orange, destination in cyan).
- **AI Auto-Play Bot**: Click `AI Auto-Play` to let the solver automatically play out the game turn-by-turn with animated card movements. Click `Pause AI` to stop at any time.
- **Adjust Bot Speed**: Click `Speed: 1x` to toggle playback speed between `1x`, `2x`, and `4x`.

## Features

- **Interactive Drag-and-Drop Gameplay**: Full support for single cards and multi-card stacks with smooth cubic ease-out movement animations.

- **Heuristic AI Solver**: Intelligent Klondike solver that prioritizes foundation moves, unblocks hidden tableau stacks, and splits card sequences to dig out critical cards.

- **Automated Bot Mode**: Watch the AI play live in real-time with smooth card sliding animations.

- **Smart Hint System**: Visual highlight indicator that recommends the best legal move on the table.

- **Stalemate Detection**: Automatically identifies when no valid moves remain across the board and deck, preventing infinite loops and gracefully displaying a `NO MORE MOVES!` notification.

- **Royal Casino Aesthetic**: Deep emerald felt background, gold metallic button borders, ivory parchment card faces, and crisp vector suit symbols (♠ ♥ ♣ ♦).

- **Monte Carlo Benchmarking**: Includes `InternalProcessor.ipynb` for running 5,000-game simulations to analyze solver win rates and score distributions.

## Installation

Before playing Solitaire AI, ensure you have [Python 3](https://www.python.org/downloads/) (Python 3.10 or higher) installed on your system.

To install the necessary dependencies, run the following command in your terminal:

```bash
python -m pip install -r requirements.txt
```

OR (only in linux):

```bash
sudo apt install python3-pygame python3-matplotlib python3-numpy
```
This installs Pygame, Matplotlib, and NumPy directly from your Linux distribution package manager.

## Notes

- The game follows standard Klondike Solitaire rules: 7 tableau columns, 4 suit foundation piles (built Ace through King), and 3-card stock draw.

- Only Kings (or card stacks starting with a King) can be placed onto empty tableau columns.

- If you wish to run the Monte Carlo simulation notebook or test custom AI solver strategies, launch Jupyter Notebook:

  ```bash
  jupyter notebook InternalProcessor.ipynb
  ```

## Authors

- Solitaire AI: KNIGHTFALL

## License

This [Solitaire AI](https://github.com/knightfall-cs/solitaire-ai.git) is licensed under the MIT License. See the [LICENSE](https://github.com/knightfall-cs/solitaire-ai/blob/main/LICENSE) file for details.

## Acknowledgments

The development of [Solitaire AI](https://github.com/knightfall-cs/solitaire-ai.git) was built upon the core Klondike engine and Monte Carlo solver logic originally developed in `InternalProcessor.ipynb`, expanded with Pygame vector rendering and smooth animation controllers.

---

Author: KNIGHTFALL
