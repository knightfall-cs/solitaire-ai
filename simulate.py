#!/usr/bin/env python3
import sys
import os
import time
import json
import random
import argparse

# Ensure local module import works regardless of CWD
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, SCRIPT_DIR)

from solitaire_engine import SolitaireEngine


def run_simulation(num_games=1000, start_seed=10000, export_path=None, launch_gui=False):
    print("=" * 65)
    print(f"🃏 SOLITAIRE AI - MONTE CARLO SIMULATION ({num_games:,} GAMES)")
    print("=" * 65)
    print(f"• Target Games:   {num_games:,}")
    print(f"• Seed Range:     {start_seed:,} -> {start_seed + num_games - 1:,}")
    if export_path:
        print(f"• Export Output:  {export_path}")
    print("• Simulating games in headless mode...\n")

    engine = SolitaireEngine()
    engine.enable_history = False  # Bypasses deepcopy undo stack for maximum speed

    start_time = time.time()
    wins = 0
    stalemates = 0
    scores = []
    moves_per_win = []
    foundation_counts = []
    winning_games = []

    # Distribution brackets
    brackets = {
        '0-10 cards': 0,
        '11-20 cards': 0,
        '21-30 cards': 0,
        '31-40 cards': 0,
        '41-51 cards': 0,
        '52 cards (WIN)': 0
    }

    for i in range(num_games):
        seed = start_seed + i
        random.seed(seed)
        engine.new_game()
        engine.enable_history = False

        steps = 0
        max_steps = 600

        while steps < max_steps:
            if engine.is_won() or engine.is_stalemate():
                break
            moved = engine.execute_ai_step()
            if not moved:
                break
            steps += 1

        cards_on_found = sum(len(p) for p in engine.foundation.values())
        scores.append(engine.score)
        foundation_counts.append(cards_on_found)

        if engine.is_won() or cards_on_found == 52:
            wins += 1
            moves_per_win.append(steps)
            brackets['52 cards (WIN)'] += 1
            winning_games.append({
                'seed': seed,
                'moves': steps,
                'score': engine.score,
                'foundations': {suit: len(pile) for suit, pile in engine.foundation.items()}
            })
        else:
            stalemates += 1
            if cards_on_found <= 10:
                brackets['0-10 cards'] += 1
            elif cards_on_found <= 20:
                brackets['11-20 cards'] += 1
            elif cards_on_found <= 30:
                brackets['21-30 cards'] += 1
            elif cards_on_found <= 40:
                brackets['31-40 cards'] += 1
            else:
                brackets['41-51 cards'] += 1

    elapsed = time.time() - start_time
    win_rate = (wins / num_games) * 100
    avg_score = sum(scores) / len(scores) if scores else 0
    avg_moves_win = sum(moves_per_win) / len(moves_per_win) if moves_per_win else 0
    avg_found_cards = sum(foundation_counts) / len(foundation_counts) if foundation_counts else 0

    print("=" * 65)
    print("                     SIMULATION REPORT")
    print("=" * 65)
    print(f"Total Games Played:        {num_games:,}")
    print(f"Total Completed Wins:      {wins:,} games")
    print(f"Overall Win Rate:          {win_rate:.2f}%")
    print(f"Average Final Score:       {avg_score:.1f}")
    print(f"Average Turns to Win:      {avg_moves_win:.1f} moves")
    print(f"Average Foundation Cards:  {avg_found_cards:.1f} / 52")
    print(f"Execution Duration:        {elapsed:.2f}s ({num_games / elapsed:.1f} games/sec)")

    print("\n" + "-" * 65)
    print("FOUNDATION CLEARANCE DISTRIBUTION:")
    print("-" * 65)
    for b_name, count in brackets.items():
        pct = (count / num_games) * 100
        bar = "█" * int(pct / 2)
        print(f"  {b_name:<18}: {count:>4} ({pct:>5.1f}%) {bar}")

    if winning_games:
        print("\n" + "-" * 65)
        print("SAMPLE VERIFIED WINNING SEEDS:")
        print("-" * 65)
        for w in winning_games[:5]:
            print(f"  • Seed {w['seed']}: Won in {w['moves']} moves with Score {w['score']}")

    # Export to JSON file if requested
    if export_path:
        data = {
            'metadata': {
                'total_games': num_games,
                'start_seed': start_seed,
                'execution_time_seconds': round(elapsed, 3),
                'games_per_second': round(num_games / elapsed, 1)
            },
            'summary': {
                'wins': wins,
                'stalemates': stalemates,
                'win_rate_percent': round(win_rate, 2),
                'average_score': round(avg_score, 1),
                'average_turns_per_win': round(avg_moves_win, 1),
                'average_foundation_cards': round(avg_found_cards, 1),
                'distribution': brackets
            },
            'winning_seeds': winning_games
        }
        with open(export_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2)
        print(f"\n[OK] Results exported successfully to: {os.path.abspath(export_path)}")

    first_win_seed = winning_games[0]['seed'] if winning_games else None
    if first_win_seed:
        print("\n" + "=" * 65)
        print("🎯 READY TO WATCH IN GUI:")
        print("=" * 65)
        print(f"Run this command to watch the AI win Seed {first_win_seed} live in GUI:")
        print(f"\n  python3 main_gui.py --seed {first_win_seed}\n")

    if launch_gui and first_win_seed:
        print(f"Launching GUI with winning seed {first_win_seed}...")
        os.system(f"python3 {os.path.join(SCRIPT_DIR, 'main_gui.py')} --seed {first_win_seed}")

    return winning_games


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description="Solitaire AI Monte Carlo Simulator")
    parser.add_argument('--games', type=int, default=1000, help="Number of games to simulate (default: 1000)")
    parser.add_argument('--start-seed', type=int, default=10000, help="Starting seed offset (default: 10000)")
    parser.add_argument('--export', type=str, default=None, help="Path to export JSON results (e.g. results.json)")
    parser.add_argument('--gui', action='store_true', help="Automatically launch GUI with the first winning seed")

    args = parser.parse_args()
    run_simulation(
        num_games=args.games,
        start_seed=args.start_seed,
        export_path=args.export,
        launch_gui=args.gui
    )
