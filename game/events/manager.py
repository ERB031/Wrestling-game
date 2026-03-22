"""Weekly random event processing."""

import random
from game.display import (
    print_subheader, print_menu, colored, Colors, bold, dim, press_enter,
)
from data.constants import RANDOM_EVENT_CHANCE, MAX_RANDOM_EVENTS_PER_WEEK


# -----------------------------------------------------------------------
# Event pool
# -----------------------------------------------------------------------

EVENTS = [
    {
        "id": "booker_meeting",
        "name": "The Booker Wants to See You",
        "weight": 15,
        "min_weeks": 8,
        "cooldown": 8,
        "handler": "_handle_booker_meeting",
    },
    {
        "id": "bar_fight",
        "name": "Bar Incident",
        "weight": 8,
        "condition": lambda p, s: p.alcohol_level > 30,
        "cooldown": 12,
        "handler": "_handle_bar_fight",
    },
    {
        "id": "drug_test",
        "name": "Drug Test",
        "weight": 10,
        "condition": lambda p, s: _promotion_tests(p, s),
        "cooldown": 16,
        "handler": "_handle_drug_test",
    },
    {
        "id": "fan_encounter",
        "name": "Fan Encounter",
        "weight": 12,
        "cooldown": 6,
        "handler": "_handle_fan_encounter",
    },
    {
        "id": "training_opportunity",
        "name": "Training Opportunity",
        "weight": 8,
        "cooldown": 12,
        "handler": "_handle_training_opportunity",
    },
    {
        "id": "locker_room_conflict",
        "name": "Locker Room Conflict",
        "weight": 10,
        "cooldown": 8,
        "handler": "_handle_locker_room_conflict",
    },
    {
        "id": "injury_flareup",
        "name": "Injury Flare-Up",
        "weight": 8,
        "condition": lambda p, s: any(i.chronic for i in p.injuries) or any(d > 50 for d in p.body_damage.values()),
        "cooldown": 6,
        "handler": "_handle_injury_flareup",
    },
    {
        "id": "tabloid_story",
        "name": "Tabloid Story",
        "weight": 5,
        "condition": lambda p, s: p.popularity >= 30 and (p.alcohol_level > 40 or p.drug_level > 30 or p.steroid_use),
        "cooldown": 16,
        "handler": "_handle_tabloid_story",
    },
    {
        "id": "contract_offer",
        "name": "Contract Offer",
        "weight": 6,
        "condition": lambda p, s: s.total_weeks > 20 and p.popularity >= 15,
        "cooldown": 12,
        "handler": "_handle_contract_offer",
    },
    {
        "id": "death_of_friend",
        "name": "A Dark Day",
        "weight": 2,
        "condition": lambda p, s: s.total_weeks > 52,
        "cooldown": 52,
        "handler": "_handle_death_of_friend",
    },
]


def _promotion_tests(player, state):
    from game.world.promotions import PROMOTIONS
    promo = PROMOTIONS.get(player.current_promotion)
    return promo and getattr(promo, 'drug_testing', False)


# -----------------------------------------------------------------------
# Main entry point
# -----------------------------------------------------------------------

def process_weekly_events(state):
    """Roll for and process weekly random events."""
    player = state.player

    if random.random() > RANDOM_EVENT_CHANCE:
        return

    # Build eligible events
    eligible = []
    for event in EVENTS:
        eid = event["id"]
        if eid in state.event_cooldowns:
            continue
        min_w = event.get("min_weeks", 0)
        if state.total_weeks < min_w:
            continue
        cond = event.get("condition")
        if cond and not cond(player, state):
            continue
        eligible.append(event)

    if not eligible:
        return

    # Weighted random pick
    weights = [e["weight"] for e in eligible]
    chosen = random.choices(eligible, weights=weights, k=1)[0]

    # Set cooldown
    state.event_cooldowns[chosen["id"]] = chosen.get("cooldown", 4)

    # Dispatch
    handler_name = chosen["handler"]
    handler = globals().get(handler_name)
    if handler:
        handler(state)


