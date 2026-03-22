"""Terminal UI display functions with ANSI color support."""

import os
import sys
import time


# ANSI color codes
class Colors:
    RESET = "\033[0m"
    BOLD = "\033[1m"
    DIM = "\033[2m"
    ITALIC = "\033[3m"
    UNDERLINE = "\033[4m"

    RED = "\033[31m"
    GREEN = "\033[32m"
    YELLOW = "\033[33m"
    BLUE = "\033[34m"
    MAGENTA = "\033[35m"
    CYAN = "\033[36m"
    WHITE = "\033[37m"

    BG_RED = "\033[41m"
    BG_GREEN = "\033[42m"
    BG_YELLOW = "\033[43m"
    BG_BLUE = "\033[44m"

    # Semantic colors
    BLOOD = "\033[91m"       # Bright red for violence/blood
    GOLD = "\033[93m"        # Bright yellow for titles/achievements
    HEEL = "\033[31m"        # Red for heel
    FACE = "\033[34m"        # Blue for face
    INJURY = "\033[91m"      # Red for injuries
    MONEY = "\033[92m"       # Green for money
    WARNING = "\033[93m"     # Yellow for warnings
    PROMO = "\033[96m"       # Cyan for promos


def clear_screen():
    """Clear the terminal screen."""
    os.system('cls' if os.name == 'nt' else 'clear')


def colored(text, color):
    """Wrap text in ANSI color codes."""
    return f"{color}{text}{Colors.RESET}"


def bold(text):
    return f"{Colors.BOLD}{text}{Colors.RESET}"


def dim(text):
    return f"{Colors.DIM}{text}{Colors.RESET}"


def print_header(text, width=60, char="="):
    """Print a boxed header."""
    border = char * width
    padding = (width - len(text) - 2) // 2
    line = f"{char}{' ' * padding}{text}{' ' * (width - padding - len(text) - 2)}{char}"
    print(colored(border, Colors.GOLD))
    print(colored(line, Colors.GOLD))
    print(colored(border, Colors.GOLD))


def print_subheader(text, width=60, char="-"):
    """Print a smaller header."""
    border = char * width
    print(f"\n{border}")
    print(f"  {bold(text)}")
    print(border)


def print_divider(width=60, char="-"):
    print(char * width)


def print_stat_bar(label, value, max_val=100, width=20, color=Colors.GREEN):
    """Print a stat with a visual bar."""
    filled = int((value / max_val) * width)
    bar = "█" * filled + "░" * (width - filled)
    label_padded = f"{label:<14}"
    print(f"  {label_padded} {colored(bar, color)} {value:>3}/{max_val}")


def print_stats(wrestler):
    """Print full wrestler stat block."""
    from data.constants import SKILL_DISPLAY_NAMES

    print_subheader(f"Stats: {wrestler.ring_name}")
    for skill_id, display_name in SKILL_DISPLAY_NAMES.items():
        value = wrestler.skills.get(skill_id, 0)
        if value >= 80:
            color = Colors.GOLD
        elif value >= 60:
            color = Colors.GREEN
        elif value >= 40:
            color = Colors.YELLOW
        else:
            color = Colors.RED
        print_stat_bar(display_name, value, color=color)

    # Derived stats
    print()
    alignment_str = get_alignment_string(wrestler.alignment)
    alignment_color = Colors.FACE if wrestler.alignment > 0 else Colors.HEEL if wrestler.alignment < 0 else Colors.WHITE
    print(f"  {'Alignment':<14} {colored(alignment_str, alignment_color)} ({wrestler.alignment:+d})")
    print(f"  {'Popularity':<14} {wrestler.popularity}")
    print(f"  {'Backstage Rep':<14} {wrestler.backstage_rep:+d}")
    print(f"  {'Money':<14} {colored(f'${wrestler.money:,}', Colors.MONEY)}")
    print(f"  {'Health':<14} {wrestler.health}%")


def get_alignment_string(alignment):
    """Get alignment zone name from value."""
    from data.constants import ALIGNMENT_ZONES, ALIGNMENT_NAMES
    for zone_id, (low, high) in ALIGNMENT_ZONES.items():
        if low <= alignment <= high:
            return ALIGNMENT_NAMES[zone_id]
    if alignment < -100:
        return "Mega Heel"
    return "Mega Face"


def print_menu(options, prompt="Choose an option"):
    """Display a numbered menu and get player choice."""
    print()
    for i, option in enumerate(options, 1):
        if isinstance(option, tuple):
            label, description = option
            print(f"  {colored(str(i), Colors.CYAN)}. {bold(label)}")
            if description:
                print(f"     {dim(description)}")
        else:
            print(f"  {colored(str(i), Colors.CYAN)}. {option}")

    print()
    while True:
        try:
            choice = input(f"  {prompt} (1-{len(options)}): ").strip()
            if not choice:
                continue
            idx = int(choice)
            if 1 <= idx <= len(options):
                return idx - 1  # Return 0-indexed
        except (ValueError, EOFError):
            pass
        print(f"  {colored('Invalid choice. Try again.', Colors.RED)}")


def print_match_moment(text, delay=0.03):
    """Print match narration with dramatic pacing."""
    for char in text:
        sys.stdout.write(char)
        sys.stdout.flush()
        time.sleep(delay)
    print()


def print_dramatic(text, delay=1.0):
    """Print text with a dramatic pause after."""
    print(f"\n  {bold(text)}")
    time.sleep(delay)


