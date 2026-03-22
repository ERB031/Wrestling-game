"""Main game loop and turn management."""

import random
from game.state import GameState
from game.display import (
    clear_screen, print_header, print_subheader, print_menu, print_stats,
    print_week_header, print_divider, print_game_over, press_enter,
    colored, Colors, bold, dim, get_input, confirm, print_dramatic,
)
from game.character.creation import create_character
from game.save import save_game, autosave, present_save_menu, present_load_menu


def new_game():
    """Start a new game."""
    state = GameState()
    state.player = create_character()
    initialize_world(state)
    return state


def initialize_world(state):
    """Set up the game world - rosters, titles, calendar."""
    from game.world.npcs import generate_roster
    from game.world.promotions import PROMOTIONS
    from game.world.titles import TitleManager
    from game.world.calendar import Calendar

    # Generate rosters for all promotions
    for promo_id, promo in PROMOTIONS.items():
        if promo_id == "retirement":
            continue
        roster = generate_roster(promo)
        state.promotion_rosters[promo_id] = roster
        for npc in roster:
            state.register_npc(npc)

    # Initialize titles
    state.title_manager = TitleManager()
    state.title_manager.initialize_titles(PROMOTIONS, state.promotion_rosters)

    # Setup calendar
    state.calendar = Calendar()
    state.calendar.schedule_month([state.player.current_promotion])

    # Set initial contract
    promo_id = state.player.current_promotion
    promo = PROMOTIONS.get(promo_id)
    state.contract = {
        "promotion_id": promo_id,
        "weeks_remaining": 52,
        "pay_per_show": promo.pay_min if promo else 0,
        "exclusive": promo.tier >= 3 if promo else False,
    }

    promo_name = promo.name if promo else promo_id
    state.log_career_event(f"Signed first contract with {promo_name}")


def game_loop(state):
    """Main game loop - runs weekly turns until game over."""
    while not state.game_over:
        run_week(state)

    # Game over
    clear_screen()
    summary = state.get_career_summary()
    print_game_over(state.player, summary)
    press_enter()


def run_week(state):
    """Process a single game week."""
    from game.events.manager import process_weekly_events
    from game.systems.lifestyle import tick_addictions, check_lifestyle_events
    from game.systems.injury import process_injury_recovery

    player = state.player

    # Display weekly header
    clear_screen()
    from game.world.promotions import PROMOTIONS
    promo = PROMOTIONS.get(player.current_promotion)
    promo_name = promo.name if promo else player.current_promotion
    print_week_header(state.current_week, state.current_year, promo_name, player)

    # Check for injuries preventing action
    if player.is_injured():
        active = [i for i in player.injuries if i.weeks_remaining > 0 and i.severity >= 3]
        if active:
            print(f"\n  {colored('You are currently injured and cannot wrestle.', Colors.INJURY)}")
            for inj in active:
                print(f"    - {inj.description}: {inj.weeks_remaining} weeks remaining")

    # Process storyline beats
    if state.active_storyline:
        from game.events.storylines import advance_storyline
        advance_storyline(state)

    # Random events
    process_weekly_events(state)

    # Check for lifestyle events
    check_lifestyle_events(state)

    # Show phase - match if booked
    ppv = _is_ppv_week(state)
    if player.can_wrestle():
        show_phase(state, is_ppv=ppv)
    else:
        print(f"\n  {dim('No match this week - recovering from injury.')}")

    # Off-day phase
    off_day_phase(state)

    # Weekly maintenance
    player.heal_week()
    tick_addictions(player)
    process_injury_recovery(player)

    # Decrement event cooldowns
    for event_id in list(state.event_cooldowns.keys()):
        state.event_cooldowns[event_id] -= 1
        if state.event_cooldowns[event_id] <= 0:
            del state.event_cooldowns[event_id]

    # Contract countdown
    if state.contract:
        state.contract["weeks_remaining"] -= 1
        if state.contract["weeks_remaining"] <= 0:
            _handle_contract_expiry(state)

    # Monthly checks (every 4 weeks)
    if state.current_week % 4 == 0:
        monthly_phase(state)

    # Yearly checks
    if state.current_week == 52:
        yearly_phase(state)

    # Advance calendar
    _advance_week(state)

    # Autosave at PPVs
    if ppv:
        autosave(state)

    # Check game over conditions
    check_game_over(state)

    # Weekly menu
    if not state.game_over:
        weekly_menu(state)


