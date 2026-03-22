"""Age-related effects and retirement logic."""

import random
from game.display import (
    print_subheader, print_menu, colored, Colors, bold, dim, press_enter,
    confirm,
)
from game.character.skills import apply_age_decline


def process_aging(player):
    """Apply yearly aging effects."""
    # Physical decline
    apply_age_decline(player)

    # Mental stats can still grow
    if player.age > 35:
        # Psychology and mic work can improve with experience
        player.add_skill_xp("psychology", random.randint(5, 15))
        player.add_skill_xp("mic_work", random.randint(3, 10))

    # Health ceiling drops with age
    if player.age > 38:
        max_health = 100 - (player.age - 38) * 3
        player.health = min(player.health, max(40, max_health))

    # Injury recovery slows
    if player.age > 35:
        for injury in player.injuries:
            if injury.weeks_remaining > 0:
                # Add extra recovery time
                extra = random.randint(0, (player.age - 35) // 3)
                injury.weeks_remaining += extra


def check_retirement_prompt(state):
    """Check if the player should be prompted about retirement."""
    player = state.player

    should_prompt = False
    reason = ""

    if player.age >= 45:
        should_prompt = True
        reason = "You're 45. The body doesn't lie."
    elif player.age >= 40 and player.health < 50:
        should_prompt = True
        reason = "You're 40 and your body is breaking down."
    elif player.age >= 38:
        # Only prompt sometimes
        if random.random() < 0.2:
            should_prompt = True
            reason = "A quiet voice in the back of your head asks: how much longer?"

    if not should_prompt:
        return

    print()
    print(f"  {dim(reason)}")
    print()

    options = [
        ("Keep going", "You're not done yet"),
        ("Start thinking about retirement", "Maybe one more year"),
        ("Retire now", "Go out on your terms"),
    ]
    choice = print_menu(options, "What do you do?")

    if choice == 0:
        print(f"\n  {dim('Not yet. Not yet.')}")
    elif choice == 1:
        print(f"\n  {dim('The end is coming. But not today.')}")
        state.log_career_event("Began considering retirement")
    elif choice == 2:
        if confirm("Are you sure you want to retire?"):
            player.is_retired = True
            state.game_over = True
            state.game_over_reason = "retirement"
            state.log_career_event(f"Retired from professional wrestling at age {player.age}")
