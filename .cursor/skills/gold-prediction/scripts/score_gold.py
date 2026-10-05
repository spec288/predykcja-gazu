#!/usr/bin/env python3
"""Quant scoring for gold 1D/1W. Stdlib only. See ../SKILL.md and ../factors.md."""
from __future__ import annotations

import argparse
import json
import math
import statistics
import sys
import urllib.error
import urllib.request
from datetime import datetime, timezone
from typing import Any

YAHOO = "https://query1.finance.yahoo.com/v8/finance/chart/{ticker}?interval=1d&range={rng}"
FRED = "https://fred.stlouisfed.org/graph/fredgraph.csv?id={sid}"
UA = "Mozilla/5.0 (compatible; gold-prediction-skill/1.0)"

WEIGHTS_1D = {
    "R1": {"A": 0.36, "B": 0.26, "C": 0.12, "D": 0.10, "E": 0.08, "F": 0.05, "G": 0.03},
    "R2": {"A": 0.30, "B": 0.26, "C": 0.14, "D": 0.10, "E": 0.10, "F": 0.05, "G": 0.05},
    "R3": {"A": 0.18, "B": 0.22, "C": 0.12, "D": 0.16, "E": 0.24, "F": 0.03, "G": 0.05},
}
WEIGHTS_1W = {
    "R1": {"A": 0.42, "B": 0.16, "C": 0.10, "D": 0.14, "E": 0.08, "F": 0.04, "G": 0.06},
    "R2": {"A": 0.36, "B": 0.16, "C": 0.14, "D": 0.16, "E": 0.08, "F": 0.03, "G": 0.07},
    "R3": {"A": 0.20, "B": 0.14, "C": 0.14, "D": 0.18, "E": 0.22, "F": 0.04, "G": 0.08},
}
A_INNER = {
    "R1": {"dxy": 0.28, "real": 0.32, "y2": 0.18, "be": 0.12, "fed": 0.10},
    "R2": {"dxy": 0.34, "real": 0.22, "y2": 0.18, "be": 0.16, "fed": 0.10},
    "R3": {"dxy": 0.22, "real": 0.12, "y2": 0.16, "be": 0.10, "fed": 0.40},
}

TICKERS = {
    "gold": "GC=F",
    "dxy": "DX-Y.NYB",
    "silver": "SI=F",
    "oil": "CL=F",
    "tnx": "^TNX",
    "fvx": "^FVX",
    "irx": "^IRX",
    "vix": "^VIX",
    "spx": "^GSPC",
    "gld": "GLD",
    "iau": "IAU",
    "hyg": "HYG",
}


def clip(x: float, lo: float = -2.0, hi: float = 2.0) -> float:
    return max(lo, min(hi, x))


def pct_change(series: list[float], lag: int) -> float | None:
    if len(series) <= lag or series[-1] == 0 or series[-1 - lag] == 0:
        return None
    return (series[-1] / series[-1 - lag] - 1.0) * 100.0


def ema(values: list[float], period: int) -> float | None:
    if len(values) < period:
        return None
    k = 2.0 / (period + 1)
    e = statistics.mean(values[:period])
    for v in values[period:]:
        e = v * k + e * (1 - k)
    return e


def rsi(values: list[float], period: int = 14) -> float | None:
    if len(values) < period + 1:
        return None
    gains, losses = [], []
    for i in range(1, len(values)):
        d = values[i] - values[i - 1]
        gains.append(max(d, 0.0))
        losses.append(max(-d, 0.0))
    avg_g = statistics.mean(gains[-period:])
    avg_l = statistics.mean(losses[-period:])
    if avg_l == 0:
        return 100.0
    rs = avg_g / avg_l
    return 100.0 - (100.0 / (1.0 + rs))


def atr_pct(high: list[float], low: list[float], close: list[float], period: int = 14) -> float | None:
    if len(close) < period + 1:
        return None
    trs = []
    for i in range(1, len(close)):
        tr = max(high[i] - low[i], abs(high[i] - close[i - 1]), abs(low[i] - close[i - 1]))
        trs.append(tr)
    if len(trs) < period:
        return None
    atr = statistics.mean(trs[-period:])
    return (atr / close[-1]) * 100.0 if close[-1] else None


