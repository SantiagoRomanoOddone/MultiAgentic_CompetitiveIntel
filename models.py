from dataclasses import dataclass
from typing import Optional


@dataclass
class PriceEvent:
    ean: str
    product_name: str
    brand: str
    chain: str
    branch_id: str
    city: str
    date: str
    list_price: float
    promo_price: Optional[float]
    previous_price: Optional[float]

    @property
    def price_change_pct(self) -> Optional[float]:
        if self.previous_price and self.previous_price > 0:
            return ((self.list_price - self.previous_price) / self.previous_price) * 100
        return None

    @property
    def is_on_promo(self) -> bool:
        return self.promo_price is not None and self.promo_price < self.list_price


@dataclass
class AnalyzedEvent(PriceEvent):
    context: str = ""


@dataclass
class ScoredAlert(AnalyzedEvent):
    urgency_score: int = 0      # 1–10
    alert_type: str = ""        # price_increase / price_drop / promotion_start / competitor_move / srp_violation
    reasoning: str = ""


@dataclass
class ActionRecommendation(ScoredAlert):
    action: str = ""            # reprice / notify_account_manager / escalate / monitor
    message: str = ""
