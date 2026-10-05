# Rubryki scoringu (−2 … +2)

Każdy czynnik: `−2` silnie bearish, `−1` bearish, `0` neutral, `+1` bullish, `+2` silnie bullish. Brak danych = `0` i flaga `data_gap`.

Score grupy = średnia ważona czynników w grupie, clip do [−2, 2].

Composite = Σ (waga_grupy × score_grupy). Mapowanie:

| |composite| | Bias | Conviction (jeśli confluence OK) |
|---|---|---|
| < 0.15 | NEUTRAL | PASS / LOW |
| 0.15–0.30 | LEAN long/short | LOW |
| 0.30–0.45 | LONG / SHORT | MED |
| ≥ 0.45 | LONG / SHORT | HIGH (tylko gdy ≥3 grupy zgodne i nie R4) |

Pasmo: `mid = spot × exp(k × ATR%)` gdzie k ∈ {−1, −0.4, 0.4, 1} dla low/base; przy R3/R4 użyj 1.8–2.2.

---

## A. Makro-taśma

### A1. DXY (najsilniejszy korelator monthly r ≈ −0.45)

| Δ DXY | 1D score | 1W score (5d Δ) |
|---|---|---|
| ≤ −0.50% / ≤ −1.2% | +2 | +2 |
| −0.49…−0.20 / −1.19…−0.40 | +1 | +1 |
| −0.19…+0.19 / −0.39…+0.39 | 0 | 0 |
| +0.20…+0.49 / +0.40…+1.19 | −1 | −1 |
| ≥ +0.50% / ≥ +1.2% | −2 | −2 |

Asymetria: słaby dolar daje większy upside niż silny dolar downside. Przy DXY i złoto **oba w górę** (kryzys) nie dawaj +2 z samego DXY — sprawdź R3.

Wagi wewnątrz A (R2): DXY 0.34 | real yield 0.22 | 2Y 0.18 | breakeven 0.16 | Fed path 0.10  
Wagi wewnątrz A (R1): DXY 0.28 | real yield 0.32 | 2Y 0.18 | breakeven 0.12 | Fed path 0.10

### A2. Real yield (DFII10; fallback 10Y − 5Y BE)

| Δ 1D / 5D (bp) | score |
|---|---|
| ≤ −8 / ≤ −20 | +2 |
| −7…−3 / −19…−8 | +1 |
| −2…+2 / −7…+7 | 0 |
| +3…+7 / +8…+19 | −1 |
| ≥ +8 / ≥ +20 | −2 |

W R2 mnożnik score A2 × 0.55 (de-coupling). W R1 × 1.0.

### A3. 2Y yield (DGS2) — najczystszy Fed-path tell na 1D

Te same progi bp co A2. Zgodność A2 i A3 wzmacnia; rozjazd (2Y ↑, real ↓) = breakevens ↑ = netto mniej bearish.

### A4. 5Y breakeven (T5YIE)

Gold reaguje na **oczekiwaną** inflację (r ≈ +0.19), nie CPI. Δ BE ≥ +5 bp/d lub +12 bp/5d → +1; ≥ +10 / +25 → +2. Odwrotnie minus.

### A5. Fed path (FedWatch / SOFR)

| Sytuacja | score |
|---|---|
| Dovish repricing ≥ 15 bp na najbliższe 2 posiedzenia | +2 |
| Dovish 5–14 bp | +1 |
| Stabilna ścieżka | 0 |
| Hawkish 5–14 bp | −1 |
| Hawkish ≥ 15 bp lub skip→hike | −2 |

Transmisja: statement → 2Y 8–20 bp → real yields → DXY → złoto. Nie handluj samego słowa „hike/cut”.

### A6. Yield curve (T10Y2Y) — prawie tylko 1W/reżim

Inwersja to **najsilniejszy forward predictor** na 3–24m, nie na 1D. Na 1W: inwersja = +0.5 do grupy A (cap), nie osobny +2.

---

## B. Technika

Potwierdzenie, nie trigger. Nie sumuj RSI+MACD+Stoch+CCI.

### 1D

| Czynnik | waga w B | rubryka |
|---|---:|---|
| Struktura vs PDH/PDL i EMA20 | 0.35 | Close > EMA20 i nad PDH → +1/+2; pod EMA20 i pod PDL → −1/−2; inside = 0 |
| Momentum 1d/3d + RSI(14) | 0.25 | RSI>70 nie jest auto-short. RSI<30 + 3–4 down days → +1 mean-reversion |
| Markov streak | 0.20 | 3–4 down: +1 do +2; 3–4 up: −1; 5+ up: −1 (słaba persystencja) |
| ATR reżim / squeeze | 0.10 | Squeeze + break z makro = wzmocnij znak A; sam squeeze = 0 |
| Dystans do EMA200 | 0.10 | Reżim (bull/bear), nie 1D sygnał. ±0.5 max |

### 1W

| Czynnik | waga w B | rubryka |
|---|---:|---|
| Weekly close vs EMA20/50 | 0.40 | Nad obu + momentum 5d>0 → +1/+2 |
| 5d i 20d return | 0.25 | Zgodne z makro → pełny score; przeciw makro → 0 |
| Weekly RSI / MACD hist | 0.15 | Tylko dywergencja z ceną przy ekstremum |
| 4 up-months | 0.20 | 3–4 kolejne + miesiące: −1/−2 (P(kontynuacja) niska) |

---

## C. Sentyment

LLM/FinBERT > VADER. Negatywne newsy mają większą wagę niż pozytywne (asymetria).

