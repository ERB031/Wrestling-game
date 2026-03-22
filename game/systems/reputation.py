"""Backstage reputation and push level calculation."""

import random


def calculate_push_level(player):
    """Calculate the player's current push level (momentum, -10 to +10).

    Based on: recent match quality, popularity, backstage rep, and randomness.
    """
    # Start from current momentum
    momentum = player.momentum

    # Popularity pull - high popularity trends toward positive push
    if player.popularity >= 70:
        momentum = min(10, momentum + 1)
    elif player.popularity >= 50:
        pass  # Neutral
    elif player.popularity < 20:
        momentum = max(-10, momentum - 1)

    # Backstage rep matters
    if player.backstage_rep > 30:
        momentum = min(10, momentum + 1)
    elif player.backstage_rep < -30:
        momentum = max(-10, momentum - 1)

    # Random booking whims
    momentum += random.randint(-1, 1)

    return max(-10, min(10, momentum))
