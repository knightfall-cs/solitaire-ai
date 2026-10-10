# Solitaire AI

[![Python](https://img.shields.io/badge/Python-3.10%2B-blue.svg)](https://www.python.org/)
[![Pygame](https://img.shields.io/badge/Pygame-2.5.2-green.svg)](https://www.pygame.org/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

**Solitaire AI** is an animated desktop Klondike Solitaire application built with Python and Pygame. It integrates an intelligent heuristic AI solver, real-time move recommendations, automated bot play, reproducible game seeds, and a high-speed headless Monte Carlo simulation benchmark engine capable of processing over 600 games per second.

---

## Table of Contents

- [Installation](#installation)
- [Usage](#usage)
  - [1. Launch Interactive GUI](#1-launch-interactive-gui)
  - [2. Launch GUI with a Specific Seed](#2-launch-gui-with-a-specific-seed)
  - [3. Run Headless Benchmarks & Simulations](#3-run-headless-benchmarks--simulations)
- [Features](#features)
- [Controls & Interface](#controls--interface)
- [Benchmark CLI Options](#benchmark-cli-options)
- [Game Rules & Notes](#game-rules--notes)
- [Authors](#authors)
- [License](#license)
- [Acknowledgments](#acknowledgments)

---

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

It is recommended to use an isolated Python virtual environment:

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

Upgrade `pip` and install required packages:

```bash
python -m pip install --upgrade pip
pip install -r requirements.txt
```

*(Alternative)* Using [uv](https://github.com/astral-sh/uv):
```bash
uv pip install -r requirements.txt
```

---

## Usage

### 1. Launch Interactive GUI

Start the graphical Solitaire application:

- **Linux / macOS**:
  ```bash
  python3 main_gui.py
  ```

- **Windows**:
  ```cmd
  python main_gui.py
  ```

### 2. Launch GUI with a Specific Seed

Replay a known board configuration or test a verified winning seed:

```bash
python3 main_gui.py --seed 10002
```

### 3. Run Headless Benchmarks & Simulations

Simulate games at high speed (~600+ games/sec) using the Monte Carlo solver CLI without loading graphics:

```bash
# Run a quick 1,000-game benchmark
python3 benchmark.py --games 1000

# Run a 5,000-game benchmark and export complete metrics to JSON
python3 benchmark.py --games 5000 --export results.json

# Test a single seed directly in headless mode
python3 benchmark.py --seed 10002
```

---

## Features

- **Royal Felt Tabletop Aesthetic**: Deep emerald green felt theme with antiqued gold borders, clean card faces, and crisp vector typography.
- **Intelligent Heuristic Solver**: Analyzes foundation targets, face-down card reveals, empty column utility, and stock cycling to select optimal moves.
- **Real-Time AI Hints**: Visual glowing highlights pointing from source cards to optimal destination piles.
- **Automated Bot Play**: Watch the AI execute real-time animated moves with configurable playback speed (`1x`, `2x`, `4x`).
- **Smooth Physics & Animations**: Cubic ease-out transitions for card dealing and user moves.
- **Realistic Victory Cascade**: Classic win cascade with floor restitution, horizontal impact friction, and natural settling across the table floor.
- **Full History & Undo**: Unlimited move backtracking with undo history.
- **Stalemate Detection**: Automatically identifies no-win cycle deadlocks.
- **High-Speed Headless Benchmark Engine**: Unified solver runs hundreds of games per second to analyze win rates, score distributions, and turns-to-win.

---

## Controls & Interface

| Control / Button | Action |
| :--- | :--- |
| **Left Click / Drag** | Pick up and move individual cards or valid tableau cascades |
| **Double Click** | Quick auto-move card to Foundation if valid |
| **New Game** | Deal a new shuffled deck |
| **Undo** | Revert the previous move (including draws) |
| **AI Hint** | Highlight the solver's recommended next move |
| **AI Auto-Play** | Toggle automated bot solver execution |
| **Speed: 1x / 2x / 4x** | Cycle bot playback animation speed |

---

## Benchmark CLI Options

[`benchmark.py`](benchmark.py) supports the following command-line flags:

```
options:
  -h, --help               Show help message and exit
  --games GAMES            Number of games to simulate (default: 1000)
  --start-seed START_SEED  Starting seed offset (default: 10000)
  --export EXPORT          Path to export JSON benchmark summary (e.g. results.json)
  --seed SEED              Simulate and evaluate a single specific seed directly
```

---

## Game Rules & Notes

- **Standard Klondike Solitaire**: 7 tableau columns, 4 suit foundation piles (built Ace through King), and 3-card stock draw.
- **King on Empty Column**: Only Kings (or stacks led by a King) can be placed onto empty tableau slots.
- **Display Driver on Wayland**: Pygame automatically leverages the SDL2 backend. If display server warnings appear on Linux Wayland environments, set `export SDL_VIDEODRIVER=x11`.

---

## Authors

- **Solitaire AI**: KNIGHTFALL
- **InternalProcessor.ipynb**: [@Krafer](https://www.youtube.com/@Krafer)

---

## License

This [Solitaire AI](https://github.com/knightfall-cs/solitaire-ai.git) project is licensed under the MIT License. See the [LICENSE](LICENSE) file for details.

---

## Acknowledgments

The development of [Solitaire AI](https://github.com/knightfall-cs/solitaire-ai.git) was built upon the core Klondike engine and Monte Carlo solver logic originally developed in `InternalProcessor.ipynb`, expanded with Pygame vector rendering, smooth physics animation controllers, and a unified benchmarking suite.

---

Author: KNIGHTFALL