def show_phase(state, is_ppv=False):
    """Handle the show/match portion of the week."""
    from game.match.simulation import run_match
    from game.world.promotions import PROMOTIONS

    player = state.player
    roster = state.get_current_roster()

    if not roster:
        print(f"\n  {dim('No opponents available this week.')}")
        return

    # Determine opponent
    opponent = pick_opponent(state, roster, is_ppv)
    if not opponent:
        return

    promo = PROMOTIONS.get(player.current_promotion)

    # Determine match type
    from game.match.simulation import get_available_match_types
    violence_tolerance = promo.violence_tolerance if promo else 5
    available_types = get_available_match_types(
        violence_tolerance,
        player.get_effective_skill("violence"),
    )

    if is_ppv:
        print(f"\n  {colored('★ PAY-PER-VIEW EVENT ★', Colors.GOLD)}")
        # PPVs can have special match types
        if state.active_storyline and state.active_storyline.get("blow_off_week") == state.total_weeks:
            match_type_id = state.active_storyline.get("blow_off_match_type", "standard_singles")
        else:
            match_type_id = choose_match_type(available_types)
    else:
        # Regular show - usually standard unless storyline dictates
        if random.random() < 0.3:
            match_type_id = choose_match_type(available_types)
        else:
            match_type_id = "standard_singles"

    # Determine if player is booked to win
    booked_to_win = determine_booking(state, opponent)

    # Run the match
    print_subheader(f"{'PPV MAIN EVENT' if is_ppv else 'MATCH'}: {player.ring_name} vs. {opponent.ring_name}")
    result = run_match(player, opponent, match_type_id, booked_to_win, state)

    # Apply results
    apply_match_results(state, result, opponent, is_ppv)


def pick_opponent(state, roster, is_ppv):
    """Pick an opponent from the roster."""
    # If in a storyline, face the feud partner
    if state.active_storyline and state.active_storyline.get("opponent_id"):
        opp = state.get_npc(state.active_storyline["opponent_id"])
        if opp:
            return opp

    # Filter to available opponents
    available = [w for w in roster if isinstance(w, object) and hasattr(w, 'can_wrestle') and w.can_wrestle()]
    if not available:
        return None

    if is_ppv:
        # PPV opponents tend to be higher ranked
        available.sort(key=lambda w: w.get_overall_rating(), reverse=True)
        return available[0] if available else None

    # Regular show - weighted random
    return random.choice(available)


def choose_match_type(available_types):
    """Let the player choose a match type (or pick automatically)."""
    from game.display import print_menu
    from game.match.match_types import MATCH_TYPES

    if len(available_types) <= 1:
        return available_types[0] if available_types else "standard_singles"

    # Show top 5 options
    options_to_show = available_types[:6]
    options = []
    for mt_id in options_to_show:
        mt = MATCH_TYPES.get(mt_id, {})
        options.append((mt.get("name", mt_id), mt.get("description", "")))

    choice = print_menu(options, "Match type")
    return options_to_show[choice]


def determine_booking(state, opponent):
    """Determine if the player is booked to win."""
    player = state.player
    momentum = player.momentum

    # Base win chance from momentum
    base_chance = 0.5 + (momentum * 0.05)

    # Popularity comparison
    if player.popularity > opponent.popularity + 20:
        base_chance += 0.15
    elif opponent.popularity > player.popularity + 20:
        base_chance -= 0.15

    # Backstage rep helps
    if player.backstage_rep > 30:
        base_chance += 0.1
    elif player.backstage_rep < -30:
        base_chance -= 0.1

    # Title holders usually retain
    if player.titles_held:
        base_chance += 0.2

    return random.random() < min(0.85, max(0.15, base_chance))


def apply_match_results(state, result, opponent, is_ppv):
    """Apply match results to game state."""
    player = state.player

    if result is None:
        return

    # Record
    if result.get("winner") == "player":
        player.wins += 1
        if isinstance(opponent, object) and hasattr(opponent, 'losses'):
            opponent.losses += 1
    elif result.get("winner") == "opponent":
        player.losses += 1
        if isinstance(opponent, object) and hasattr(opponent, 'wins'):
            opponent.wins += 1
    else:
        player.draws += 1

    player.total_matches += 1

    # Match rating
    rating = result.get("rating", 2.0)
    if rating > player.best_match_rating:
        player.best_match_rating = rating

    # Popularity
    pop_change = result.get("popularity_change", 0)
    if is_ppv:
        pop_change = int(pop_change * 1.5)
    player.popularity = max(0, min(100, player.popularity + pop_change))
    if player.popularity > player.peak_popularity:
        player.peak_popularity = player.popularity

    # Alignment
    alignment_change = result.get("alignment_change", 0)
    player.alignment = max(-100, min(100, player.alignment + alignment_change))

    # Money
    pay = state.contract.get("pay_per_show", 0)
    if is_ppv:
        pay = int(pay * 2)
    player.money += pay
    player.total_earnings += pay

    # Momentum
    if result.get("winner") == "player":
        player.momentum = min(10, player.momentum + 1)
    else:
        player.momentum = max(-10, player.momentum - 1)

    # Backstage rep
    rep_change = result.get("rep_change", 0)
    player.backstage_rep = max(-100, min(100, player.backstage_rep + rep_change))

    # Record match
    state.match_history.append({
        "week": state.total_weeks,
        "opponent": opponent.ring_name if hasattr(opponent, 'ring_name') else str(opponent),
        "match_type": result.get("match_type", "unknown"),
        "rating": rating,
        "winner": result.get("winner", "unknown"),
        "ppv": is_ppv,
    })

    # Log notable matches
    if rating >= 4.0:
        state.log_career_event(
            f"{'PPV ' if is_ppv else ''}{rating:.1f}-star classic vs. "
            f"{opponent.ring_name if hasattr(opponent, 'ring_name') else opponent}"
        )


