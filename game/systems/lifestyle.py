"""Lifestyle and substance abuse system.

Tracks alcohol, drugs, painkillers, steroids, relationships, and burnout.
"""

import random
from game.display import (
    print_subheader, print_menu, colored, Colors, bold, dim, press_enter,
)
from data.constants import (
    ADDICTION_CASUAL, ADDICTION_CRAVING, ADDICTION_PROBLEM,
    ADDICTION_SEVERE, ADDICTION_CRITICAL,
    STEROID_LIGHT_BOOST, STEROID_HEAVY_BOOST,
)


def present_lifestyle_choices(player, context="night_out"):
    """Present lifestyle choices during off-day or event."""
    print_subheader("NIGHT OUT")
    print("  You hit the town after the show. What's the plan?")

    options = [
        ("Have a few drinks", "Social drinking. Networking. The usual."),
        ("Hit it hard", "Shots, clubs, the full deal. You earned it."),
        ("Stay sober", "Mineral water and early to bed."),
    ]

    if player.painkiller_level > 0 or any(i.weeks_remaining > 0 for i in player.injuries):
        options.append(("Pop some pills", "The pain doesn't stop just because the show is over."))

    if player.steroid_use or player.steroid_cumulative > 0:
        options.append(("Steroid cycle", "Time for your next injection."))
    elif player.get_effective_skill("power") < 50 or player.get_effective_skill("look") < 40:
        options.append(("Start using steroids", "Everyone else is doing it. Maybe it's time."))

    choice = print_menu(options, "What do you do?")

    if choice == 0:  # Social drinking
        player.alcohol_level = min(100, player.alcohol_level + 5)
        player.burnout = max(0, player.burnout - 3)
        print(f"\n  A few beers with the boys. Good for morale.")
        if player.alcohol_level > ADDICTION_CASUAL:
            _msg = "You're developing a taste for this."
            print(f"  {dim(_msg)}")

    elif choice == 1:  # Heavy drinking
        player.alcohol_level = min(100, player.alcohol_level + 15)
        player.drug_level = min(100, player.drug_level + random.randint(0, 10))
        player.burnout = max(0, player.burnout - 8)
        player.health = max(50, player.health - 5)
        print(f"\n  You go hard. Shots, dancing, the whole deal.")

        if random.random() < 0.15:
            print(f"  {colored('You black out. What happened last night?', Colors.WARNING)}")
            if random.random() < 0.3:
                _msg = "Something happened. You're not sure what. People are looking at you weird."
                print(f"  {colored(_msg, Colors.RED)}")
                player.backstage_rep -= 5
        if player.alcohol_level > ADDICTION_PROBLEM:
            _msg = "You can't remember the last night you didn't drink."
            print(f"  {colored(_msg, Colors.WARNING)}")

    elif choice == 2:  # Stay sober
        player.burnout = max(0, player.burnout - 2)
        player.health = min(100, player.health + 3)
        print(f"\n  {dim('A quiet night. Your body thanks you.')}")
        # Slight alcohol/drug decay
        player.alcohol_level = max(0, player.alcohol_level - 3)
        player.drug_level = max(0, player.drug_level - 2)

    elif choice == 3:  # Pills or steroids (depends on what option 3 was)
        option_text = options[3][0]
        if "pills" in option_text.lower():
            _take_painkillers(player)
        else:
            _use_steroids(player)

    elif choice == 4:  # Steroids (if both pills and steroids available)
        _use_steroids(player)


def _take_painkillers(player):
    """Handle painkiller use."""
    player.painkiller_level = min(100, player.painkiller_level + 10)
    player.health = min(100, player.health + 5)  # Temporary relief
    print(f"\n  The pills take the edge off. Health +5. Dependency +10.")

    if player.painkiller_level > ADDICTION_CRAVING:
        print(f"  {colored('You need them now. Not just for the pain.', Colors.WARNING)}")
    if player.painkiller_level > ADDICTION_SEVERE:
        _msg = "You're taking more than prescribed. Much more."
        print(f"  {colored(_msg, Colors.RED)}")
        if random.random() < 0.1:
            print(f"  {colored('You nod off at dinner. Someone notices.', Colors.RED)}")
            player.backstage_rep -= 5


