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

With your virtual environment activated, launch the game by executing the main entry point:

- **Linux / macOS**:

  ```bash
  python3 main_gui.py
  ```

- **Windows**:

  ```cmd
  python main_gui.py
  ```

## Features

- Interactive Klondike Solitaire gameplay with smooth drag-and-drop animations.

- Integrated heuristic AI solver with move recommendations and smart hints.

- Automated AI bot mode with real-time animated card playback.

- Automatic stalemate detection and victory recognition.

- Full move history tracking with Undo functionality.

- Includes Monte Carlo simulation notebook for analyzing solver win rates.


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