def off_day_phase(state):
    """Handle off-day activities."""
    from game.character.skills import present_training_options
    from game.systems.lifestyle import present_lifestyle_choices

    print_subheader("OFF DAY")

    options = [
        ("Train", "Hit the gym and work on your skills"),
        ("Rest", "Recover health and let your body heal"),
        ("Go Out", "Hit the town - bars, clubs, social scene"),
        ("Study Tape", "Watch matches and study the craft"),
    ]

    # Add relationship option if in one
    if state.player.relationship_status != "single":
        options.append(("Spend Time with Partner", "Maintain your relationship"))

    choice = print_menu(options, "How do you spend your off day?")

    player = state.player

    if choice == 0:  # Train
        present_training_options(player)
    elif choice == 1:  # Rest
        recovery = random.randint(10, 20)
        player.health = min(100, player.health + recovery)
        player.burnout = max(0, player.burnout - 5)
        print(f"\n  You rest up. Health +{recovery}. Burnout reduced.")
    elif choice == 2:  # Go out
        present_lifestyle_choices(player, "night_out")
    elif choice == 3:  # Study tape
        # Small boost to psychology and in_ring
        from game.character.skills import train_skill
        xp = random.randint(5, 12)
        skill = random.choice(["psychology", "in_ring"])
        leveled = player.add_skill_xp(skill, xp)
        from data.constants import SKILL_DISPLAY_NAMES
        print(f"\n  You study wrestling tapes for hours.")
        print(f"  {SKILL_DISPLAY_NAMES[skill]} +{xp} XP" + (" - LEVEL UP!" if leveled else ""))
    elif choice == 4:  # Relationship
        player.relationship_health = min(100, player.relationship_health + 10)
        player.burnout = max(0, player.burnout - 3)
        print(f"\n  You spend quality time with {player.relationship_partner or 'your partner'}.")
        print(f"  Relationship health improved. Burnout reduced.")

    press_enter()


def monthly_phase(state):
    """Monthly career checks."""
    from game.systems.reputation import calculate_push_level

    player = state.player

    # Update push level
    player.momentum = calculate_push_level(player)

    # Financial check
    player.money -= 200 * 4  # Monthly expenses
    if player.money < 0:
        _msg = "You're broke. Living paycheck to paycheck."
        print(f"\n  {colored(_msg, Colors.WARNING)}")
        player.burnout += 5

    # Title defense tracking
    if player.titles_held:
        player.weeks_as_champion += 4


def yearly_phase(state):
    """Yearly career milestones."""
    from game.character.skills import check_skill_milestones
    from game.systems.aging import process_aging, check_retirement_prompt

    player = state.player
    player.age += 1

    print_subheader(f"YEAR {state.current_year} IN REVIEW")
    print(f"  Age: {player.age}")
    print(f"  Record this year: Check your stats")
    print(f"  Current Popularity: {player.popularity}")
    print(f"  Money: ${player.money:,}")

    # Age effects
    process_aging(player)

    # Skill milestones
    check_skill_milestones(player)

    # Retirement check
    if player.age >= 35:
        check_retirement_prompt(state)

    press_enter()


