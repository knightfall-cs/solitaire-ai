#!/usr/bin/env python3
"""
Unit tests validating audit fixes ISSUE-001 through ISSUE-008:
- ISSUE-001: Legal sub-stack tableau move generation
- ISSUE-002 & ISSUE-007: Strategy flags (mid_deck_strats, random_strats)
- ISSUE-003: Heuristic state scoring and cycle avoidance
- ISSUE-004: Stock/waste 3-card draw and physical recycling rules
- ISSUE-005: Unbiased 52-card deck generation
- ISSUE-008: Benchmark CLI positive game validation
"""

import unittest
import subprocess
import sys
import os

# Ensure local module import
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
PARENT_DIR = os.path.dirname(SCRIPT_DIR)
sys.path.insert(0, PARENT_DIR)

from solitaire_engine import SolitaireEngine, Card


class TestSolitaireEngineAudit(unittest.TestCase):

    def setUp(self):
        self.engine = SolitaireEngine()

    # --- ISSUE-001: Sub-stack move generation ---
    def test_sub_stack_move_generation(self):
        """Verifies that any face-up sub-stack suffix can legally move to a valid column."""
        self.engine.tableau = [[] for _ in range(7)]
        # Col 0: [9♠ (black), 8♥ (red), 7♣ (black)]
        self.engine.tableau[0] = [
            Card(9, 1, 1, face_up=True),
            Card(8, 2, 2, face_up=True),
            Card(7, 1, 3, face_up=True)
        ]
        # Col 1: [9♣ (black)] - valid destination for 8♥ (red)
        self.engine.tableau[1] = [
            Card(9, 1, 3, face_up=True)
        ]

        moves = self.engine.get_tableau_moves()
        # Find move from col 0 starting at index 1 (8♥) to col 1
        sub_move = next(
            (m for m in moves if m[0] == -1 and m[1][0] == 0 and m[1][1] == 0 and m[1][2] == 1 and m[1][3] == 1),
            None
        )
        self.assertIsNotNone(sub_move, "Legal sub-stack move for 8♥-7♣ onto 9♣ was not generated!")
        self.assertTrue(sub_move[4], "is_sub_stack flag should be True for mid-sequence moves")

        # Execute sub-stack move
        success = self.engine.move_tableau_to_tableau(src_col=0, card_idx=1, dest_col=1)
        self.assertTrue(success)
        self.assertEqual(len(self.engine.tableau[0]), 1)
        self.assertEqual(self.engine.tableau[0][0].rank, 9)
        self.assertEqual(len(self.engine.tableau[1]), 3)
        self.assertEqual(self.engine.tableau[1][1].rank, 8)
        self.assertEqual(self.engine.tableau[1][2].rank, 7)

    # --- ISSUE-002 & ISSUE-007: mid_deck_strats toggle ---
    def test_mid_deck_strats_toggle(self):
        """Verifies that mid_deck_strats flag actively controls generation of sub-stack moves."""
        self.engine.tableau = [[] for _ in range(7)]
        self.engine.tableau[0] = [
            Card(9, 1, 1, face_up=True),
            Card(8, 2, 2, face_up=True),
            Card(7, 1, 3, face_up=True)
        ]
        self.engine.tableau[1] = [Card(9, 1, 3, face_up=True)]

        # With mid_deck_strats = False, only whole-stack moves (card_idx == 0) are generated
        self.engine.mid_deck_strats = False
        moves_disabled = self.engine.get_tableau_moves()
        sub_moves_disabled = [m for m in moves_disabled if m[0] == -1 and m[1][0] == 0 and m[4] is True]
        self.assertEqual(len(sub_moves_disabled), 0, "Sub-stack moves should not be generated when mid_deck_strats=False")

        # With mid_deck_strats = True, sub-stack moves are generated
        self.engine.mid_deck_strats = True
        moves_enabled = self.engine.get_tableau_moves()
        sub_moves_enabled = [m for m in moves_enabled if m[0] == -1 and m[1][0] == 0 and m[4] is True]
        self.assertGreater(len(sub_moves_enabled), 0, "Sub-stack moves should be generated when mid_deck_strats=True")

    # --- ISSUE-003: Cycle avoidance & state signatures ---
    def test_cycle_avoidance(self):
        """Verifies that moving a card back and forth between columns is penalized to prevent cycles."""
        self.engine.tableau = [[] for _ in range(7)]
        # Col 0: [9♠, 8♥]
        self.engine.tableau[0] = [Card(9, 1, 1, face_up=True), Card(8, 2, 2, face_up=True)]
        # Col 1: [9♣]
        self.engine.tableau[1] = [Card(9, 1, 3, face_up=True)]

        # Move 8♥ from Col 0 to Col 1
        initial_sig = self.engine.get_state_signature()
        self.engine.move_tableau_to_tableau(src_col=0, card_idx=1, dest_col=1)

        # After move, initial_sig is in visited_states
        self.assertIn(initial_sig, self.engine.visited_states)

        # Candidate move to move 8♥ back from Col 1 to Col 0 should be penalized
        moves = self.engine.get_tableau_moves()
        reverse_move = next(
            (m for m in moves if m[0] == -1 and m[1][0] == 0 and m[1][1] == 1 and m[1][2] == 1 and m[1][3] == 0),
            None
        )
        self.assertIsNotNone(reverse_move, "Reverse move should be generated as a legal move")
        score = self.engine.evaluate_move(reverse_move)
        self.assertLess(score, 0, "Reverse move reproducing a visited state must have negative score")

    # --- ISSUE-004: Stock/waste 3-card draw and recycling rules ---
    def test_stock_waste_transitions(self):
        """Verifies 3-card draw mechanics, waste top accessibility, and physical deck recycling."""
        # Setup 6 cards in stock
        cards = [
            Card(1, 1, 1, face_up=False),
            Card(2, 2, 2, face_up=False),
            Card(3, 1, 3, face_up=False),
            Card(4, 2, 4, face_up=False),
            Card(5, 1, 1, face_up=False),
            Card(6, 2, 2, face_up=False)
        ]
        self.engine.stock = list(cards)  # In stock list: cards[5] is on top (.pop() order)
        self.engine.waste = []

        # First draw: pops 3 cards (rank 6, 5, 4) into waste
        drawn_count = self.engine.draw_stock_cards()
        self.assertEqual(drawn_count, 3)
        self.assertEqual(len(self.engine.stock), 3)
        self.assertEqual(len(self.engine.waste), 3)
        self.assertEqual(self.engine.waste[-1].rank, 4, "Top of waste should be the last card drawn (rank 4)")
        self.assertTrue(self.engine.waste[-1].face_up)

        # Second draw: pops remaining 3 cards (rank 3, 2, 1) into waste
        drawn_count2 = self.engine.draw_stock_cards()
        self.assertEqual(drawn_count2, 3)
        self.assertEqual(len(self.engine.stock), 0)
        self.assertEqual(len(self.engine.waste), 6)
        self.assertEqual(self.engine.waste[-1].rank, 1, "Top of waste should now be rank 1")

        # Third draw: stock is empty, so waste is recycled into stock
        recycle_count = self.engine.draw_stock_cards()
        self.assertEqual(recycle_count, 6)
        self.assertEqual(len(self.engine.stock), 6)
        self.assertEqual(len(self.engine.waste), 0)
        # All recycled stock cards must be face down
        self.assertTrue(all(not c.face_up for c in self.engine.stock))
        # First card drawn after recycling should match the first card drawn originally (rank 6, 5, 4)
        next_drawn = self.engine.draw_stock_cards()
        self.assertEqual(next_drawn, 3)
        self.assertEqual(self.engine.waste[-1].rank, 4)

    # --- ISSUE-005: Unbiased deck generation ---
    def test_deck_generation_unbiased(self):
        """Verifies generate_52_deck creates exactly 52 distinct cards covering all ranks and suits."""
        deck = SolitaireEngine.generate_52_deck()
        self.assertEqual(len(deck), 52)

        # Check all unique (rank, suit) combinations
        unique_cards = {(c.rank, c.suit) for c in deck}
        self.assertEqual(len(unique_cards), 52, "Deck must contain 52 distinct rank/suit cards")

        # Check suit and rank counts
        for s in range(1, 5):
            self.assertEqual(sum(1 for c in deck if c.suit == s), 13, f"Suit {s} must have 13 cards")
        for r in range(1, 14):
            self.assertEqual(sum(1 for c in deck if c.rank == r), 4, f"Rank {r} must have 4 cards")

    # --- ISSUE-007: random_strats flag ---
    def test_random_strats_flag(self):
        """Verifies random_strats defaults to False and can be toggled."""
        self.assertFalse(self.engine.random_strats)
        self.engine.random_strats = True
        self.assertTrue(self.engine.random_strats)

    # --- ISSUE-008: Benchmark CLI validation ---
    def test_benchmark_cli_validation(self):
        """Verifies benchmark.py fails with code 2 when --games <= 0."""
        benchmark_path = os.path.join(PARENT_DIR, 'benchmark.py')

        # Test --games 0
        p0 = subprocess.run([sys.executable, benchmark_path, '--games', '0'], capture_output=True, text=True)
        self.assertEqual(p0.returncode, 2)
        self.assertIn("--games must be a positive integer greater than 0", p0.stderr)

        # Test --games -1
        p_neg = subprocess.run([sys.executable, benchmark_path, '--games', '-1'], capture_output=True, text=True)
        self.assertEqual(p_neg.returncode, 2)
        self.assertIn("--games must be a positive integer greater than 0", p_neg.stderr)


if __name__ == '__main__':
    unittest.main()
