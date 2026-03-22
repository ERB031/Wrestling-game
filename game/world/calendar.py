"""Calendar system for tracking game time, shows, and PPV scheduling."""

from dataclasses import dataclass, field


# ---------------------------------------------------------------------------
# PPV schedules per promotion (month numbers when PPVs occur)
# ---------------------------------------------------------------------------

PROMOTION_PPVS = {
    "backyard": {
        6: "Backyard Bash",
        9: "Trampoline Deathmatch",
    },
    "czw": {
        2: "Cage of Death",
        5: "Tournament of Death: Qualifiers",
        6: "Tournament of Death",
        9: "Tangled Web",
        12: "Final Exam",
    },
    "roh": {
        1: "Final Battle Fallout",
        3: "Supercard of Honor",
        5: "War of the Worlds",
        7: "Best in the World",
        9: "Death Before Dishonor",
        11: "Final Battle",
    },
    "pwg": {
        3: "All Star Weekend",
        6: "Mystery Vortex",
        8: "Battle of Los Angeles: Night 1",
        9: "Battle of Los Angeles: Finals",
        11: "Thirteen",
    },
    "njpw": {
        1: "Wrestle Kingdom",
        2: "The New Beginning",
        4: "Sakura Genesis",
        5: "Wrestling Dontaku",
        6: "Dominion",
        7: "G1 Climax Opening",
        8: "G1 Climax Finals",
        10: "King of Pro Wrestling",
        11: "Power Struggle",
    },
    "ajpw": {
        1: "New Year Wars",
        3: "Champion Carnival Opening",
        4: "Champion Carnival Finals",
        7: "Summer Action Series",
        10: "Royal Road Tournament",
        12: "World's Strongest Tag Determination League",
    },
    "ecw": {
        1: "Guilty as Charged",
        3: "Living Dangerously",
        5: "Hardcore Heaven",
        7: "Heat Wave",
        9: "Anarchy Rulz",
        11: "November to Remember",
    },
    "tna": {
        1: "Genesis",
        3: "Lockdown",
        5: "Slammiversary",
        7: "Destination X",
        9: "No Surrender",
        11: "Bound for Glory",
    },
    "nxt": {
        1: "New Year's Evil",
        4: "Stand & Deliver",
        6: "The Great American Bash",
        8: "Heatwave",
        10: "Halloween Havoc",
        12: "Deadline",
    },
    "aew": {
        1: "Worlds End Aftermath",
        3: "Revolution",
        5: "Double or Nothing",
        6: "Forbidden Door",
        7: "All In",
        9: "All Out",
        11: "Full Gear",
        12: "Worlds End",
    },
    "wwe": {
        1: "Royal Rumble",
        2: "Elimination Chamber",
        4: "WrestleMania",
        5: "Backlash",
        6: "Money in the Bank",
        7: "SummerSlam",
        9: "Clash at the Castle",
        10: "Crown Jewel",
        11: "Survivor Series",
        12: "Saturday Night's Main Event",
    },
    "retirement": {
        4: "Legends Showdown",
        10: "Old School Raw",
    },
}


MONTHS = [
    "January", "February", "March", "April", "May", "June",
    "July", "August", "September", "October", "November", "December",
]

WEEKS_PER_MONTH = 4
MONTHS_PER_YEAR = 12
WEEKS_PER_YEAR = WEEKS_PER_MONTH * MONTHS_PER_YEAR  # 48 (simplified)


@dataclass
class Show:
    """A single scheduled show (weekly TV or PPV)."""
    promotion_id: str
    name: str
    week: int
    month: int
    year: int
    is_ppv: bool = False

    def to_dict(self):
        return self.__dict__.copy()

    @classmethod
    def from_dict(cls, data):
        return cls(**data)

    def __str__(self):
        label = "PPV" if self.is_ppv else "Show"
        return f"[{label}] {self.name} (Week {self.week}, {MONTHS[self.month - 1]} Year {self.year})"


