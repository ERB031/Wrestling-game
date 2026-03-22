"""Save/load system using JSON serialization."""

import json
import os

SAVE_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "saves")
MAX_SAVE_SLOTS = 3
AUTOSAVE_SLOT = 0  # Slot 0 is autosave


def ensure_save_dir():
    """Create save directory if it doesn't exist."""
    os.makedirs(SAVE_DIR, exist_ok=True)


def get_save_path(slot):
    """Get the file path for a save slot."""
    if slot == AUTOSAVE_SLOT:
        return os.path.join(SAVE_DIR, "autosave.json")
    return os.path.join(SAVE_DIR, f"save_{slot}.json")


def save_game(game_state, slot=None):
    """Save the game state to a slot."""
    from game.display import colored, Colors

    ensure_save_dir()

    if slot is None:
        slot = game_state.save_slot

    game_state.save_slot = slot
    save_path = get_save_path(slot)

    try:
        data = game_state.to_dict()
        with open(save_path, 'w') as f:
            json.dump(data, f, indent=2, default=str)

        slot_name = "Autosave" if slot == AUTOSAVE_SLOT else f"Slot {slot}"
        print(f"\n  {colored(f'Game saved to {slot_name}.', Colors.GREEN)}")
        return True
    except Exception as e:
        print(f"\n  {colored(f'Save failed: {e}', Colors.RED)}")
        return False


def load_game(slot):
    """Load a game state from a slot."""
    from game.state import GameState

    save_path = get_save_path(slot)

    if not os.path.exists(save_path):
        return None

    try:
        with open(save_path, 'r') as f:
            data = json.load(f)
        return GameState.from_dict(data)
    except Exception as e:
        print(f"  Load failed: {e}")
        return None


def autosave(game_state):
    """Quick autosave."""
    save_game(game_state, AUTOSAVE_SLOT)


def list_saves():
    """List all available save files with summary info."""
    from game.display import colored, Colors, bold, dim

    ensure_save_dir()
    saves = []

    for slot in range(AUTOSAVE_SLOT, MAX_SAVE_SLOTS + 1):
        save_path = get_save_path(slot)
        if os.path.exists(save_path):
            try:
                with open(save_path, 'r') as f:
                    data = json.load(f)

                player = data.get("player", {})
                slot_name = "Autosave" if slot == AUTOSAVE_SLOT else f"Slot {slot}"
                ring_name = player.get("ring_name", "Unknown")
                year = data.get("current_year", 1)
                week = data.get("current_week", 1)
                promo = player.get("current_promotion", "Unknown")

                saves.append({
                    "slot": slot,
                    "name": slot_name,
                    "ring_name": ring_name,
                    "year": year,
                    "week": week,
                    "promotion": promo,
                    "exists": True,
                })
            except Exception:
                saves.append({"slot": slot, "exists": False})
        else:
            saves.append({"slot": slot, "exists": False})

    return saves


def delete_save(slot):
    """Delete a save file."""
    save_path = get_save_path(slot)
    if os.path.exists(save_path):
        os.remove(save_path)
        return True
    return False


def present_save_menu(game_state):
    """Show save menu and handle save."""
    from game.display import print_menu, print_subheader, colored, Colors, bold, dim

    print_subheader("SAVE GAME")
    saves = list_saves()

    options = []
    for save in saves:
        if save["slot"] == AUTOSAVE_SLOT:
            continue  # Don't manually save to autosave
        if save.get("exists"):
            label = f"Slot {save['slot']}: {save['ring_name']} - Year {save['year']}, Week {save['week']} ({save['promotion'].upper()})"
            options.append((label, "Will overwrite existing save"))
        else:
            options.append((f"Slot {save['slot']}: Empty", "New save"))

    options.append(("Cancel", "Return to game"))

    choice = print_menu(options, "Choose save slot")
    if choice < len(options) - 1:
        slot = choice + 1  # Slots 1-3
        save_game(game_state, slot)
    return


def present_load_menu():
    """Show load menu and return loaded state or None."""
    from game.display import print_menu, print_subheader, colored, Colors, bold, dim

    print_subheader("LOAD GAME")
    saves = list_saves()

    available = [s for s in saves if s.get("exists")]
    if not available:
        print("  No saved games found.")
        return None

    options = []
    slot_map = []
    for save in available:
        slot_name = save["name"]
        label = f"{slot_name}: {save['ring_name']} - Year {save['year']}, Week {save['week']} ({save['promotion'].upper()})"
        options.append(label)
        slot_map.append(save["slot"])

    options.append("Cancel")

    choice = print_menu(options, "Choose save to load")
    if choice < len(slot_map):
        return load_game(slot_map[choice])
    return None
