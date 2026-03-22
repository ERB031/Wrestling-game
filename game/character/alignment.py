"""Face/Heel alignment system."""

import random
from game.display import colored, Colors, bold, print_dramatic, print_crowd_reaction


def shift_alignment(wrestler, amount, reason=""):
    """Shift alignment and notify."""
    old = wrestler.alignment
    wrestler.alignment = max(-100, min(100, wrestler.alignment + amount))

    if abs(amount) >= 5:
        direction = "face" if amount > 0 else "heel"
        color = Colors.FACE if amount > 0 else Colors.HEEL
        if reason:
            print(f"  {colored(f'Alignment shift ({amount:+d}): {reason}', color)}")

    # Check for turn
    old_zone = get_alignment_zone(old)
    new_zone = get_alignment_zone(wrestler.alignment)
    if old_zone != new_zone:
        if (old_zone in ("face", "mega_face") and new_zone in ("heel", "mega_heel")):
            print_dramatic("THE CROWD IS IN SHOCK! YOU'VE TURNED HEEL!")
            print_crowd_reaction("gasp", 2)
            wrestler.popularity = min(100, wrestler.popularity + 15)
        elif (old_zone in ("heel", "mega_heel") and new_zone in ("face", "mega_face")):
            print_dramatic("THE CROWD ERUPTS! YOU'VE TURNED FACE!")
            print_crowd_reaction("pop", 3)
            wrestler.popularity = min(100, wrestler.popularity + 15)


def get_alignment_zone(alignment):
    """Get zone string from alignment value."""
    if alignment <= -60:
        return "mega_heel"
    elif alignment <= -20:
        return "heel"
    elif alignment <= 20:
        return "tweener"
    elif alignment <= 60:
        return "face"
    return "mega_face"


def get_alignment_name(alignment):
    """Get display name for alignment."""
    zone = get_alignment_zone(alignment)
    names = {
        "mega_heel": "Mega Heel",
        "heel": "Heel",
        "tweener": "Tweener",
        "face": "Face",
        "mega_face": "Mega Face",
    }
    return names.get(zone, "Unknown")


def check_alignment_divergence(wrestler):
    """Check if booked alignment diverges from natural. Returns event or None."""
    diff = abs(wrestler.alignment - wrestler.booked_alignment)
    if diff > 40:
        return {
            "type": "alignment_conflict",
            "text": (
                "The booker pulls you aside. 'Look, we've got you booked as a "
                f"{'face' if wrestler.booked_alignment > 0 else 'heel'}, but the crowd "
                f"{'loves' if wrestler.alignment > 20 else 'hates'} you. We need to address this.'"
            ),
            "choices": [
                {
                    "text": "Lean into what the crowd wants",
                    "effect": lambda w: setattr(w, 'booked_alignment', w.alignment),
                },
                {
                    "text": "Double down on your current character",
                    "effect": lambda w: None,  # Keep divergence
                },
                {
                    "text": "Go off-script and do what you want",
                    "effect": lambda w: _go_off_script(w),
                },
            ],
        }
    return None


def _go_off_script(wrestler):
    """Go off-script - risky but potentially legendary."""
    wrestler.backstage_rep -= 15
    if random.random() < 0.4:
        wrestler.popularity += 20
        wrestler.popularity = min(100, wrestler.popularity)
    else:
        wrestler.popularity -= 10
        wrestler.popularity = max(0, wrestler.popularity)


def get_crowd_reaction(wrestler):
    """Get crowd reaction based on alignment and popularity."""
    zone = get_alignment_zone(wrestler.alignment)
    pop = wrestler.popularity

    if zone in ("face", "mega_face"):
        if pop >= 70:
            return "pop", 3
        elif pop >= 40:
            return "pop", 2
        return "pop", 1
    elif zone in ("heel", "mega_heel"):
        if pop >= 70:
            return "heat", 3
        elif pop >= 40:
            return "heat", 2
        return "heat", 1
    else:  # tweener
        if pop >= 60:
            return "chant", 2
        return "chant", 1


def process_turn(wrestler, direction):
    """Process a full face/heel turn."""
    if direction == "heel":
        wrestler.alignment = max(-100, min(-30, wrestler.alignment - 40))
        wrestler.booked_alignment = wrestler.alignment
        print_dramatic("HEEL TURN!")
        print_crowd_reaction("heat", 3)
    elif direction == "face":
        wrestler.alignment = min(100, max(30, wrestler.alignment + 40))
        wrestler.booked_alignment = wrestler.alignment
        print_dramatic("FACE TURN!")
        print_crowd_reaction("pop", 3)

    wrestler.popularity = min(100, wrestler.popularity + 10)
