"""Contract system for wrestler employment agreements."""

import random
from dataclasses import dataclass, field


@dataclass
class Contract:
    """A wrestler's employment contract with a promotion."""
    promotion_id: str
    weeks_duration: int         # Total contract length in weeks
    weeks_remaining: int = 0    # Weeks left on the deal
    pay_per_show: int = 0       # Base pay per appearance
    exclusive: bool = False     # Can the wrestler work elsewhere?
    title_shot_clause: bool = False  # Guaranteed title shot during contract?
    downside_guarantee: int = 0     # Minimum weekly pay even without a show
    merchandise_cut: float = 0.0    # 0.0–1.0 percentage of merch sales
    creative_control: bool = False  # Can refuse storylines
    no_compete_weeks: int = 0       # Weeks after contract expires before signing elsewhere
    signing_bonus: int = 0

    # Internal tracking
    shows_worked: int = 0
    total_earned: int = 0
    is_active: bool = True

    def __post_init__(self):
        if self.weeks_remaining == 0:
            self.weeks_remaining = self.weeks_duration

    def advance_week(self, worked_show=False):
        """Process one week of the contract.

        Parameters
        ----------
        worked_show : bool
            Whether the wrestler appeared on a show this week.

        Returns
        -------
        dict
            Summary including pay earned this week and expiration status.
        """
        if not self.is_active:
            return {"pay": 0, "expired": True}

        self.weeks_remaining -= 1
        pay = 0

        if worked_show:
            pay = self.pay_per_show
            self.shows_worked += 1
        elif self.downside_guarantee > 0:
            pay = self.downside_guarantee

        self.total_earned += pay

        expired = self.weeks_remaining <= 0
        if expired:
            self.is_active = False

        return {
            "pay": pay,
            "expired": expired,
            "weeks_remaining": self.weeks_remaining,
        }

    def is_expired(self):
        return self.weeks_remaining <= 0

    def get_weekly_value(self):
        """Estimate the contract's average weekly value."""
        return self.pay_per_show + self.downside_guarantee

    def to_dict(self):
        return self.__dict__.copy()

    @classmethod
    def from_dict(cls, data):
        return cls(**data)

    def __str__(self):
        excl = "Exclusive" if self.exclusive else "Non-Exclusive"
        return (
            f"Contract with {self.promotion_id}: ${self.pay_per_show}/show, "
            f"{self.weeks_remaining}wk remaining ({excl})"
        )


# ---------------------------------------------------------------------------
# Contract generation / offer logic
# ---------------------------------------------------------------------------

def _base_offer(promotion):
    """Generate a baseline contract offer from a promotion.

    Parameters
    ----------
    promotion : Promotion

    Returns
    -------
    Contract
    """
    duration_ranges = {
        1: (8, 16),
        2: (12, 26),
        3: (26, 52),
        4: (52, 156),  # 1–3 years
    }
    lo, hi = duration_ranges.get(promotion.tier, (12, 52))
    weeks = random.randint(lo, hi)

    pay = random.randint(promotion.pay_min, max(promotion.pay_max, promotion.pay_min + 1))

    exclusive = promotion.tier >= 3
    title_shot = False
    downside = 0
    merch = 0.0
    creative = False
    no_compete = 0
    bonus = 0

    if promotion.tier >= 3:
        downside = pay // 4
        merch = random.uniform(0.02, 0.10)
        no_compete = random.randint(4, 13)

    if promotion.tier >= 4:
        downside = pay // 3
        merch = random.uniform(0.05, 0.20)
        no_compete = random.randint(13, 39)
        bonus = random.randint(500, 5000) * promotion.tier

    return Contract(
        promotion_id=promotion.id,
        weeks_duration=weeks,
        pay_per_show=pay,
        exclusive=exclusive,
        title_shot_clause=title_shot,
        downside_guarantee=downside,
        merchandise_cut=round(merch, 3),
        creative_control=creative,
        no_compete_weeks=no_compete,
        signing_bonus=bonus,
    )


def generate_offer(promotion, wrestler):
    """Generate a contract offer from a promotion to a wrestler.

    The offer is adjusted based on the wrestler's popularity,
    overall rating, and backstage reputation.

    Parameters
    ----------
    promotion : Promotion
    wrestler : Wrestler

    Returns
    -------
    Contract
    """
    offer = _base_offer(promotion)

    # --- Adjust pay based on wrestler value ---
    overall = wrestler.get_overall_rating()
    pop = wrestler.popularity

    # Popularity multiplier (1.0–2.5)
    pop_mult = 1.0 + (pop / 100) * 1.5

    # Overall rating multiplier (0.8–1.8)
    ovr_mult = 0.8 + (overall / 100) * 1.0

    combined = (pop_mult + ovr_mult) / 2
    offer.pay_per_show = int(offer.pay_per_show * combined)
    offer.downside_guarantee = int(offer.downside_guarantee * combined)
    offer.signing_bonus = int(offer.signing_bonus * combined)

    # High-value wrestlers may get a title shot clause
    if overall >= 70 and pop >= 50:
        offer.title_shot_clause = random.random() < 0.3

    # Stars get better merch deals
    if pop >= 60:
        offer.merchandise_cut = min(0.30, offer.merchandise_cut * 1.5)

    return offer


# ---------------------------------------------------------------------------
# Negotiation system
# ---------------------------------------------------------------------------