def weekly_menu(state):
    """Show end-of-week menu options."""
    print_divider()
    options = [
        "Continue to next week",
        "View stats",
        "View career history",
        "Save game",
        "Retire",
    ]

    choice = print_menu(options, "What would you like to do?")

    if choice == 0:
        return
    elif choice == 1:
        clear_screen()
        print_stats(state.player)
        press_enter()
        weekly_menu(state)
    elif choice == 2:
        clear_screen()
        print_subheader("CAREER LOG")
        if state.career_log:
            for entry in state.career_log[-20:]:
                print(f"  Year {entry['year']}, Week {entry['week']}: {entry['text']}")
        else:
            print("  No notable events yet.")
        press_enter()
        weekly_menu(state)
    elif choice == 3:
        present_save_menu(state)
        weekly_menu(state)
    elif choice == 4:
        if confirm("Are you sure you want to retire?"):
            state.game_over = True
            state.game_over_reason = "retirement"
            state.log_career_event(f"Retired from professional wrestling at age {state.player.age}")


def _is_ppv_week(state):
    """Check if current week is a PPV week."""
    if hasattr(state, 'calendar') and state.calendar:
        return state.calendar.is_ppv_week(state.player.current_promotion)
    # Fallback: every 4th week
    return state.current_week % 4 == 0


def _advance_week(state):
    """Advance the game calendar by one week."""
    state.total_weeks += 1
    state.current_week += 1

    if state.current_week > 52:
        state.current_week = 1
        state.current_year += 1

    # Advance calendar object if present
    if hasattr(state, 'calendar') and state.calendar:
        result = state.calendar.advance_week()
        if result.get("rolled_month"):
            state.calendar.schedule_month([state.player.current_promotion])


def _handle_contract_expiry(state):
    """Handle contract expiration."""
    from game.world.promotions import PROMOTIONS, get_available_promotions
    from game.world.contracts import generate_offer

    player = state.player
    promo = PROMOTIONS.get(player.current_promotion)
    promo_name = promo.name if promo else player.current_promotion

    print_subheader("CONTRACT EXPIRED")
    print(f"  Your contract with {promo_name} has expired.")

    # Current promotion may offer renewal
    options = []
    if promo:
        new_offer = generate_offer(promo, player)
        options.append((
            f"Re-sign with {promo_name}",
            f"${new_offer.pay_per_show}/show, {new_offer.weeks_duration} weeks",
        ))

    # Other promotions may be interested
    available = get_available_promotions(player)
    available = [p for p in available if p.id != player.current_promotion][:3]
    for ap in available:
        offer = generate_offer(ap, player)
        options.append((
            f"Sign with {ap.name}",
            f"${offer.pay_per_show}/show, {offer.weeks_duration} weeks (Tier {ap.tier})",
        ))

    options.append(("Go freelance", "No contract. Work when you want."))

    choice = print_menu(options, "What do you do?")

    if choice == 0 and promo:
        # Re-sign
        new_offer = generate_offer(promo, player)
        state.contract = {
            "promotion_id": promo.id,
            "weeks_remaining": new_offer.weeks_duration,
            "pay_per_show": new_offer.pay_per_show,
            "exclusive": new_offer.exclusive,
        }
        player.money += new_offer.signing_bonus
        print(f"\n  Re-signed with {promo_name}!")
        if new_offer.signing_bonus:
            print(f"  Signing bonus: ${new_offer.signing_bonus:,}")
        state.log_career_event(f"Re-signed with {promo_name}")
    elif choice <= len(available) and choice > 0:
        # Sign with new promotion
        new_promo = available[choice - 1]
        offer = generate_offer(new_promo, player)
        player.current_promotion = new_promo.id
        if new_promo.id not in player.career_promotions:
            player.career_promotions.append(new_promo.id)
        state.contract = {
            "promotion_id": new_promo.id,
            "weeks_remaining": offer.weeks_duration,
            "pay_per_show": offer.pay_per_show,
            "exclusive": offer.exclusive,
        }
        player.money += offer.signing_bonus
        print(f"\n  Signed with {new_promo.name}!")
        if offer.signing_bonus:
            print(f"  Signing bonus: ${offer.signing_bonus:,}")
        state.log_career_event(f"Signed with {new_promo.name}")
    else:
        # Freelance
        state.contract = {
            "promotion_id": player.current_promotion,
            "weeks_remaining": 12,
            "pay_per_show": 50,
            "exclusive": False,
        }
        print(f"\n  You go freelance. Working indie dates.")

    press_enter()


def check_game_over(state):
    """Check for game-over conditions."""
    player = state.player

    if player.is_dead:
        state.game_over = True
        state.game_over_reason = "death"
        return

    if player.is_retired:
        state.game_over = True
        state.game_over_reason = "retirement"
        return

    if player.age >= 55:
        _msg = "Your body can't take it anymore. It's time to hang up the boots."
        print(f"\n  {colored(_msg, Colors.WARNING)}")
        state.game_over = True
        state.game_over_reason = "age"
        state.log_career_event("Forced to retire due to age")
