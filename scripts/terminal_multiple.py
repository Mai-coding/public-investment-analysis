#!/usr/bin/env python3
"""Zero-weight finite-horizon references, with separate terminal cash.

All amounts use a common currency/unit. Distributions FV is per CURRENT share;
terminal totals divided by future diluted shares capture financing and buybacks.
An explicit zero distribution is an assumption, not a missing-data fallback.
Terminal cash is a company total; it is never an intermediate dividend.
"""
from __future__ import annotations

import math
from dataclasses import dataclass


METRICS = {"P/E", "P/S", "P/B", "P/TBV", "P/AFFO", "P/NAV"}


def _finite(name: str, value: float, *, positive: bool = False, signed: bool = False) -> float:
    if not isinstance(value, (int, float)) or isinstance(value, bool) or not math.isfinite(value):
        raise ValueError(f"{name} must be finite")
    if (not signed and value < 0) or (positive and value <= 0):
        raise ValueError(f"{name} must be {'positive' if positive else 'nonnegative'}")
    return float(value)


@dataclass(frozen=True)
class TerminalCase:
    metric: str
    terminal_total: float
    terminal_shares: float
    exit_multiple: float
    horizon: float
    required_return: float
    distributions_fv: float
    terminal_cash: float = 0.0
    cash_treatment: str = "Included"

    def __post_init__(self) -> None:
        if self.metric not in METRICS:
            raise ValueError(f"unsupported equity multiple: {self.metric}")
        for name in ("terminal_total", "required_return", "distributions_fv"):
            _finite(name, getattr(self, name))
        for name in ("terminal_shares", "exit_multiple", "horizon"):
            _finite(name, getattr(self, name), positive=True)
        _finite("terminal_cash", self.terminal_cash, signed=True)
        if self.cash_treatment not in {"Included", "Separate"}:
            raise ValueError("Cash Treatment must be Included or Separate")
        if self.cash_treatment == "Included" and self.terminal_cash != 0:
            raise ValueError("Included cash must not be added again as Terminal Cash")
        _finite("terminal equity value", self.terminal_equity_value)
        _finite("return factor", self.factor, positive=True)

    @property
    def factor(self) -> float:
        return (1 + self.required_return) ** self.horizon

    @property
    def terminal_equity_value(self) -> float:
        return self.terminal_total * self.exit_multiple + self.terminal_cash

    @property
    def terminal_price(self) -> float:
        return self.terminal_equity_value / self.terminal_shares

    @property
    def supported_price(self) -> float:
        return (self.terminal_price + self.distributions_fv) / self.factor

    def implied_total(self, current_price: float) -> float:
        """Conditional requirement; cash and distributions have distinct units."""
        _finite("current_price", current_price, positive=True)
        required_equity = (current_price * self.factor - self.distributions_fv) * self.terminal_shares
        return max(0.0, required_equity - self.terminal_cash) / self.exit_multiple

    def expected_cagr(self, current_price: float) -> float:
        """Total-wealth CAGR under the explicitly supplied distribution FV."""
        _finite("current_price", current_price, positive=True)
        return ((self.terminal_price + self.distributions_fv) / current_price) ** (1 / self.horizon) - 1


def distributions_future_value(distributions: list[tuple[float, float]], horizon: float,
                               reinvestment_rate: float) -> float:
    """Explicit reinvestment convention; amounts are per current share."""
    _finite("horizon", horizon, positive=True)
    _finite("reinvestment_rate", reinvestment_rate)
    total = 0.0
    for year, amount in distributions:
        _finite("distribution year", year)
        _finite("distribution amount", amount)
        if year > horizon:
            raise ValueError("distribution cannot occur after horizon")
        total += amount * (1 + reinvestment_rate) ** (horizon - year)
    return total


def mature_ps(mature_pe: float, net_margin: float) -> float:
    _finite("mature_pe", mature_pe, positive=True)
    _finite("net_margin", net_margin, positive=True)
    if net_margin > 1:
        raise ValueError("sustainable net_margin must not exceed 100%")
    return mature_pe * net_margin


def central_valuation(forward_comps: float) -> float:
    """Central valuation is100% forward comps; terminal is not an input."""
    return _finite('forward_comps', forward_comps)