class Negotiation:
    """Handles back-and-forth contract negotiation between player and promotion.

    The player can request changes; the promotion accepts, counters,
    or walks away based on the wrestler's leverage.
    """

    MAX_ROUNDS = 5

    def __init__(self, promotion, wrestler, initial_offer=None):
        self.promotion = promotion
        self.wrestler = wrestler
        self.current_offer = initial_offer or generate_offer(promotion, wrestler)
        self.round = 0
        self.concluded = False
        self.accepted = False
        self._calculate_leverage()

    def _calculate_leverage(self):
        """Determine how much negotiating power the wrestler has (0.0–1.0)."""
        pop = self.wrestler.popularity
        overall = self.wrestler.get_overall_rating()
        rep = self.wrestler.backstage_rep

        # Base leverage from popularity and skill
        self.leverage = (pop * 0.5 + overall * 0.3 + (rep + 100) * 0.1) / 100
        self.leverage = max(0.05, min(1.0, self.leverage))

    def request_more_pay(self, amount):
        """Player asks for a higher per-show pay.

        Parameters
        ----------
        amount : int
            The pay amount the player wants.

        Returns
        -------
        dict
            Result with 'accepted', 'counter', or 'walked_away'.
        """
        return self._negotiate("pay_per_show", amount)

    def request_title_shot(self):
        """Player requests a title shot clause."""
        if self.current_offer.title_shot_clause:
            return {"accepted": True, "message": "Already included in the offer."}
        return self._negotiate_bool("title_shot_clause")

    def request_creative_control(self):
        """Player requests creative control."""
        if self.current_offer.creative_control:
            return {"accepted": True, "message": "Already included in the offer."}
        return self._negotiate_bool("creative_control")

    def request_no_exclusive(self):
        """Player asks to remove the exclusivity clause."""
        if not self.current_offer.exclusive:
            return {"accepted": True, "message": "Contract is already non-exclusive."}
        return self._negotiate_bool("exclusive", desired_value=False)

    def request_shorter_no_compete(self, weeks):
        """Player asks for a shorter no-compete period."""
        return self._negotiate("no_compete_weeks", weeks, lower_is_better=True)

    def request_signing_bonus(self, amount):
        """Player asks for a signing bonus."""
        return self._negotiate("signing_bonus", amount)

    def request_more_merch(self, percentage):
        """Player asks for a bigger merchandise cut (pass as 0.0–1.0)."""
        return self._negotiate("merchandise_cut", percentage)

    def accept_offer(self):
        """Player accepts the current offer."""
        self.concluded = True
        self.accepted = True
        return {
            "accepted": True,
            "contract": self.current_offer,
            "message": "You signed the contract!",
        }

    def decline_offer(self):
        """Player walks away entirely."""
        self.concluded = True
        self.accepted = False
        return {
            "accepted": False,
            "message": "You walked away from the negotiation.",
        }

    def _negotiate(self, field, requested, lower_is_better=False):
        """Generic numeric negotiation."""
        if self.concluded:
            return {"accepted": False, "message": "Negotiation is over."}

        self.round += 1
        if self.round > self.MAX_ROUNDS:
            self.concluded = True
            return {
                "accepted": False,
                "walked_away": True,
                "message": f"{self.promotion.short_name} has lost patience and withdrawn the offer.",
            }

        current = getattr(self.current_offer, field)

        if lower_is_better:
            gap = current - requested
        else:
            gap = requested - current

        if gap <= 0:
            return {"accepted": True, "message": "Already meets your request.", "offer": self.current_offer}

        # Chance of acceptance based on leverage and how big the ask is
        relative_ask = gap / max(abs(current), 1)
        accept_chance = self.leverage - (relative_ask * 0.5)
        accept_chance += random.uniform(-0.15, 0.15)

        if accept_chance >= 0.5:
            setattr(self.current_offer, field, requested)
            return {
                "accepted": True,
                "message": f"{self.promotion.short_name} agreed to your terms.",
                "offer": self.current_offer,
            }
        elif accept_chance >= 0.2:
            # Counter offer — split the difference
            if lower_is_better:
                counter = current - int(gap * random.uniform(0.3, 0.6))
            else:
                counter = current + int(gap * random.uniform(0.3, 0.6))
            if isinstance(current, float):
                counter = round(counter, 3)
            else:
                counter = int(counter)
            setattr(self.current_offer, field, counter)
            return {
                "accepted": False,
                "counter": True,
                "message": f"{self.promotion.short_name} countered with {field}={counter}.",
                "offer": self.current_offer,
            }
        else:
            # Rejected, offer stands
            return {
                "accepted": False,
                "counter": False,
                "message": f"{self.promotion.short_name} refused your request.",
                "offer": self.current_offer,
            }

    def _negotiate_bool(self, field, desired_value=True):
        """Negotiate a boolean clause."""
        if self.concluded:
            return {"accepted": False, "message": "Negotiation is over."}

        self.round += 1
        if self.round > self.MAX_ROUNDS:
            self.concluded = True
            return {
                "accepted": False,
                "walked_away": True,
                "message": f"{self.promotion.short_name} has lost patience and withdrawn the offer.",
            }

        accept_chance = self.leverage + random.uniform(-0.2, 0.2)

        # Some clauses are harder to get
        difficulty = {
            "title_shot_clause": -0.15,
            "creative_control": -0.25,
            "exclusive": -0.10,
        }
        accept_chance += difficulty.get(field, 0)

        if accept_chance >= 0.5:
            setattr(self.current_offer, field, desired_value)
            return {
                "accepted": True,
                "message": f"{self.promotion.short_name} agreed to add {field.replace('_', ' ')}.",
                "offer": self.current_offer,
            }
        else:
            return {
                "accepted": False,
                "message": f"{self.promotion.short_name} refused to include {field.replace('_', ' ')}.",
                "offer": self.current_offer,
            }