# -----------------------------------------------------------------------
# Event handlers
# -----------------------------------------------------------------------

def _handle_booker_meeting(state):
    player = state.player
    print_subheader("THE BOOKER WANTS TO SEE YOU")
    print("  You're called into the office before the show.")

    options = [
        ("Listen to the plan", "See what they have in store for you"),
        ("Pitch your own idea", "Try to take control of your direction"),
        ("Complain about your spot", "You deserve better and you know it"),
    ]
    choice = print_menu(options, "What do you do?")

    if choice == 0:
        _msg = "\"We're going to give you a push. Don't screw it up.\""
        print(f"\n  {dim(_msg)}")
        player.momentum = min(10, player.momentum + 2)
        player.backstage_rep += 5
    elif choice == 1:
        if player.get_effective_skill("charisma") > 50 and random.random() < 0.6:
            print(f"\n  {colored('The booker loves it! Creative freedom!', Colors.GREEN)}")
            player.momentum = min(10, player.momentum + 3)
            player.backstage_rep += 3
        else:
            _msg = "\"That's... not what we're looking for. Just do what we tell you.\""
            print(f"\n  {dim(_msg)}")
            player.backstage_rep -= 5
    elif choice == 2:
        if player.popularity > 60:
            _msg = "The booker sighs. \"Fine. We'll see what we can do.\""
            print(f"\n  {dim(_msg)}")
            player.momentum = min(10, player.momentum + 1)
            player.backstage_rep -= 3
        else:
            _msg = "\"Who the hell do you think you are? Get out of my office.\""
            print(f"\n  {colored(_msg, Colors.RED)}")
            player.backstage_rep -= 15
            player.momentum = max(-10, player.momentum - 2)


def _handle_bar_fight(state):
    player = state.player
    print_subheader("BAR INCIDENT")
    print("  You've had a few too many at the hotel bar.")
    print("  Some local recognizes you and starts talking shit.")

    options = [
        ("Walk away", "Not worth the trouble"),
        ("Talk your way out", "Use that mic work"),
        ("Throw hands", "They asked for it"),
    ]
    choice = print_menu(options, "What do you do?")

    if choice == 0:
        print(f"\n  {dim('You walk away. Smart move.')}")
        player.backstage_rep += 3
    elif choice == 1:
        if player.get_effective_skill("mic_work") > 40:
            print(f"\n  You talk them down with a few well-chosen words. Crisis averted.")
            player.backstage_rep += 2
        else:
            print(f"\n  Your slurred words don't help. Security gets called.")
            player.backstage_rep -= 5
    elif choice == 2:
        print(f"\n  {colored('You crack them across the jaw.', Colors.BLOOD)}")
        if random.random() < 0.4:
            print(f"  {colored('The police are called. This makes the news.', Colors.WARNING)}")
            player.backstage_rep -= 20
            player.popularity += random.randint(-5, 5)
            state.log_career_event("Arrested after bar fight")
        else:
            print(f"  Bouncers break it up. No cops. This time.")
            player.backstage_rep -= 8
            player.alignment -= 5


def _handle_drug_test(state):
    player = state.player
    print_subheader("DRUG TEST")
    print("  Surprise wellness test. Everyone has to provide a sample.")

    using = player.steroid_use or player.drug_level > 30

    if not using:
        print(f"\n  {colored('You pass with flying colors. Clean as a whistle.', Colors.GREEN)}")
        return

    options = [
        ("Take the test honestly", "Face the music if it comes back positive"),
        ("Try to cheat", "Risky, but it might work"),
        ("Confess to management", "Come clean before the results hit"),
    ]
    choice = print_menu(options, "What do you do?")

    if choice == 0:
        if random.random() < 0.7:  # 70% chance of getting caught
            print(f"\n  {colored('FAILED. You tested positive.', Colors.RED)}")
            _apply_wellness_violation(state)
        else:
            print(f"\n  {colored('By some miracle, you passed.', Colors.GREEN)}")
    elif choice == 1:
        if random.random() < 0.5:
            print(f"\n  {colored('You managed to swap the sample. You got away with it.', Colors.WARNING)}")
        else:
            _msg = "They caught you cheating. That's even worse."
            print(f"\n  {colored(_msg, Colors.RED)}")
            _apply_wellness_violation(state, double=True)
    elif choice == 2:
        print(f"\n  You come clean to management.")
        print(f"  They appreciate the honesty, but there are still consequences.")
        player.backstage_rep += 10
        # Lighter punishment
        player.momentum = max(-10, player.momentum - 3)
        state.log_career_event("Confessed to substance use during drug test")


