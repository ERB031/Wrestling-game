"""Championship title tracking, history, and match logic."""

import random
from dataclasses import dataclass, field


@dataclass
class TitleReign:
    """A single reign (period of holding a title)."""
    holder_id: str          # npc_id or "player"
    holder_name: str        # ring name for display
    promotion_id: str
    title_name: str
    won_week: int           # Absolute week number when won
    lost_week: int = 0      # 0 means reign is active
    defenses: int = 0

    def is_active(self):
        return self.lost_week == 0

    def reign_length(self, current_week=0):
        """Return reign length in weeks."""
        end = self.lost_week if self.lost_week else current_week
        return max(0, end - self.won_week)

    def to_dict(self):
        return self.__dict__.copy()

    @classmethod
    def from_dict(cls, data):
        return cls(**data)


class TitleManager:
    """Manages all championship titles across all promotions.

    Tracks current holders, full title history, and provides
    match-related title logic.
    """

    def __init__(self):
        # {promotion_id: {title_name: TitleReign or None}}
        self.current_champions = {}
        # Full history: list of TitleReign
        self.title_history = []

    def initialize_titles(self, promotions_dict, rosters_dict):
        """Set up initial champions from generated rosters.

        Parameters
        ----------
        promotions_dict : dict[str, Promotion]
        rosters_dict : dict[str, list[Wrestler]]
        """
        for promo_id, promo in promotions_dict.items():
            self.current_champions[promo_id] = {}
            roster = rosters_dict.get(promo_id, [])

            for title in promo.titles:
                if title.is_tag or title.is_womens:
                    # Skip tag and women's titles for now (simplified)
                    self.current_champions[promo_id][title.name] = None
                    continue

                if roster:
                    # Pick the best wrestler for the most prestigious title
                    candidates = sorted(roster, key=lambda w: w.get_overall_rating(), reverse=True)
                    champ = candidates[0]
                    roster = roster[1:]  # Don't double-assign

                    reign = TitleReign(
                        holder_id=champ.npc_id,
                        holder_name=champ.ring_name,
                        promotion_id=promo_id,
                        title_name=title.name,
                        won_week=0,
                        defenses=random.randint(0, 5),
                    )
                    self.current_champions[promo_id][title.name] = reign
                    self.title_history.append(reign)
                else:
                    self.current_champions[promo_id][title.name] = None

    # ------------------------------------------------------------------
    # Queries
    # ------------------------------------------------------------------

    def get_champion(self, promotion_id, title_name):
        """Return the active TitleReign for a specific title, or None if vacant."""
        promo_titles = self.current_champions.get(promotion_id, {})
        reign = promo_titles.get(title_name)
        if reign and reign.is_active():
            return reign
        return None

    def get_all_champions(self, promotion_id):
        """Return a dict of {title_name: TitleReign or None} for a promotion."""
        return self.current_champions.get(promotion_id, {})

    def get_title_history(self, promotion_id=None, title_name=None):
        """Return title history, optionally filtered."""
        history = self.title_history
        if promotion_id:
            history = [r for r in history if r.promotion_id == promotion_id]
        if title_name:
            history = [r for r in history if r.title_name == title_name]
        return history

    def get_wrestler_titles(self, wrestler_id):
        """Return all active reigns held by a specific wrestler."""
        active = []
        for promo_titles in self.current_champions.values():
            for reign in promo_titles.values():
                if reign and reign.is_active() and reign.holder_id == wrestler_id:
                    active.append(reign)
        return active

    def is_champion(self, wrestler_id, promotion_id=None, title_name=None):
        """Check if a wrestler currently holds any (or a specific) title."""
        titles = self.get_wrestler_titles(wrestler_id)
        if promotion_id:
            titles = [t for t in titles if t.promotion_id == promotion_id]
        if title_name:
            titles = [t for t in titles if t.title_name == title_name]
        return len(titles) > 0

    # ------------------------------------------------------------------
    # Title changes
    # ------------------------------------------------------------------

    def award_title(self, promotion_id, title_name, wrestler_id, wrestler_name, current_week):
        """Award a title to a wrestler (handles vacancy or title change).

        Parameters
        ----------
        promotion_id : str
        title_name : str
        wrestler_id : str
        wrestler_name : str
        current_week : int
            Absolute week number.

        Returns
        -------
        dict
            Result with old_champion info (if any) and new reign.
        """
        old_reign = self.get_champion(promotion_id, title_name)
        old_champion = None

        if old_reign:
            old_reign.lost_week = current_week
            old_champion = {
                "holder_id": old_reign.holder_id,
                "holder_name": old_reign.holder_name,
                "reign_length": old_reign.reign_length(current_week),
                "defenses": old_reign.defenses,
            }

        new_reign = TitleReign(
            holder_id=wrestler_id,
            holder_name=wrestler_name,
            promotion_id=promotion_id,
            title_name=title_name,
            won_week=current_week,
        )
        self.current_champions.setdefault(promotion_id, {})[title_name] = new_reign
        self.title_history.append(new_reign)

        return {
            "title_name": title_name,
            "new_champion": wrestler_name,
            "old_champion": old_champion,
            "reign": new_reign,
        }

    def record_defense(self, promotion_id, title_name):
        """Record a successful title defense."""
        reign = self.get_champion(promotion_id, title_name)
        if reign:
            reign.defenses += 1
            return True
        return False

    def vacate_title(self, promotion_id, title_name, current_week, reason=""):
        """Strip the title from the current holder.

        Parameters
        ----------
        promotion_id : str
        title_name : str
        current_week : int
        reason : str
            Reason for vacating (injury, suspension, etc.)

        Returns
        -------
        dict or None
        """
        reign = self.get_champion(promotion_id, title_name)
        if reign is None:
            return None

        reign.lost_week = current_week
        self.current_champions[promotion_id][title_name] = None

        return {
            "title_name": title_name,
            "former_champion": reign.holder_name,
            "reign_length": reign.reign_length(current_week),
            "reason": reason or "Title vacated",
        }

    # ------------------------------------------------------------------
    # Title match logic
    # ------------------------------------------------------------------

    def resolve_title_match(self, promotion_id, title_name, champion, challenger,
                            match_result, current_week):
        """Process the result of a title match.

        Parameters
        ----------
        promotion_id : str
        title_name : str
        champion : Wrestler
            The defending champion.
        challenger : Wrestler
            The challenger.
        match_result : str
            "champion_wins", "challenger_wins", or "draw".
        current_week : int

        Returns
        -------
        dict
            Outcome including whether a title change happened.
        """
        champ_id = champion.npc_id if champion.npc_id else "player"
        chall_id = challenger.npc_id if challenger.npc_id else "player"

        if match_result == "challenger_wins":
            result = self.award_title(
                promotion_id, title_name,
                chall_id, challenger.ring_name,
                current_week,
            )
            return {
                "title_change": True,
                "new_champion": challenger.ring_name,
                "former_champion": champion.ring_name,
                "details": result,
            }
        elif match_result == "champion_wins":
            self.record_defense(promotion_id, title_name)
            return {
                "title_change": False,
                "champion_retains": champion.ring_name,
                "defenses": self.get_champion(promotion_id, title_name).defenses
                if self.get_champion(promotion_id, title_name) else 0,
            }
        else:
            # Draw — champion retains by default
            self.record_defense(promotion_id, title_name)
            return {
                "title_change": False,
                "draw": True,
                "champion_retains": champion.ring_name,
            }

    def simulate_npc_title_defense(self, promotion_id, title_name, roster, current_week):
        """Simulate an NPC title defense (happens in the background).

        Parameters
        ----------
        promotion_id : str
        title_name : str
        roster : list[Wrestler]
        current_week : int

        Returns
        -------
        dict or None
        """
        reign = self.get_champion(promotion_id, title_name)
        if reign is None:
            return None

        # Find the champion in the roster
        champion = None
        challengers = []
        for w in roster:
            if w.npc_id == reign.holder_id:
                champion = w
            else:
                challengers.append(w)

        if champion is None or not challengers:
            return None

        challenger = random.choice(challengers)

        # Simple outcome based on overall ratings
        champ_rating = champion.get_overall_rating()
        chall_rating = challenger.get_overall_rating()
        champ_advantage = (champ_rating - chall_rating) / 100

        # Champions have a built-in retention bonus
        title_change_chance = 0.20 - (champ_advantage * 0.3)
        title_change_chance = max(0.05, min(0.40, title_change_chance))

        if random.random() < title_change_chance:
            result = "challenger_wins"
        else:
            result = "champion_wins"

        return self.resolve_title_match(
            promotion_id, title_name,
            champion, challenger,
            result, current_week,
        )

    # ------------------------------------------------------------------
    # Serialization
    # ------------------------------------------------------------------

    def to_dict(self):
        champs = {}
        for promo_id, titles in self.current_champions.items():
            champs[promo_id] = {}
            for title_name, reign in titles.items():
                champs[promo_id][title_name] = reign.to_dict() if reign else None
        return {
            "current_champions": champs,
            "title_history": [r.to_dict() for r in self.title_history],
        }

    @classmethod
    def from_dict(cls, data):
        manager = cls()
        for promo_id, titles in data.get("current_champions", {}).items():
            manager.current_champions[promo_id] = {}
            for title_name, reign_data in titles.items():
                if reign_data:
                    manager.current_champions[promo_id][title_name] = TitleReign.from_dict(reign_data)
                else:
                    manager.current_champions[promo_id][title_name] = None
        manager.title_history = [TitleReign.from_dict(r) for r in data.get("title_history", [])]
        return manager