def streak(close: list[float]) -> tuple[int, str]:
    if len(close) < 2:
        return 0, "flat"
    sign = 1 if close[-1] > close[-2] else (-1 if close[-1] < close[-2] else 0)
    if sign == 0:
        return 0, "flat"
    n = 1
    for i in range(len(close) - 2, 0, -1):
        d = close[i] - close[i - 1]
        s = 1 if d > 0 else (-1 if d < 0 else 0)
        if s != sign:
            break
        n += 1
    return n, ("up" if sign > 0 else "down")


def pearson(a: list[float], b: list[float]) -> float | None:
    if len(a) != len(b) or len(a) < 10:
        return None
    ma, mb = statistics.mean(a), statistics.mean(b)
    num = sum((x - ma) * (y - mb) for x, y in zip(a, b))
    da = math.sqrt(sum((x - ma) ** 2 for x in a))
    db = math.sqrt(sum((y - mb) ** 2 for y in b))
    if da == 0 or db == 0:
        return None
    return num / (da * db)


def http_get(url: str, timeout: int = 12) -> bytes:
    req = urllib.request.Request(url, headers={"User-Agent": UA})
    with urllib.request.urlopen(req, timeout=timeout) as resp:
        return resp.read()


def yahoo_ohlcv(ticker: str, rng: str = "1y") -> dict[str, Any]:
    raw = json.loads(http_get(YAHOO.format(ticker=urllib.request.quote(ticker), rng=rng)))
    result = raw["chart"]["result"][0]
    ts = result["timestamp"]
    q = result["indicators"]["quote"][0]
    adj = result["indicators"].get("adjclose", [{}])[0].get("adjclose")
    out = {"t": ts, "o": q["open"], "h": q["high"], "l": q["low"], "c": q["close"], "v": q.get("volume")}
    if adj:
        out["c"] = adj
    # drop nulls
    keep = [i for i in range(len(out["c"])) if out["c"][i] is not None]
    for k in list(out):
        out[k] = [out[k][i] for i in keep]
    return out


def fred_series(sid: str) -> tuple[list[str], list[float]]:
    text = http_get(FRED.format(sid=sid)).decode("utf-8", errors="replace")
    dates, vals = [], []
    for line in text.splitlines()[1:]:
        if "," not in line:
            continue
        d, v = line.strip().split(",", 1)
        v = v.strip()
        if v in ("", ".", "NA"):
            continue
        try:
            vals.append(float(v))
            dates.append(d)
        except ValueError:
            continue
    return dates, vals


def score_dxy(delta: float | None, daily: bool) -> float:
    if delta is None:
        return 0.0
    if daily:
        th = [(-0.50, 2), (-0.20, 1), (0.20, 0), (0.50, -1)]
    else:
        th = [(-1.20, 2), (-0.40, 1), (0.40, 0), (1.20, -1)]
    if delta <= th[0][0]:
        return float(th[0][1])
    if delta <= th[1][0]:
        return float(th[1][1])
    if delta < th[2][0]:
        return 0.0
    if delta < th[3][0]:
        return -1.0
    return -2.0


def score_bp(delta_bp: float | None, daily: bool, invert: bool = True) -> float:
    """Yield/real-yield: up = bearish gold when invert=True. BE: invert=False."""
    if delta_bp is None:
        return 0.0
    if daily:
        cuts = [(-8, 2), (-3, 1), (3, 0), (8, -1)]
    else:
        cuts = [(-20, 2), (-8, 1), (8, 0), (20, -1)]
    if delta_bp <= cuts[0][0]:
        s = float(cuts[0][1])
    elif delta_bp <= cuts[1][0]:
        s = float(cuts[1][1])
    elif delta_bp < cuts[2][0]:
        s = 0.0
    elif delta_bp < cuts[3][0]:
        s = -1.0
    else:
        s = -2.0
    return s if invert else -s


def score_flow(pct: float | None) -> float:
    if pct is None:
        return 0.0
    if pct >= 0.50:
        return 2.0
    if pct >= 0.15:
        return 1.0
    if pct <= -0.50:
        return -2.0
    if pct <= -0.15:
        return -1.0
    return 0.0


def map_bias(score: float, n_agree: int, event: bool, regime: str) -> dict[str, str]:
    mag = abs(score)
    if event:
        return {"bias": "NEUTRAL", "conviction": "PASS"}
    if mag < 0.15:
        return {"bias": "NEUTRAL", "conviction": "PASS"}
    sign = "LONG" if score > 0 else "SHORT"
    if mag >= 0.45 and n_agree >= 3 and not (regime == "R3" and score > 0):
        conv = "HIGH"
    elif mag >= 0.30:
        conv = "MED"
    else:
        conv = "LOW"
    if regime == "R3" and score > 0 and conv == "HIGH":
        conv = "MED"
    return {"bias": sign if mag >= 0.15 else "NEUTRAL", "conviction": conv}


