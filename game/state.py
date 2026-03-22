"""Central game state container."""

from dataclasses import dataclass, field
from game.character.wrestler import Wrestler


@dataclass
class GameState:
    """Holds all game state for saving/loading and passing between systems."""

    # Player
    player: Wrestler = None

    # Time
    current_week: int = 1
    current_year: int = 1
    total_weeks: int = 0

    # World state
    promotion_rosters: dict = field(default_factory=dict)  # {promo_id: [Wrestler]}
    title_holders: dict = field(default_factory=dict)  # {title_id: npc_id or "player"}
    title_history: dict = field(default_factory=dict)  # {title_id: [(holder, weeks_held)]}

    # Current storyline
    active_storyline: dict = field(default_factory=dict)  # Active storyline data or {}
    storyline_history: list = field(default_factory=list)

    # Calendar
    ppv_schedule: list = field(default_factory=list)  # Upcoming PPVs
    next_ppv_week: int = 0
    is_ppv_week: bool = False

    # Contract
    contract: dict = field(default_factory=dict)  # Current contract details

    # Tracking
    match_history: list = field(default_factory=list)  # List of match result dicts
    event_cooldowns: dict = field(default_factory=dict)  # {event_id: weeks_until_available}
    career_log: list = field(default_factory=list)  # Notable career moments

    # NPC tracking
    npc_registry: dict = field(default_factory=dict)  # {npc_id: Wrestler.to_dict()}

    # Calendar and title manager (set in initialize_world)
    calendar: object = None
    title_manager: object = None

    # Game flags
    game_over: bool = False
    game_over_reason: str = ""
    save_slot: int = 0

    def get_current_roster(self):
        """Get the roster for the player's current promotion."""
        if not self.player or not self.player.current_promotion:
            return []
        return self.promotion_rosters.get(self.player.current_promotion, [])

    def get_npc(self, npc_id):
        """Get an NPC wrestler by ID."""
        data = self.npc_registry.get(npc_id)
        if data:
            return Wrestler.from_dict(data) if isinstance(data, dict) else data
        return None

    def register_npc(self, wrestler):
        """Register an NPC in the global registry."""
        self.npc_registry[wrestler.npc_id] = wrestler

    def log_career_event(self, text):
        """Add a notable event to the career log."""
        self.career_log.append({
            "week": self.current_week,
            "year": self.current_year,
            "total_week": self.total_weeks,
            "text": text,
        })

    def get_career_summary(self):
        """Generate end-of-career summary stats."""
        p = self.player
        return {
            "years_active": self.current_year,
            "total_matches": p.total_matches,
            "wins": p.wins,
            "losses": p.losses,
            "draws": p.draws,
            "titles_won": len(p.career_titles),
            "title_list": p.career_titles,
            "best_match": p.best_match_rating,
            "peak_popularity": p.peak_popularity,
            "promotions": p.career_promotions,
            "total_earnings": p.total_earnings,
            "legacy_score": self._calculate_legacy_score(),
        }

    def _calculate_legacy_score(self):
        """Calculate Hall of Fame legacy score (0-100)."""
        p = self.player
        score = 0

        # Titles (max 30 points)
        score += min(30, len(p.career_titles) * 6)

        # Match quality (max 20 points)
        if p.best_match_rating >= 5.0:
            score += 20
        elif p.best_match_rating >= 4.5:
            score += 16
        elif p.best_match_rating >= 4.0:
            score += 12
        elif p.best_match_rating >= 3.5:
            score += 8

        # Popularity (max 20 points)
        score += int(p.peak_popularity * 0.2)

        # Longevity (max 15 points)
        score += min(15, self.current_year)

        # Win record (max 10 points)
        if p.total_matches > 0:
            win_pct = p.wins / p.total_matches
            score += int(win_pct * 10)

        # Promotion variety (max 5 points)
        score += min(5, len(p.career_promotions))

        return min(100, score)

    def to_dict(self):
        """Serialize full game state for saving."""
        data = {
            "player": self.player.to_dict() if self.player else None,
            "current_week": self.current_week,
            "current_year": self.current_year,
            "total_weeks": self.total_weeks,
            "title_holders": self.title_holders,
            "title_history": self.title_history,
            "active_storyline": self.active_storyline,
            "storyline_history": self.storyline_history,
            "ppv_schedule": self.ppv_schedule,
            "next_ppv_week": self.next_ppv_week,
            "contract": self.contract,
            "match_history": self.match_history,
            "event_cooldowns": self.event_cooldowns,
            "career_log": self.career_log,
            "game_over": self.game_over,
            "game_over_reason": self.game_over_reason,
            "save_slot": self.save_slot,
        }

        # Serialize calendar
        if self.calendar:
            data["calendar"] = self.calendar.to_dict()

        # Serialize title manager
        if self.title_manager:
            data["title_manager"] = self.title_manager.to_dict()

        # Serialize NPC registry
        npc_data = {}
        for npc_id, npc in self.npc_registry.items():
            if isinstance(npc, Wrestler):
                npc_data[npc_id] = npc.to_dict()
            else:
                npc_data[npc_id] = npc
        data["npc_registry"] = npc_data

        # Serialize rosters (just NPC IDs)
        roster_data = {}
        for promo_id, roster in self.promotion_rosters.items():
            roster_data[promo_id] = [
                w.npc_id if isinstance(w, Wrestler) else w
                for w in roster
            ]
        data["promotion_rosters"] = roster_data

        return data

    @classmethod
    def from_dict(cls, data):
        """Deserialize game state from saved data."""
        state = cls()

        if data.get("player"):
            state.player = Wrestler.from_dict(data["player"])

        state.current_week = data.get("current_week", 1)
        state.current_year = data.get("current_year", 1)
        state.total_weeks = data.get("total_weeks", 0)
        state.title_holders = data.get("title_holders", {})
        state.title_history = data.get("title_history", {})
        state.active_storyline = data.get("active_storyline", {})
        state.storyline_history = data.get("storyline_history", [])
        state.ppv_schedule = data.get("ppv_schedule", [])
        state.next_ppv_week = data.get("next_ppv_week", 0)
        state.contract = data.get("contract", {})
        state.match_history = data.get("match_history", [])
        state.event_cooldowns = data.get("event_cooldowns", {})
        state.career_log = data.get("career_log", [])
        state.game_over = data.get("game_over", False)
        state.game_over_reason = data.get("game_over_reason", "")
        state.save_slot = data.get("save_slot", 0)

        # Restore NPC registry
        for npc_id, npc_data in data.get("npc_registry", {}).items():
            if isinstance(npc_data, dict):
                state.npc_registry[npc_id] = Wrestler.from_dict(npc_data)
            else:
                state.npc_registry[npc_id] = npc_data

        # Restore rosters (resolve NPC IDs to Wrestler objects)
        for promo_id, npc_ids in data.get("promotion_rosters", {}).items():
            roster = []
            for npc_id in npc_ids:
                npc = state.npc_registry.get(npc_id)
                if npc:
                    roster.append(npc)
            state.promotion_rosters[promo_id] = roster

        # Restore calendar
        if data.get("calendar"):
            from game.world.calendar import Calendar
            state.calendar = Calendar.from_dict(data["calendar"])

        # Restore title manager
        if data.get("title_manager"):
            from game.world.titles import TitleManager
            state.title_manager = TitleManager.from_dict(data["title_manager"])

        return state