def _use_steroids(player):
    """Handle steroid use."""
    if not player.steroid_use:
        print(f"\n  You start a steroid cycle. The needle goes in.")
        print(f"  {dim('Everyone else looks bigger. You need to keep up.')}")
        player.steroid_use = True
        player.steroid_cumulative = 0

    player.steroid_cumulative += 1
    print(f"\n  Week {player.steroid_cumulative} on the cycle.")

    # Benefits
    for skill, boost in STEROID_LIGHT_BOOST.items():
        if skill in player.skills:
            # Temporary boost is handled by get_effective_skill
            pass

    print(f"  {colored('Power, Look, and Athleticism temporarily boosted.', Colors.GREEN)}")

    # Risks
    if player.steroid_cumulative > 26:  # 6+ months
        if random.random() < 0.1:
            print(f"  {colored('Your heart is racing. Chest pains. You ignore them.', Colors.WARNING)}")
            player.health = max(50, player.health - 10)
            player.body_damage["ribs"] = min(100, player.body_damage.get("ribs", 0) + 5)
    if player.steroid_cumulative > 52:  # 1+ year
        if random.random() < 0.15:
            print(f"  {colored('Mood swings. Rage. Your relationship is suffering.', Colors.WARNING)}")
            if player.relationship_status != "single":
                player.relationship_health = max(0, player.relationship_health - 15)


def tick_addictions(player):
    """Process weekly addiction decay and consequences."""
    # Natural decay (slow)
    if player.alcohol_level > 0:
        decay = 2 if player.alcohol_level < ADDICTION_PROBLEM else 1
        player.alcohol_level = max(0, player.alcohol_level - decay)

    if player.drug_level > 0:
        decay = 2 if player.drug_level < ADDICTION_PROBLEM else 1
        player.drug_level = max(0, player.drug_level - decay)

    if player.painkiller_level > 0:
        decay = 1  # Very slow decay
        player.painkiller_level = max(0, player.painkiller_level - decay)

    # Burnout from road life
    player.burnout = min(100, player.burnout + 1)

    # Withdrawal effects
    if player.alcohol_level > ADDICTION_SEVERE:
        player.health = max(30, player.health - 3)
    if player.painkiller_level > ADDICTION_SEVERE:
        player.health = max(30, player.health - 2)
    if player.drug_level > ADDICTION_SEVERE:
        player.health = max(20, player.health - 5)

    # Critical addiction consequences
    if player.alcohol_level >= ADDICTION_CRITICAL:
        if random.random() < 0.05:
            print(f"  {colored('Your drinking is out of control. People are worried.', Colors.RED)}")
            player.backstage_rep -= 5

    if player.drug_level >= ADDICTION_CRITICAL:
        if random.random() < 0.08:
            _msg = "You can't function without a fix. This is bad."
            print(f"  {colored(_msg, Colors.RED)}")
            player.backstage_rep -= 8

    if player.painkiller_level >= ADDICTION_CRITICAL:
        if random.random() < 0.06:
            _msg = "You're popping pills like candy. Nobody can reach you."
            print(f"  {colored(_msg, Colors.RED)}")

    # Steroid weekly effects
    if player.steroid_use:
        player.steroid_cumulative += 1
        # Long-term health risks
        if player.steroid_cumulative > 52 and random.random() < 0.02:
            player.health = max(40, player.health - 15)
            print(f"  {colored('Steroid side effects are catching up. Health -15.', Colors.WARNING)}")

    # Burnout effects
    if player.burnout > 80:
        if random.random() < 0.1:
            _msg = "You're burned out. Everything feels like a chore."
            print(f"  {colored(_msg, Colors.WARNING)}")

    # Relationship decay from road life
    if player.relationship_status != "single":
        player.relationship_health = max(0, player.relationship_health - 2)
        if player.relationship_health <= 0 and random.random() < 0.3:
            print(f"  {colored('Your relationship has ended. The road life won.', Colors.RED)}")
            player.relationship_status = "single"
            player.relationship_partner = ""
            player.burnout = min(100, player.burnout + 15)


def check_lifestyle_events(state):
    """Check for lifestyle-triggered events."""
    player = state.player

    # Death check from extreme substance abuse
    total_substance = player.alcohol_level + player.drug_level + player.painkiller_level
    if total_substance > 250 and player.health < 30:
        if random.random() < 0.02:
            print(f"\n  {colored('You collapsed in your hotel room.', Colors.RED)}")
            print(f"  {colored('They found you just in time. Rushed to the hospital.', Colors.RED)}")
            from game.character.wrestler import Injury
            player.injuries.append(Injury(
                body_part="ribs", severity=3,
                description="Hospitalization - Substance Abuse", weeks_remaining=8,
            ))
            player.health = 30
            state.log_career_event("Hospitalized for substance abuse")

    # Steroid heart attack risk (age + long-term use)
    if player.steroid_use and player.age > 40 and player.steroid_cumulative > 104:
        if random.random() < 0.01:
            print(f"\n  {colored('Heart attack. The steroids finally caught up.', Colors.RED)}")
            player.health = 10
            player.steroid_use = False
            from game.character.wrestler import Injury
            player.injuries.append(Injury(
                body_part="ribs", severity=4,
                description="Heart Attack", weeks_remaining=26,
                chronic=True,
            ))
            state.log_career_event("Suffered a heart attack")