def last_delta(vals: list[float], lag: int) -> float | None:
    if len(vals) <= lag:
        return None
    return vals[-1] - vals[-1 - lag]


def aligned_returns(a_t: list[int], a_c: list[float], b_t: list[int], b_c: list[float], n: int = 60) -> tuple[list[float], list[float]]:
    amap = {t: c for t, c in zip(a_t, a_c)}
    bmap = {t: c for t, c in zip(b_t, b_c)}
    common = sorted(set(amap) & set(bmap))
    if len(common) < n + 1:
        n = max(10, len(common) - 1)
    common = common[-(n + 1) :]
    ra, rb = [], []
    for i in range(1, len(common)):
        p, q = common[i - 1], common[i]
        if amap[p] and bmap[p]:
            ra.append(math.log(amap[q] / amap[p]))
            rb.append(bmap[q] - bmap[p])
    return ra, rb


def collect() -> dict[str, Any]:
    gaps: list[str] = []
    data: dict[str, Any] = {}
    for name, ticker in TICKERS.items():
        try:
            data[name] = yahoo_ohlcv(ticker)
        except Exception as exc:  # noqa: BLE001
            gaps.append(f"{name}:{exc.__class__.__name__}")
            data[name] = None
    fred: dict[str, list[float]] = {}
    for sid in ("DFII10", "T5YIE", "DGS2", "DGS10", "T10Y2Y", "BAMLH0A0HYM2"):
        try:
            _, vals = fred_series(sid)
            fred[sid] = vals
        except Exception as exc:  # noqa: BLE001
            gaps.append(f"fred:{sid}:{exc.__class__.__name__}")
            fred[sid] = []
    return {"yahoo": data, "fred": fred, "gaps": gaps}


