# Solitaire AI

Solitaire AI is an animated desktop Klondike Solitaire game built with Python and Pygame, featuring an integrated heuristic AI solver, real-time move hints, automated bot play, and Monte Carlo win-rate simulation benchmarks.

## Table of Contents

- [Installation](#installation)
- [Usage](#usage)
- [Features](#features)
- [Notes](#notes)
- [Authors](#authors)
- [License](#license)
- [Acknowledgments](#acknowledgments)

## Installation

### Prerequisites

Ensure the following tools are installed on your system:
- **Python**: Version 3.10 or higher ([Download Python](https://www.python.org/downloads/))
- **Git**: For source version control ([Download Git](https://git-scm.com/))
- **Pip**: Standard Python package installer

### Step 1: Clone the Repository

Clone the project repository to your local machine and navigate into the project directory:

```bash
git clone https://github.com/knightfall-cs/solitaire-ai.git
cd solitaire-ai
```

### Step 2: Configure a Virtual Environment

It is recommended to use an isolated Python virtual environment to manage project dependencies:

- **On Linux / macOS**:

  ```bash
  python3 -m venv .venv
  source .venv/bin/activate
  ```

- **On Windows (Command Prompt)**:

  ```cmd
  python -m venv .venv
  .venv\Scripts\activate
  ```

- **On Windows (PowerShell)**:

  ```powershell
  python -m venv .venv
  .venv\Scripts\Activate.ps1
  ```

### Step 3: Install Dependencies

Upgrade `pip` to the latest version and install the required packages:

```bash
python -m pip install --upgrade pip
pip install -r requirements.txt
```

*(Alternative)* If you use [uv](https://github.com/astral-sh/uv), dependencies can be installed via:

```bash
uv pip install -r requirements.txt
```

## Usage

### Launching the Application

With your virtual environment activated, launch the game by executing the main entry point:

- **Linux / macOS**:

  ```bash
  python3 main_gui.py
  ```

- **Windows**:

  ```cmd
  python main_gui.py
  ```

### User Interface & Controls

| Control | Description |
|---|---|
| **Left Click + Drag** | Pick up and move any face-up card or card stack between Tableau columns and Foundation piles. |
| **Double Click** | Automatically send an eligible card to its respective Foundation pile. |
| **Click Stock Pile** | Draw 3 cards to the Waste pile, or recycle the Waste pile when the Stock is depleted. |
| **New Game** | Reset the board state and deal a fresh 52-card Klondike deal. |
| **Undo** | Revert the most recent move using the engine's state history stack. |
| **AI Hint** | Evaluate legal moves and highlight the optimal move (source card in orange, destination in cyan). |
| **AI Auto-Play** | Toggle the automated bot to play moves in real time with animated transitions. Click **Pause AI** to halt. |
| **Speed Toggle** | Cycle AI playback animation speed between `1x`, `2x`, and `4x`. |

### Running the Simulation Notebook

To inspect the solver algorithms or run the 5,000-game Monte Carlo simulation benchmark:

```bash
jupyter notebook InternalProcessor.ipynb
```

## Features

- **Interactive Drag-and-Drop Gameplay**: Full support for single cards and multi-card stacks with smooth cubic ease-out movement animations.

- **Heuristic AI Solver**: Intelligent Klondike solver that prioritizes foundation moves, unblocks hidden tableau stacks, and splits card sequences to dig out critical cards.

- **Automated Bot Mode**: Watch the AI play live in real-time with smooth card sliding animations.

- **Smart Hint System**: Visual highlight indicator that recommends the best legal move on the table.

- **Stalemate Detection**: Automatically identifies when no valid moves remain across the board and deck, preventing infinite loops and gracefully displaying a `NO MORE MOVES!` notification.

- **Royal Casino Aesthetic**: Deep emerald felt background, gold metallic button borders, ivory parchment card faces, and crisp vector suit symbols (♠ ♥ ♣ ♦).

- **Monte Carlo Benchmarking**: Includes `InternalProcessor.ipynb` for running 5,000-game simulations to analyze solver win rates and score distributions.

## Notes

- The game adheres to standard Klondike Solitaire rules: 7 tableau columns, 4 suit foundation piles (built Ace through King), and 3-card stock draw.

- Only Kings (or card stacks starting with a King) can be placed onto empty tableau columns.

- On Linux systems utilizing Wayland, Pygame uses the SDL2 backend automatically. If you encounter display driver warnings, you may optionally set `export SDL_VIDEODRIVER=x11`.

## Authors

- Solitaire AI: KNIGHTFALL

## License

This [Solitaire AI](https://github.com/knightfall-cs/solitaire-ai.git) is licensed under the MIT License. See the [LICENSE](https://github.com/knightfall-cs/solitaire-ai/blob/main/LICENSE) file for details.

## Acknowledgments

The development of [Solitaire AI](https://github.com/knightfall-cs/solitaire-ai.git) was built upon the core Klondike engine and Monte Carlo solver logic originally developed in `InternalProcessor.ipynb`, expanded with Pygame vector rendering and smooth animation controllers.

---

Author: KNIGHTFALL