def _apply_wellness_violation(state, double=False):
    player = state.player
    penalty = -15 if not double else -30
    player.backstage_rep += penalty
    player.momentum = max(-10, player.momentum - 5)
    print(f"  Backstage reputation hit: {penalty}")
    if double:
        _msg = "Suspension incoming. You're off TV for 4 weeks."
        print(f"  {colored(_msg, Colors.RED)}")
        # Add a minor injury to simulate suspension
        from game.character.wrestler import Injury
        player.injuries.append(Injury(
            body_part="head", severity=1,
            description="Wellness Suspension", weeks_remaining=4,
        ))
    state.log_career_event("Failed wellness test" + (" (caught cheating)" if double else ""))


def _handle_fan_encounter(state):
    player = state.player
    print_subheader("FAN ENCOUNTER")

    scenario = random.choice(["kid", "aggressive", "wholesome"])

    if scenario == "kid":
        print("  A kid in a hospital wants to meet you. The promotion arranged a visit.")
        options = [
            ("Go and make their day", "Be a hero"),
            ("Too busy", "You've got things to do"),
        ]
        choice = print_menu(options, "What do you do?")
        if choice == 0:
            print(f"\n  The kid's face lights up. This is why you do this.")
            player.alignment += 10
            player.popularity += 3
            player.backstage_rep += 5
            player.burnout = max(0, player.burnout - 5)
        else:
            print(f"\n  {dim('You blow it off. Nobody finds out, but you know.')}")
            player.backstage_rep -= 3
    elif scenario == "aggressive":
        print("  An aggressive fan grabs you at an airport.")
        print("  They're in your face, camera phone recording.")
        options = [
            ("Stay calm and walk away", "Don't feed the trolls"),
            ("Cut a promo on them", "Stay in character"),
            ("Shove them", "Get out of your face"),
        ]
        choice = print_menu(options, "What do you do?")
        if choice == 0:
            print(f"\n  {dim('You walk away. Nothing happens.')}")
        elif choice == 1:
            if player.get_effective_skill("mic_work") > 40:
                print(f"\n  You cut a promo so devastating the crowd cheers. The video goes viral.")
                player.popularity += 5
            else:
                print(f"\n  The promo falls flat. The video still goes viral, but not in a good way.")
                player.popularity -= 2
        elif choice == 2:
            print(f"\n  {colored('The shove is caught on camera. Not a good look.', Colors.WARNING)}")
            player.backstage_rep -= 10
            player.popularity -= 3
    else:
        print("  A longtime fan approaches you after a show.")
        promo_upper = player.current_promotion.upper()
        print(f'  "I\'ve been watching you since {promo_upper}. You\'re my favorite."')
        print(f"\n  {dim('Sometimes this job is worth it.')}")
        player.burnout = max(0, player.burnout - 3)