def score_all(pack: dict[str, Any], event: bool) -> dict[str, Any]:
    y = pack["yahoo"]
    fred = pack["fred"]
    gaps: list[str] = list(pack["gaps"])
    gold = y.get("gold")
    if not gold or len(gold["c"]) < 30:
        raise SystemExit("brak serii gold (GC=F)")

    g_c, g_h, g_l = gold["c"], gold["h"], gold["l"]
    spot = g_c[-1]
    atrp = atr_pct(g_h, g_l, g_c) or 1.0
    e20 = ema(g_c, 20)
    e50 = ema(g_c, 50)
    e200 = ema(g_c, 200)
    r14 = rsi(g_c)
    n_streak, side = streak(g_c)
    r1 = pct_change(g_c, 1)
    r5 = pct_change(g_c, 5)
    r20 = pct_change(g_c, 20)

    dxy_c = y["dxy"]["c"] if y.get("dxy") else []
    dxy_1 = pct_change(dxy_c, 1) if dxy_c else None
    dxy_5 = pct_change(dxy_c, 5) if dxy_c else None

    real = fred.get("DFII10") or []
    be = fred.get("T5YIE") or []
    dgs2 = fred.get("DGS2") or []
    hy = fred.get("BAMLH0A0HYM2") or []
    t10y2y = fred.get("T10Y2Y") or []

    # fallback real ≈ 10Y - 5Y BE using Yahoo TNX (percent) if FRED empty
    if len(real) < 5 and y.get("tnx") and be:
        tnx = y["tnx"]["c"]
        # cannot perfectly align; skip
    def pct_to_bp(vals: list[float], lag: int) -> float | None:
        d = last_delta(vals, lag)
        return None if d is None else d * 100.0

    real_1 = pct_to_bp(real, 1)
    real_5 = pct_to_bp(real, 5)
    be_1 = pct_to_bp(be, 1)
    be_5 = pct_to_bp(be, 5)
    y2_1 = pct_to_bp(dgs2, 1)
    y2_5 = pct_to_bp(dgs2, 5)
    if y2_1 is None and y.get("irx") and len(y["irx"]["c"]) > 5:
        y2_1 = pct_to_bp(y["irx"]["c"], 1)
        y2_5 = pct_to_bp(y["irx"]["c"], 5)
        gaps.append("y2:fallback_IRX")

    # regime
    regime = "R2"
    hy_last = hy[-1] if hy else None
    gold_down = (r1 or 0) < -0.3
    vix_last = y["vix"]["c"][-1] if y.get("vix") and y["vix"]["c"] else None
    if hy_last is not None and hy_last > 6.0 and gold_down:
        regime = "R3"
    elif event:
        regime = "R4"
    else:
        if gold and real and y.get("dxy"):
            # corr gold logret vs Δ real (60d) — use FRED last 60 vs gold last 60 poorly aligned
            # proxy: Yahoo TNX vs gold if DFII short
            pass
        tnx = y["tnx"]["c"] if y.get("tnx") else []
        if len(g_c) > 61 and len(tnx) > 61:
            # align by index tail (both daily, close enough)
            n = 60
            g_ret = [math.log(g_c[-n + i] / g_c[-n + i - 1]) for i in range(1, n)]
            y_ret = [tnx[-n + i] - tnx[-n + i - 1] for i in range(1, n)]
            corr = pearson(g_ret, y_ret)
            if corr is not None and corr <= -0.40:
                regime = "R1"

    if event:
        regime_w = "R2"  # weights unused; gate later
        regime_out = "R4"
    else:
        regime_w = regime if regime in ("R1", "R2", "R3") else "R2"
        regime_out = regime_w

    real_mult = 0.55 if regime_w == "R2" else 1.0
    a_w = A_INNER[regime_w]

    a_dxy_1 = score_dxy(dxy_1, True)
    a_dxy_5 = score_dxy(dxy_5, False)
    a_real_1 = score_bp(real_1, True) * real_mult
    a_real_5 = score_bp(real_5, False) * real_mult
    a_y2_1 = score_bp(y2_1, True)
    a_y2_5 = score_bp(y2_5, False)
    a_be_1 = score_bp(be_1, True, invert=False)
    a_be_5 = score_bp(be_5, False, invert=False)
    a_fed = 0.0  # overlay — no FedWatch in stdlib fetch

    A_1d = clip(
        a_w["dxy"] * a_dxy_1
        + a_w["real"] * a_real_1
        + a_w["y2"] * a_y2_1
        + a_w["be"] * a_be_1
        + a_w["fed"] * a_fed
    )
    A_1w = clip(
        a_w["dxy"] * a_dxy_5
        + a_w["real"] * a_real_5
        + a_w["y2"] * a_y2_5
        + a_w["be"] * a_be_5
        + a_w["fed"] * a_fed
    )
    if t10y2y and t10y2y[-1] < 0:
        A_1w = clip(A_1w + 0.5)

    # B technical
    struct = 0.0
    if e20:
        if g_c[-1] > e20:
            struct += 1.0
        else:
            struct -= 1.0
    pdh = g_h[-2] if len(g_h) >= 2 else None
    pdl = g_l[-2] if len(g_l) >= 2 else None
    if pdh and g_c[-1] > pdh:
        struct += 1.0
    if pdl and g_c[-1] < pdl:
        struct -= 1.0
    struct = clip(struct)

    mom = 0.0
    if r14 is not None:
        if r14 < 30 and side == "down" and n_streak >= 3:
            mom += 1.0
        elif r14 > 70 and side == "up" and n_streak >= 3:
            mom -= 0.5
    if r1 is not None and r1 > 0.6:
        mom += 0.5
    if r1 is not None and r1 < -0.6:
        mom -= 0.5
    mom = clip(mom)

    markov = 0.0
    if side == "down" and n_streak >= 4:
        markov = 2.0
    elif side == "down" and n_streak >= 3:
        markov = 1.0
    elif side == "up" and n_streak >= 5:
        markov = -1.0
    elif side == "up" and n_streak >= 3:
        markov = -1.0

    dist200 = 0.0
    if e200:
        dist200 = 0.5 if g_c[-1] > e200 else -0.5

    B_1d = clip(0.35 * struct + 0.25 * mom + 0.20 * markov + 0.10 * 0.0 + 0.10 * dist200)

    weekly_struct = 0.0
    if e20 and e50:
        if g_c[-1] > e20 and g_c[-1] > e50 and (r5 or 0) > 0:
            weekly_struct = 1.5 if (r20 or 0) > 0 else 1.0
        elif g_c[-1] < e20 and g_c[-1] < e50 and (r5 or 0) < 0:
            weekly_struct = -1.5 if (r20 or 0) < 0 else -1.0
    # monthly up streak
    monthly_mr = 0.0
    if len(g_c) >= 90:
        months = []
        # approx 21d blocks
        for k in range(1, 5):
            if len(g_c) > 21 * k:
                months.append(g_c[-1] > g_c[-1 - 21] if k == 1 else g_c[-1 - 21 * (k - 1)] > g_c[-1 - 21 * k])
        up_m = 0
        for m in months:
            if m:
                up_m += 1
            else:
                break
        if up_m >= 4:
            monthly_mr = -2.0
        elif up_m >= 3:
            monthly_mr = -1.0

    B_1w = clip(0.40 * weekly_struct + 0.25 * (1.0 if (r5 or 0) > 0 else (-1.0 if (r5 or 0) < 0 else 0)) + 0.20 * monthly_mr)

    # C sentiment placeholder 0 — overlay
    C_1d = 0.0
    C_1w = 0.0

    # D flows: GLD+IAU volume-less — use close*proxy via pct of price? Better: volume spike is not flow.
    # Use 1d/5d GLD return as weak proxy only if holdings unavailable → mark gap.
    gld_1 = pct_change(y["gld"]["c"], 1) if y.get("gld") else None
    gld_5 = pct_change(y["gld"]["c"], 5) if y.get("gld") else None
    # Without shares outstanding, do not pretend ETF flow. Neutral + gap.
    D_1d = 0.0
    D_1w = 0.0
    gaps.append("flows:GLD_shares_not_in_yahoo_chart")

    # E cross
    si_1 = pct_change(y["silver"]["c"], 1) if y.get("silver") else None
    si_5 = pct_change(y["silver"]["c"], 5) if y.get("silver") else None
    oil_px = y["oil"]["c"][-1] if y.get("oil") and y["oil"]["c"] else None
    oil_5 = pct_change(y["oil"]["c"], 5) if y.get("oil") else None
    hyg_1 = pct_change(y["hyg"]["c"], 1) if y.get("hyg") else None
    spx_1 = pct_change(y["spx"]["c"], 1) if y.get("spx") else None

    E_1d = 0.0
    if si_1 is not None and r1 is not None:
        if si_1 * r1 > 0:
            E_1d += 0.5 if abs(si_1) > 0.3 else 0.25
        else:
            E_1d -= 0.5
    if hyg_1 is not None and hyg_1 < -1.5:
        E_1d -= 1.0  # credit stress selloff risk 1d
    if spx_1 is not None and spx_1 < -2.0 and (r1 or 0) < 0:
        E_1d -= 1.0  # R3-ish
    E_1d = clip(E_1d)

    E_1w = 0.0
    if si_5 is not None and r5 is not None:
        E_1w += 0.5 if si_5 * r5 > 0 else -0.5
    if hy_last is not None and hy_last > 6:
        E_1w += 1.0
    if oil_5 is not None and oil_5 <= -8.0 and (r5 or 0) >= 0:
        E_1w += 0.5
    E_1w = clip(E_1w)

    # F calendar
    now = datetime.now(timezone.utc)
    dow = now.weekday()  # 0 Mon
    month = now.month
    F_1d = 0.5 if dow == 4 else (-0.5 if dow == 0 else 0.0)
    F_1w = 0.5 if month in (1, 8) else (-0.5 if month in (5, 6, 9) else 0.0)

    G_1d = 0.0
    G_1w = 0.0
    gaps.append("sge_premium:manual")

    groups_1d = {"A": A_1d, "B": B_1d, "C": C_1d, "D": D_1d, "E": E_1d, "F": F_1d, "G": G_1d}
    groups_1w = {"A": A_1w, "B": B_1w, "C": C_1w, "D": D_1w, "E": E_1w, "F": F_1w, "G": G_1w}

    w1d = WEIGHTS_1D[regime_w]
    w1w = WEIGHTS_1W[regime_w]
    s1d = sum(w1d[k] * groups_1d[k] for k in w1d)
    s1w = sum(w1w[k] * groups_1w[k] for k in w1w)

    def agree(groups: dict[str, float]) -> int:
        signs = [1 if v > 0.15 else (-1 if v < -0.15 else 0) for k, v in groups.items() if k != "F"]
        pos = sum(1 for x in signs if x > 0)
        neg = sum(1 for x in signs if x < 0)
        return max(pos, neg)

    n1d, n1w = agree(groups_1d), agree(groups_1w)
    m1d = map_bias(s1d, n1d, event, regime_out)
    m1w = map_bias(s1w, n1w, False, regime_out)  # 1W not fully gated
    if event:
        m1w["conviction"] = "LOW" if m1w["conviction"] == "HIGH" else m1w["conviction"]
        if m1w["conviction"] == "MED":
            pass
        if m1w["conviction"] == "HIGH":
            m1w["conviction"] = "MED"

    def band(k: float) -> dict[str, float]:
        width = atrp * k / 100.0
        return {
            "low": round(spot * (1 - width), 2),
            "high": round(spot * (1 + width), 2),
            "mid": round(spot * math.exp(s1d * 0.15 * atrp / 100.0) if k < 1.5 else spot * math.exp(s1w * 0.15 * atrp * math.sqrt(5) / 100.0), 2),
        }

    k_d = 2.0 if event or regime_out == "R3" else 1.15
    k_w = 2.2 if regime_out == "R3" else 1.9
    b1d = band(k_d)
    # fix 1w mid
    width_w = atrp * math.sqrt(5) * (1.1 if regime_out != "R3" else 1.4) / 100.0
    b1w = {
        "low": round(spot * (1 - width_w), 2),
        "high": round(spot * (1 + width_w), 2),
        "mid": round(spot * math.exp(clip(s1w) * 0.20 * atrp * math.sqrt(5) / 100.0), 2),
    }

    return {
        "asof_utc": now.strftime("%Y-%m-%dT%H:%M:%SZ"),
        "spot": round(spot, 2),
        "atr_pct": round(atrp, 3),
        "atr_usd": round(spot * atrp / 100.0, 2),
        "regime": regime_out,
        "event_gate": event,
        "data_gaps": gaps,
        "tape": {
            "gold_1d_pct": None if r1 is None else round(r1, 3),
            "gold_5d_pct": None if r5 is None else round(r5, 3),
            "dxy_1d_pct": None if dxy_1 is None else round(dxy_1, 3),
            "dxy_5d_pct": None if dxy_5 is None else round(dxy_5, 3),
            "real_yield_1d_bp": None if real_1 is None else round(real_1, 1),
            "real_yield_5d_bp": None if real_5 is None else round(real_5, 1),
            "dgs2_1d_bp": None if y2_1 is None else round(y2_1, 1),
            "breakeven_1d_bp": None if be_1 is None else round(be_1, 1),
            "hy_oas": hy_last,
            "vix": vix_last,
            "rsi14": None if r14 is None else round(r14, 1),
            "ema20": None if e20 is None else round(e20, 2),
            "ema50": None if e50 is None else round(e50, 2),
            "ema200": None if e200 is None else round(e200, 2),
            "streak": f"{n_streak} {side}",
            "gold_oil": None if not oil_px else round(spot / oil_px, 2),
            "oil_5d_pct": None if oil_5 is None else round(oil_5, 3),
            "silver_1d_pct": None if si_1 is None else round(si_1, 3),
            "t10y2y": t10y2y[-1] if t10y2y else None,
            "dow": ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"][dow],
        },
        "quant_1d": {
            "groups": {k: round(v, 3) for k, v in groups_1d.items()},
            "composite": round(s1d, 3),
            "agree": n1d,
            **m1d,
            "band": b1d,
            "note": "overlay C/D/G/Fed path = 0; merge 0.70*quant+0.30*overlay",
        },
        "quant_1w": {
            "groups": {k: round(v, 3) for k, v in groups_1w.items()},
            "composite": round(s1w, 3),
            "agree": n1w,
            **m1w,
            "band": b1w,
            "note": "overlay C/D/G/Fed/COT/SGE = 0; merge 0.55*quant+0.45*overlay",
        },
        "weights_used": {"1d": w1d, "1w": w1w, "A_inner": a_w},
    }


def main() -> None:
    p = argparse.ArgumentParser(description="Gold 1D/1W quant score")
    p.add_argument("--event", action="store_true", help="CPI/NFP/FOMC/Powell within 24h")
    p.add_argument("--pretty", action="store_true")
    args = p.parse_args()
    pack = collect()
    out = score_all(pack, event=args.event)
    dump = json.dumps(out, indent=2 if args.pretty else None)
    sys.stdout.write(dump + "\n")


if __name__ == "__main__":
    main()
