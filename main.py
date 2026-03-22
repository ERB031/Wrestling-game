#!/usr/bin/env python3
"""Wrestling Career Simulator - Main Entry Point."""

import sys
import os

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from game.display import (
    clear_screen, print_header, print_menu, colored, Colors, bold, dim,
    press_enter, print_divider,
)
from game.save import present_load_menu, list_saves
from game.engine import new_game, game_loop


def title_screen():
    """Display the title screen."""
    clear_screen()
    print()
    print(colored(r"""
    ╔═══════════════════════════════════════════════════════╗
    ║                                                       ║
    ║   ██╗    ██╗██████╗ ███████╗███████╗████████╗██╗      ║
    ║   ██║    ██║██╔══██╗██╔════╝██╔════╝╚══██╔══╝██║      ║
    ║   ██║ █╗ ██║██████╔╝█████╗  ███████╗   ██║   ██║      ║
    ║   ██║███╗██║██╔══██╗██╔══╝  ╚════██║   ██║   ██║      ║
    ║   ╚███╔███╔╝██║  ██║███████╗███████║   ██║   ███████╗  ║
    ║    ╚══╝╚══╝ ╚═╝  ╚═╝╚══════╝╚══════╝   ╚═╝   ╚══════╝  ║
    ║                                                       ║
    ║          C A R E E R   S I M U L A T O R              ║
    ║                                                       ║
    ║    From backyard rings to WrestleMania main events.   ║
    ║    Every choice matters. Every scar tells a story.    ║
    ║                                                       ║
    ╚═══════════════════════════════════════════════════════╝
    """, Colors.GOLD))
    print()
    print(dim("    A text-based wrestling career simulation"))
    print(dim("    Content Warning: Violence, drug use, adult themes"))
    print()


def main_menu():
    """Show the main menu and handle selection."""
    options = [
        ("New Career", "Create a new wrestler and start from scratch"),
        ("Continue", "Load a saved career"),
        ("Quit", "Exit the game"),
    ]

    choice = print_menu(options, "Select")
    return choice


def run():
    """Main game entry point."""
    while True:
        title_screen()
        choice = main_menu()

        if choice == 0:  # New game
            state = new_game()
            game_loop(state)
        elif choice == 1:  # Load
            state = present_load_menu()
            if state:
                game_loop(state)
            else:
                print("\n  No save loaded.")
                press_enter()
        elif choice == 2:  # Quit
            clear_screen()
            print()
            print(colored("  Thanks for playing. See you in the ring.", Colors.GOLD))
            print()
            sys.exit(0)


if __name__ == "__main__":
    try:
        run()
    except KeyboardInterrupt:
        print("\n\n  Game interrupted. Progress not saved.")
        sys.exit(0)