def _handle_training_opportunity(state):
    player = state.player
    print_subheader("TRAINING OPPORTUNITY")
    print("  A legendary retired wrestler is running a special training seminar.")

    from data.constants import SKILLS, SKILL_DISPLAY_NAMES
    skill = random.choice(SKILLS)
    skill_name = SKILL_DISPLAY_NAMES[skill]

    print(f"  They're known for their {skill_name}.")

    options = [
        (f"Attend the seminar", f"Focus on improving {skill_name}"),
        ("Skip it", "You don't need anyone's help"),
    ]
    choice = print_menu(options, "What do you do?")

    if choice == 0:
        xp = random.randint(20, 40)
        leveled = player.add_skill_xp(skill, xp)
        print(f"\n  An incredible session. {skill_name} +{xp} XP!")
        if leveled:
            print(f"  {colored(f'{skill_name} leveled up to {player.skills[skill]}!', Colors.GREEN)}")
        player.backstage_rep += 3
    else:
        print(f"\n  {dim('You skip it. More time at the bar instead.')}")


def _handle_locker_room_conflict(state):
    player = state.player
    roster = state.get_current_roster()
    if not roster:
        return

    antagonist = random.choice(roster)
    print_subheader("LOCKER ROOM CONFLICT")
    print(f"  {antagonist.ring_name} has a problem with you.")

    reasons = [
        "They think you're too green to be in your spot.",
        "They heard you were talking shit about them.",
        "They want your match slot this week.",
        "They think you're too stiff in the ring.",
        "They're jealous of your push.",
    ]
    print(f"  {random.choice(reasons)}")

    options = [
        ("Talk it out", "Diplomacy is the smart play"),
        ("Stand your ground", "You're not backing down"),
        ("Go to management", "Let the office handle it"),
        ("Escalate", "Get in their face"),
    ]
    choice = print_menu(options, "What do you do?")

    if choice == 0:
        print(f"\n  You hash it out like professionals.")
        player.backstage_rep += 5
        player.relationships[antagonist.npc_id] = player.relationships.get(antagonist.npc_id, 0) + 10
    elif choice == 1:
        print(f"\n  You stand firm. {antagonist.ring_name} respects that. Barely.")
        player.backstage_rep += 2
    elif choice == 2:
        print(f"\n  Management mediates. The conflict is resolved, but you're seen as a snitch.")
        player.backstage_rep -= 5
        player.relationships[antagonist.npc_id] = player.relationships.get(antagonist.npc_id, 0) - 15
    elif choice == 3:
        print(f"\n  {colored('You get in their face. Things get heated.', Colors.WARNING)}")
        if player.get_effective_skill("violence") > antagonist.get_effective_skill("violence"):
            print(f"  {antagonist.ring_name} backs down. You win this round.")
            player.backstage_rep -= 3
            player.relationships[antagonist.npc_id] = player.relationships.get(antagonist.npc_id, 0) - 20
        else:
            print(f"  {antagonist.ring_name} doesn't back down. Security separates you both.")
            player.backstage_rep -= 10
            player.relationships[antagonist.npc_id] = player.relationships.get(antagonist.npc_id, 0) - 25


def _handle_injury_flareup(state):
    player = state.player
    print_subheader("INJURY FLARE-UP")

    # Find the worst body part
    worst_part = max(player.body_damage, key=player.body_damage.get)
    damage = player.body_damage[worst_part]

    print(f"  Your {worst_part.replace('_', ' ')} is acting up again.")
    print(f"  The old damage (severity: {damage:.0f}/100) is making itself known.")

    options = [
        ("Push through", "Pop some painkillers and keep going"),
        ("Take it easy", "Rest and let it heal"),
        ("See a doctor", "Get a professional opinion"),
    ]
    choice = print_menu(options, "What do you do?")

    if choice == 0:
        player.painkiller_level = min(100, player.painkiller_level + 10)
        player.health = max(30, player.health - 10)
        print(f"\n  You pop a few pills and power through. Painkiller dependency +10.")
    elif choice == 1:
        player.health = min(100, player.health + 15)
        player.body_damage[worst_part] = max(0, damage - 5)
        print(f"\n  Rest helps. Health restored. Damage slightly reduced.")
    elif choice == 2:
        player.money -= 500
        player.body_damage[worst_part] = max(0, damage - 10)
        print(f"\n  The doctor helps. -$500, but the damage is reduced.")
        if damage > 70:
            _msg = "\"Honestly, you should think about how much longer you can do this.\""
            print(f"  {colored(_msg, Colors.WARNING)}")


