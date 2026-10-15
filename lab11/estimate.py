"""Part C: estimate a rare probability honestly. TODO 4, 6 and 7."""
from __future__ import annotations

import math

import numpy as np

from avsim import space
from .search import proposal_logpdf


def wilson_ci(k: int, n: int, z: float = 1.96) -> tuple[float, float]:
    """TODO 4. Wilson score interval for k successes in n trials. Must behave at k = 0 (lower bound 0,
    upper bound > 0) where the plain normal interval collapses to [0, 0]. Return (0, 1) for n = 0."""
    if n < 0 or k < 0 or k > n:
        raise ValueError("Wilson interval requires 0 <= k <= n")
    if n == 0:
        return 0.0, 1.0

    n = float(n)
    # Preserve the exact boundary required for an unobserved event.  The
    # closed-form expression can leave a tiny positive residual after
    # subtraction, which would incorrectly report a nonzero lower bound.
    if k == 0:
        z2 = float(z) ** 2
        return 0.0, z2 / (n + z2)
    z2 = float(z) ** 2
    phat = float(k) / n
    denom = 1.0 + z2 / n
    center = (phat + z2 / (2.0 * n)) / denom
    half = abs(float(z)) * math.sqrt(phat * (1.0 - phat) / n + z2 / (4.0 * n * n)) / denom
    return max(0.0, center - half), min(1.0, center + half)


def log_weights(Z, Bn, nat: space.Natural, prop: dict, beta: float = 0.2) -> np.ndarray:
    """TODO 6. log p(u) - log q(u) for each row, where q is the DEFENSIVE MIXTURE
    q = (1 - beta) * proposal + beta * natural.

    nat.logpdf(Z, Bn) gives log p; proposal_logpdf(prop, Z, Bn) gives log of the CEM proposal.
    Use np.logaddexp so a weight of 1e-30 does not underflow to 0."""
    if not 0.0 <= beta <= 1.0:
        raise ValueError("beta must be between 0 and 1")
    log_p = np.asarray(nat.logpdf(Z, Bn), dtype=float)
    log_proposal = np.asarray(proposal_logpdf(prop, Z, Bn), dtype=float)
    # log((1-beta) * proposal + beta * natural), evaluated without forming
    # either potentially tiny density in ordinary probability space.
    if beta == 0.0:
        log_q = log_proposal
    elif beta == 1.0:
        log_q = log_p
    else:
        log_q = np.logaddexp(np.log1p(-beta) + log_proposal, np.log(beta) + log_p)
    return log_p - log_q


def is_estimate(logw: np.ndarray, y: np.ndarray, z: float = 1.96) -> dict:
    """TODO 7. Importance-sampling estimate of P(y = 1) under the natural distribution.

    w = exp(logw); p = mean(w * y)  (NOT normalised by sum(w): that version is biased for small n);
    se = std(w * y, ddof=1) / sqrt(n); CI = [max(0, p - z se), p + z se];
    Kish effective sample size ess = (sum w)^2 / sum(w^2).
    Return dict(p=, lo=, hi=, se=, ess=, n=)."""
    logw = np.asarray(logw, dtype=float).reshape(-1)
    y = np.asarray(y, dtype=float).reshape(-1)
    if logw.shape != y.shape:
        raise ValueError("logw and y must have the same length")
    n = int(y.size)
    if n == 0:
        # No observations provide no useful interval or effective sample size.
        return dict(p=0.0, lo=0.0, hi=1.0, se=0.0, ess=0.0, n=0)

    w = np.exp(logw)
    wy = w * y
    p = float(np.mean(wy))
    if n > 1:
        se = float(np.std(wy, ddof=1) / math.sqrt(n))
        lo = max(0.0, p - float(z) * se)
        hi = p + float(z) * se
    else:
        # A sample variance needs at least two draws. Keep the reported interval
        # uninformative instead of implying certainty from a single observation.
        se = 0.0
        lo, hi = 0.0, 1.0

    # Scale before squaring to avoid overflow; this ratio is invariant to a common
    # scale factor and is exactly Kish's (sum w)^2 / sum(w^2).
    finite = np.isfinite(logw)
    if np.any(finite):
        scaled_w = np.exp(logw[finite] - np.max(logw[finite]))
        sum_w = float(np.sum(scaled_w))
        sum_w2 = float(np.sum(scaled_w * scaled_w))
        ess = sum_w * sum_w / sum_w2 if sum_w2 > 0.0 else 0.0
    else:
        ess = 0.0
    return dict(p=p, lo=float(lo), hi=float(hi), se=se, ess=float(ess), n=n)


def rule_of_three(n_eff: float) -> float:
    """Given: 95% upper bound on a probability when 0 events were seen in n_eff independent tries."""
    return 3.0 / max(n_eff, 1.0)