Źródła: Reuters/Bloomberg (twarde), Kitco (narracja, lag), X tylko jako **zliczanie** geopol/Fed (nie influencer TA).

| Sytuacja | score |
|---|---|
| Escalation geopol (wojna, atak na infrastrukturę energetyczną, Taiwan/Strait) świeży <24h | +2 1D, +1 1W |
| Escalation wygasa / de-escalation | −1 |
| Dovish Fed surprise w newsie, zgodny z A5 | +1 (nie dubluj A5 w pełni — max +0.5 extra) |
| Hawkish / strong NFP/CPI surprise już w cenie taśmy | 0 (taśma w A) |
| Czysty retail FOMO (ATH chasing, YouTube targets) | −1 crowding 1W |
| Brak newsa | 0 |

GPR (Caldara–Iacoviello): poziom wysoki = szersze pasmo i dodatni skew 1W, **nie** auto-long 1D. ΔGPR spike → +1 do D na 1W, +0.5 na 1D.

ChatGPT/gold-social sentiment: dodatni sentyment → wyższe short-term futures returns (SSRN 2024). Użyj jako C, waga mała.

---

## D. Przepływy i pozycjonowanie

### 1D — tylko ETF

GLD+IAU zmiana shares outstanding / holdings:

| Flow | score |
|---|---|
| Silny inflow (> ~0.5% AUM lub wielodniowy) | +1 / +2 |
| Neutral | 0 |
| Outflow | −1 / −2 |

Lag 1–2d FLOW → RETURN dodatni, 3–5d mean-reversion. Na 1D bierz **wczorajszy** flow, nie dzisiejszy niepełny.

### 1W — ETF + COT

| Czynnik | waga w D | |
|---|---:|---|
| ETF 5d flow | 0.45 | jak wyżej na oknie tygodnia |
| MM net 13w MA trend | 0.35 | rosnący 13w → +1 (conviction); ostry zwrot po trendzie → −1 warning |
| MM z-score 52w | 0.20 | \|z\|>2 = crowding: **zmniejsza** pewność trendu, nie odwraca sam |

Swap dealers / commercials: tło, nie 1W trigger.

---

## E. Cross-asset

| Czynnik | 1D | 1W | Uwaga |
|---|---|---|---|
| Silver SI 1d/5d zgodny ze złotem | ±1 potwierdzenie | ±1 | Rozjazd: obniż conviction |
| Gold/silver z-score | 0 | ±1 przy \|z\|>2 (GSR 95th ≈ 88 hist.) | Mean-reversion srebra, słaby 1D gold |
| HY OAS Δ i poziom | 0 chyba że spike | +1 gdy OAS>6% | Lepszy fear niż VIX |
| VIX poziom | 0 kierunku | 0 kierunku | Tylko vol regime |
| Oil 5d ≤ −8% przy złocie ≥0 | 0 | stress +0.5 | Próg GOR 25/30 z ery $1–2k jest martwy przy $4k+ |
| SPX crash day | −1 jeśli R3 | 0/+1 po 72h | Liquidity trap |

---

## F. Kalendarz (mała waga)

| | score 1D | 1W |
|---|---|---|
| Piątek | +0.5 | n/a |
| Poniedziałek | −0.5 | n/a |
| Styczeń / sierpień | n/a | +0.5 |
| Maj–czerwiec / wrzesień | n/a | −0.5 |

Nie przebija makro. Sesja Azja 00:00–08:00 UTC historycznie niesie drift — przy 1D uwzględnij czy Azja już przeszła.

---

## G. Physical

| SGE vs LBMA | 1D | 1W |
|---|---|---|
| Premium ≥ +1% (≥1σ hist.) | +1 | +1 / +2 jeśli trwa ≥5 sesji |
| +0.3…+1.0% | 0 / +0.5 | +1 |
| Discount ≤ −0.2% | −0.5 | −1 |

LBMA: po dniach z premium ≥1% lepsze forward returns niż po discount. CB buying (WGC) = structural R2, nie 1D.

---

## Overlay jakościowy (agent)

Po skrypcie dodaj tylko to, czego skrypt nie ma:

- Event surprise vs consensus
- FOMC language / dots vs OIS
- COT 13w (1W)
- SGE premium
- GPR / breaking geopol
- CB headlines (PBOC, etc.)

Nie dubluj DXY/yields już w quant. Overlay score też w [−2, 2], potem merge 0.70/0.30 (1D) lub 0.55/0.45 (1W).

---

## Event gate — procedura

**Przed** (≤24h do CPI, Core PCE, NFP, FOMC, Powell):

- 1D: PASS. Możesz podać **warunkowy** if/then (hot CPI → 2Y/DXY ↑ → gold ↓) bez kierunku bazowego.
- 1W: wolno LEAN, conviction max MED.

**Po** publikacji:

1. Policz surprise (actual − consensus).
2. Sprawdź 30–60 min: 2Y, DFII10, DXY, gold.
3. NFP: trzymaj znak pierwszej godziny przez 1D i jako bias 1W (72h rule).
4. CPI: ignoruj print, czytaj breakevens vs nominal.
5. FOMC: 2Y + dots + presser. Zgodność trzech = pełny A5 ±2.

---

## Confluence checklist

HIGH wymaga:

- [ ] Znak A zgodny ze znakiem composite
- [ ] Co najmniej 3 z {A,B,C,D,E} tego samego znaku
- [ ] |composite| ≥ 0.45
- [ ] Nie R4
- [ ] Nie R3 dnia 1 (w R3 HIGH short dozwolony, HIGH long zabroniony)
- [ ] Brak krytycznego data_gap w DXY i yields