def _handle_tabloid_story(state):
    player = state.player
    print_subheader("TABLOID STORY")
    print(f"  A gossip site has published a story about you.")

    topics = []
    if player.alcohol_level > 40:
        topics.append("drinking")
    if player.drug_level > 30:
        topics.append("drug use")
    if player.steroid_use:
        topics.append("steroid use")
    if player.relationship_status != "single":
        topics.append("relationship drama")

    topic = random.choice(topics) if topics else "wild behavior"
    print(f"  The story is about your alleged {topic}.")

    options = [
        ("Ignore it", "Don't give it oxygen"),
        ("Deny everything", "Publicly deny the story"),
        ("Own it", "Lean into it"),
    ]
    choice = print_menu(options, "What do you do?")

    if choice == 0:
        print(f"\n  {dim('The story fades in a few days.')}")
        player.popularity -= 1
    elif choice == 1:
        if random.random() < 0.5:
            print(f"\n  Nobody believes you, but at least you said something.")
            player.popularity -= 3
        else:
            print(f"\n  Your denial is convincing enough. Story dies.")
    elif choice == 2:
        print(f"\n  You lean into the controversy. Surprisingly, it works.")
        player.popularity += random.randint(2, 8)
        player.alignment -= 10
        player.backstage_rep -= 5


def _handle_contract_offer(state):
    player = state.player
    print_subheader("CONTRACT OFFER")

    from game.world.promotions import get_available_promotions
    available = get_available_promotions(player)
    # Filter to promotions player is NOT currently in
    available = [p for p in available if p.id != player.current_promotion]

    if not available:
        print("  You hear rumors of interest, but nothing materializes.")
        return

    promo = random.choice(available)
    print(f"  {colored(promo.name, Colors.CYAN)} has reached out!")
    print(f"  They're interested in bringing you in.")
    print(f"  Tier: {promo.tier} | Pay: ${promo.pay_min}-${promo.pay_max}/show")

    options = [
        ("Express interest", "Start a conversation"),
        ("Not interested", "You're happy where you are"),
    ]
    choice = print_menu(options, "What do you do?")

    if choice == 0:
        print(f"\n  You tell them you're interested. They'll be in touch.")
        state.log_career_event(f"Received contract interest from {promo.name}")
    else:
        print(f"\n  {dim('You pass on the opportunity. For now.')}")


def _handle_death_of_friend(state):
    player = state.player
    print_subheader("A DARK DAY")

    roster = state.get_current_roster()
    if roster:
        # Pick a random NPC from any promotion
        npc = random.choice(roster)
        name = npc.ring_name
    else:
        name = "an old friend from the business"

    causes = [
        "heart attack", "drug overdose", "car accident",
        "complications from years of in-ring injuries",
    ]
    cause = random.choice(causes)

    print(f"  {colored(f'You get the call. {name} is dead.', Colors.RED)}")
    print(f"  Cause: {cause}.")
    print(f"\n  {dim('The business takes another one.')}")
    print()

    options = [
        ("Grieve privately", "Process this on your own"),
        ("Dedicate your next match", "Wrestle in their memory"),
        ("Hit the bottle", "Numb the pain"),
    ]
    choice = print_menu(options, "How do you cope?")

    if choice == 0:
        player.burnout += 10
        print(f"\n  {dim('You sit alone in the hotel room. The walls feel closer.')}")
    elif choice == 1:
        player.momentum = min(10, player.momentum + 2)
        player.burnout += 5
        print(f"\n  You'll wrestle your heart out next time. For them.")
    elif choice == 2:
        player.alcohol_level = min(100, player.alcohol_level + 20)
        player.burnout += 5
        _msg = "The whiskey doesn't help. But you keep pouring."
        print(f"\n  {dim(_msg)}")

    state.log_career_event(f"Mourned the death of {name}")