@dataclass
class Calendar:
    """Tracks the passage of game time and scheduled events."""
    week: int = 1          # 1–4 within the month
    month: int = 1         # 1–12
    year: int = 1          # Starts at year 1

    # Upcoming shows (populated each month)
    scheduled_shows: list = field(default_factory=list)

    # History of past shows
    show_history: list = field(default_factory=list)

    def advance_week(self):
        """Move the calendar forward by one week.

        Returns
        -------
        dict
            Info about the new week including any shows happening.
        """
        self.week += 1
        rolled_month = False
        rolled_year = False

        if self.week > WEEKS_PER_MONTH:
            self.week = 1
            self.month += 1
            rolled_month = True

        if self.month > MONTHS_PER_YEAR:
            self.month = 1
            self.year += 1
            rolled_year = True

        return {
            "week": self.week,
            "month": self.month,
            "year": self.year,
            "rolled_month": rolled_month,
            "rolled_year": rolled_year,
        }

    def get_current_week_number(self):
        """Return the absolute week number since the start of the game."""
        return (self.year - 1) * WEEKS_PER_YEAR + (self.month - 1) * WEEKS_PER_MONTH + self.week

    def get_date_string(self):
        """Human-readable date string."""
        return f"Week {self.week}, {MONTHS[self.month - 1]}, Year {self.year}"

    # ------------------------------------------------------------------
    # Show scheduling
    # ------------------------------------------------------------------

    def schedule_month(self, active_promotion_ids):
        """Generate the schedule for the current month.

        Parameters
        ----------
        active_promotion_ids : list[str]
            Promotion ids that the player might interact with.
        """
        self.scheduled_shows = []

        for promo_id in active_promotion_ids:
            ppv_schedule = PROMOTION_PPVS.get(promo_id, {})

            # Check for a PPV this month
            ppv_name = ppv_schedule.get(self.month)
            if ppv_name:
                ppv_week = WEEKS_PER_MONTH  # PPVs happen on the last week
                self.scheduled_shows.append(Show(
                    promotion_id=promo_id,
                    name=ppv_name,
                    week=ppv_week,
                    month=self.month,
                    year=self.year,
                    is_ppv=True,
                ))

            # Regular weekly shows (every week, or every other week for smaller promos)
            from game.world.promotions import get_promotion
            promo = get_promotion(promo_id)
            if promo is None:
                continue

            if promo.tv_deal:
                # Weekly TV: every week of the month
                for w in range(1, WEEKS_PER_MONTH + 1):
                    # Skip the PPV week for the regular show name
                    if ppv_name and w == WEEKS_PER_MONTH:
                        continue
                    self.scheduled_shows.append(Show(
                        promotion_id=promo_id,
                        name=f"{promo.short_name} Weekly",
                        week=w,
                        month=self.month,
                        year=self.year,
                        is_ppv=False,
                    ))
            else:
                # Non-TV promotions run shows every other week
                for w in [1, 3]:
                    if ppv_name and w == WEEKS_PER_MONTH:
                        continue
                    self.scheduled_shows.append(Show(
                        promotion_id=promo_id,
                        name=f"{promo.short_name} Live Event",
                        week=w,
                        month=self.month,
                        year=self.year,
                        is_ppv=False,
                    ))

        # Sort by week
        self.scheduled_shows.sort(key=lambda s: s.week)

    def get_shows_this_week(self, promotion_id=None):
        """Return shows happening this week, optionally filtered by promotion."""
        shows = [
            s for s in self.scheduled_shows
            if s.week == self.week and s.month == self.month and s.year == self.year
        ]
        if promotion_id:
            shows = [s for s in shows if s.promotion_id == promotion_id]
        return shows

    def is_ppv_week(self, promotion_id=None):
        """Check whether any show this week is a PPV."""
        shows = self.get_shows_this_week(promotion_id)
        return any(s.is_ppv for s in shows)

    def get_upcoming_ppvs(self, promotion_id=None, lookahead_months=3):
        """Return PPVs coming up in the next N months.

        Parameters
        ----------
        promotion_id : str or None
            Filter by promotion; None returns all.
        lookahead_months : int
            How many months ahead to look.

        Returns
        -------
        list[dict]
            Each dict has promotion_id, ppv_name, month, month_name.
        """
        upcoming = []
        for offset in range(lookahead_months):
            future_month = ((self.month - 1 + offset) % MONTHS_PER_YEAR) + 1
            future_year = self.year + ((self.month - 1 + offset) // MONTHS_PER_YEAR)

            for promo_id, ppv_schedule in PROMOTION_PPVS.items():
                if promotion_id and promo_id != promotion_id:
                    continue
                ppv_name = ppv_schedule.get(future_month)
                if ppv_name:
                    upcoming.append({
                        "promotion_id": promo_id,
                        "ppv_name": ppv_name,
                        "month": future_month,
                        "month_name": MONTHS[future_month - 1],
                        "year": future_year,
                    })

        return upcoming

    def archive_week(self):
        """Move this week's shows into the history."""
        current = self.get_shows_this_week()
        for show in current:
            self.show_history.append(show)
        self.scheduled_shows = [
            s for s in self.scheduled_shows if s not in current
        ]

    # ------------------------------------------------------------------
    # Serialization
    # ------------------------------------------------------------------

    def to_dict(self):
        return {
            "week": self.week,
            "month": self.month,
            "year": self.year,
            "scheduled_shows": [s.to_dict() for s in self.scheduled_shows],
            "show_history": [s.to_dict() for s in self.show_history],
        }

    @classmethod
    def from_dict(cls, data):
        cal = cls(
            week=data["week"],
            month=data["month"],
            year=data["year"],
        )
        cal.scheduled_shows = [Show.from_dict(s) for s in data.get("scheduled_shows", [])]
        cal.show_history = [Show.from_dict(s) for s in data.get("show_history", [])]
        return cal