def print_crowd_reaction(reaction, intensity=1):
    """Print crowd noise."""
    reactions = {
        "pop": ["*mild pop*", "*BIG POP!*", "*THE ROOF BLOWS OFF!*"],
        "heat": ["*scattered boos*", "*LOUD BOOS!*", "*NUCLEAR HEAT!*"],
        "chant": ["*crowd starts chanting*", "*THE CHANT IS DEAFENING!*", "*EVERY PERSON IS ON THEIR FEET CHANTING!*"],
        "gasp": ["*crowd murmurs*", "*CROWD GASPS!*", "*STUNNED SILENCE THEN PANDEMONIUM!*"],
        "holy_shit": ["*holy shit! holy shit!*", "*HOLY SHIT! HOLY SHIT! HOLY SHIT!*"],
    }
    idx = min(intensity - 1, len(reactions.get(reaction, [""])) - 1)
    text = reactions.get(reaction, [""])[idx]
    color = Colors.GOLD if reaction in ("pop", "chant") else Colors.BLOOD if reaction == "holy_shit" else Colors.YELLOW
    print(f"\n    {colored(text, color)}")


def print_injury_report(injury):
    """Print an injury notification."""
    severity_words = {1: "Minor", 2: "Moderate", 3: "MAJOR", 4: "CAREER-THREATENING"}
    sev_text = severity_words.get(injury.severity, "Unknown")
    color = Colors.YELLOW if injury.severity <= 2 else Colors.BLOOD
    print(f"\n  {colored('⚠ INJURY:', color)} {colored(sev_text, color)}")
    print(f"    {injury.description} ({injury.body_part.replace('_', ' ').title()})")
    print(f"    Recovery: {injury.weeks_remaining} weeks")


def print_title_change(winner_name, title_name):
    """Print a title change announcement."""
    print()
    print(colored("  ★ ★ ★ ★ ★ ★ ★ ★ ★ ★ ★ ★ ★ ★ ★ ★ ★ ★ ★ ★", Colors.GOLD))
    print(colored(f"  NEW {title_name.upper()}!", Colors.GOLD))
    print(colored(f"  {winner_name}!", Colors.GOLD))
    print(colored("  ★ ★ ★ ★ ★ ★ ★ ★ ★ ★ ★ ★ ★ ★ ★ ★ ★ ★ ★ ★", Colors.GOLD))


def print_match_rating(stars):
    """Print match star rating."""
    full = int(stars)
    half = stars - full >= 0.25
    star_str = "★" * full + ("½" if half else "") + "☆" * (5 - full - (1 if half else 0))
    if stars >= 4.5:
        color = Colors.GOLD
    elif stars >= 3.5:
        color = Colors.GREEN
    elif stars >= 2.5:
        color = Colors.YELLOW
    else:
        color = Colors.RED
    print(f"\n  Match Rating: {colored(star_str, color)} ({stars:.2f})")


def get_input(prompt=""):
    """Get input from the player with error handling."""
    try:
        return input(f"  {prompt}").strip()
    except (EOFError, KeyboardInterrupt):
        print()
        return ""


def confirm(prompt="Continue?"):
    """Ask for yes/no confirmation."""
    response = get_input(f"{prompt} (y/n): ").lower()
    return response in ("y", "yes")


def press_enter():
    """Wait for player to press enter."""
    get_input("\nPress Enter to continue...")


def print_week_header(week, year, promotion_name, wrestler):
    """Print the weekly status header."""
    alignment_str = get_alignment_string(wrestler.alignment)
    alignment_color = Colors.FACE if wrestler.alignment > 0 else Colors.HEEL if wrestler.alignment < 0 else Colors.WHITE

    print()
    print(colored("═" * 60, Colors.GOLD))
    print(f"  WEEK {week} | YEAR {year} | {colored(promotion_name, Colors.CYAN)}")
    print(f'  "{wrestler.ring_name}" {wrestler.real_name} | Age: {wrestler.age}')
    print(f"  Record: {wrestler.wins}-{wrestler.losses} | {colored(alignment_str, alignment_color)} ({wrestler.alignment:+d}) | Pop: {wrestler.popularity}")
    if wrestler.titles_held:
        for title in wrestler.titles_held:
            print(f"  {colored('★ ' + title, Colors.GOLD)}")
    print(colored("═" * 60, Colors.GOLD))


def print_game_over(wrestler, career_summary):
    """Print the end-of-career summary."""
    clear_screen()
    print()
    print_header("CAREER OVER", char="★")
    print()
    print(f'  {bold(wrestler.ring_name)} "{wrestler.real_name}"')
    print(f"  Career Span: {career_summary['years_active']} years")
    print(f"  Final Record: {wrestler.wins}-{wrestler.losses}")
    print(f"  Championships Won: {career_summary['titles_won']}")
    print(f"  Best Match Rating: {career_summary['best_match']:.2f} stars")
    print(f"  Peak Popularity: {career_summary['peak_popularity']}")
    print(f"  Promotions Worked: {', '.join(career_summary['promotions'])}")
    total_earnings = career_summary["total_earnings"]
    print(f"  Career Earnings: {colored(f'${total_earnings:,}', Colors.MONEY)}")
    print()

    # Hall of Fame check
    score = career_summary.get("legacy_score", 0)
    if score >= 90:
        print(colored("  ★ ★ ★ FIRST BALLOT HALL OF FAMER ★ ★ ★", Colors.GOLD))
    elif score >= 70:
        print(colored("  ★ ★ HALL OF FAME INDUCTEE ★ ★", Colors.GOLD))
    elif score >= 50:
        print(colored("  ★ HALL OF FAME WORTHY ★", Colors.GOLD))
    else:
        print(dim("  A career that will be remembered by the true fans."))

    print(f"\n  Legacy Score: {colored(str(score), Colors.GOLD)}/100")
    print()
