#!/usr/bin/env python3
"""
benchmark.py - Solitaire AI Benchmark & Simulation CLI

Unifies performance benchmarking and game simulation by delegating directly
to the SolitaireEngine core methods.
"""

import sys
import os
import argparse
import random

# Ensure local module import works regardless of CWD
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, SCRIPT_DIR)

from solitaire_engine import SolitaireEngine


def print_benchmark_report(data):
    meta = data['metadata']
    summary = data['summary']

    print("=" * 65)
    print("                     BENCHMARK REPORT")
    print("=" * 65)
    print(f"Total Games Played:        {meta['total_games']:,}")
    print(f"Total Completed Wins:      {summary['wins']:,} games")
    print(f"Overall Win Rate:          {summary['win_rate_percent']:.2f}%")
    print(f"Average Final Score:       {summary['average_score']:.1f}")
    print(f"Average Turns to Win:      {summary['average_turns_per_win']:.1f} moves")
    print(f"Average Foundation Cards:  {summary['average_foundation_cards']:.1f} / 52")
    print(f"Execution Duration:        {meta['execution_time_seconds']:.2f}s ({meta['games_per_second']:.1f} games/sec)")

    print("\n" + "-" * 65)
    print("FOUNDATION CLEARANCE DISTRIBUTION:")
    print("-" * 65)
    num_games = meta['total_games']
    for b_name, count in summary['distribution'].items():
        pct = (count / num_games) * 100
        bar = "█" * int(pct / 2)
        print(f"  {b_name:<18}: {count:>4} ({pct:>5.1f}%) {bar}")

    winning_seeds = data.get('winning_seeds', [])
    if winning_seeds:
        print("\n" + "-" * 65)
        print("SAMPLE VERIFIED WINNING SEEDS:")
        print("-" * 65)
        for w in winning_seeds[:5]:
            print(f"  • Seed {w['seed']}: Won in {w['moves']} moves with Score {w['score']}")

    first_win = winning_seeds[0]['seed'] if winning_seeds else None
    if first_win:
        print("\n" + "=" * 65)
        print("🎯 READY TO WATCH IN GUI:")
        print("=" * 65)
        print(f"Run this command to watch the AI win Seed {first_win} live in GUI:")
        print(f"\n  python3 main_gui.py --seed {first_win}\n")


def test_single_seed(seed):
    print(f"Testing single seed: {seed}...")
    random.seed(seed)
    engine = SolitaireEngine()
    engine.enable_history = False
    
    res = engine.simulate_game()
    status = "🏆 VICTORY!" if res['won'] else "🛑 Stalemate"
    print(f"\nResult for Seed {seed}:")
    print(f"  • Status:            {status}")
    print(f"  • Total Moves:       {res['moves']}")
    print(f"  • Final Score:       {res['score']}")
    print(f"  • Foundation Cards:  {res['cards_cleared']} / 52")
    print(f"  • Piles:             {res['foundations']}\n")
    if res['won']:
        print(f"To watch this winning game live in GUI:\n  python3 main_gui.py --seed {seed}\n")


def main():
    parser = argparse.ArgumentParser(
        description="Solitaire AI - Benchmark & Monte Carlo Simulation Tool",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""Examples:
  python3 benchmark.py --games 1000
  python3 benchmark.py --games 5000 --export results.json
  python3 benchmark.py --seed 10002
"""
    )
    parser.add_argument('--games', type=int, default=1000, help="Number of games to benchmark (default: 1000)")
    parser.add_argument('--start-seed', type=int, default=10000, help="Starting seed offset (default: 10000)")
    parser.add_argument('--export', type=str, default=None, help="Path to export JSON results (e.g. results.json)")
    parser.add_argument('--seed', type=int, default=None, help="Test a single specific seed directly")

    args = parser.parse_args()

    if args.seed is not None:
        test_single_seed(args.seed)
        return

    print("=" * 65)
    print(f"🃏 SOLITAIRE AI - MONTE CARLO BENCHMARK ({args.games:,} GAMES)")
    print("=" * 65)
    print(f"• Target Games:   {args.games:,}")
    print(f"• Seed Range:     {args.start_seed:,} -> {args.start_seed + args.games - 1:,}")
    if args.export:
        print(f"• Export Output:  {args.export}")
    print("• Running simulation via SolitaireEngine...\n")

    data = SolitaireEngine.run_benchmark(
        num_games=args.games,
        start_seed=args.start_seed,
        export_path=args.export
    )

    print_benchmark_report(data)

    if args.export:
        print(f"[OK] Results exported successfully to: {os.path.abspath(args.export)}")


if __name__ == '__main__':
    main()
