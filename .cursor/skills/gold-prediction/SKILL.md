---
name: gold-prediction
description: Inżynieryjna predykcja złota (XAUUSD / GC / LBMA) na dwa okna 1D i 1W. Łączy makro (DXY, real yields, Fed path), sentyment, przepływy, technikę i reżim z wyważonymi wagami. Używaj gdy użytkownik prosi o predykcję złota, forecast XAUUSD, bias 1D/1W, analizę złota, lub ocenę kierunku ceny złota.
---

# Predykcja złota 1D / 1W

Cel: maksymalna **trafność kierunkowa** (direction), nie zgadywanie dokładnej ceny. Cena złota jest niestacjonarna; predykcja poziomu to iluzja. Predykuj znak i koszyk wielkości (ATR), potem pasmo.

Ten skill ładuje się automatycznie przy zapytaniach o złoto / XAUUSD / GC.

## Sufity trafności (nie przekraczaj w narracji)

Walk-forward, bez look-ahead. Źródła: XGBoost+makro 2024–26, BrokersDB 22y, desk ML 55–65%.

| Warstwa | 1D | 1W |
|---|---|---|
| Wszystkie sesje | 54–58% | 56–62% |
| Tylko HIGH (confluence ≥3, brak event gate) | 60–66% | 62–70% |
| Claim >70% bez własnego walk-forward | zabroniony | zabroniony |

Trafność rośnie przez **PASS**, nie przez wymuszanie kierunku. HIGH wołaj rzadko.

## Architektura

```
1. Dane (cena + makro + kalendarz + news)
2. Reżim R1–R4
3. Scoring czynników −2…+2
4. Wagi horyzontu × reżimu
5. Quant (skrypt) + overlay jakościowy
6. Confluence → LONG | SHORT | NEUTRAL + HIGH|MED|LOW|PASS
7. Pasmo ATR, invalidation, event gate
```

Uruchom `scripts/score_gold.py` gdy sieć działa. Overlay (newsy, COT, SGE, GPR, Fed funds futures) dolicz ręcznie wg [factors.md](factors.md). Szczegóły empiryczne: [sources.md](sources.md). Szablon: [output-template.md](output-template.md).

## Reżimy

| Kod | Detekcja | Co zmienia |
|---|---|---|
| **R1** Opportunity-cost | 60d corr(gold, Δreal yield) ≤ −0.40 | Pełna waga real yields + DXY |
| **R2** Structural bid (default od 2022) | corr > −0.40, brak paniki płynności | Tłum real-yield beta (JPM: R² 85%→16%); waga GPR / CB / term premium |
| **R3** Liquidity scramble | HY OAS > 6% **i** złoto spada z ryzykownymi | Pierwsza noga w dół (margin). Nie kupuj dipu dnia 1 |
| **R4** Event | CPI / NFP / FOMC / Powell w ≤24h | 1D = PASS lub LOW; pasmo 1.5–2× ATR |

Domyślnie **R2**, chyba że dane pokażą R1/R3/R4. W R2 złoto może rosnąć przy rosnących real yields (CB, fiscal, de-dollarization).

## Wagi grup — 1D vs 1W

Suma = 1.00. To nie są „równe filary”. 1D ≠ przeskalowane 1W.

### 1D (close → next session close)

| Grupa | R1 | R2 | R3 |
|---|---:|---:|---:|
| A Makro-taśma (DXY, 2Y/5Y, real yield, breakevens, Fed path) | 0.36 | 0.30 | 0.18 |
| B Technika / mikrostruktura | 0.26 | 0.26 | 0.22 |
| C Sentyment news (FinBERT/LLM, asymetria negatywna) | 0.12 | 0.14 | 0.12 |
| D Przepływy (GLD/IAU daily; **nie COT**) | 0.10 | 0.10 | 0.16 |
| E Cross-asset (SI, HY spread; VIX **nie** jako kierunek) | 0.08 | 0.10 | 0.24 |
| F Kalendarz (DoW, miesiąc) | 0.05 | 0.05 | 0.03 |
| G Physical (SGE premium) | 0.03 | 0.05 | 0.05 |

### 1W (piątek→piątek lub rolling 5 sesji)

| Grupa | R1 | R2 | R3 |
|---|---:|---:|---:|
| A Makro (DXY, real yields, Fed path, breakevens) | 0.42 | 0.36 | 0.20 |
| B Technika tygodniowa + momentum | 0.16 | 0.16 | 0.14 |
| C Przepływy + COT (ETF tydzień, MM 13w trend / z-score) | 0.14 | 0.16 | 0.18 |
| D Sentyment + geopolityka (GPR = filtr vol, słaby kierunek) | 0.10 | 0.14 | 0.14 |
| E Cross-asset (SI, GSR, HY; gold/oil = reżim nie trade) | 0.08 | 0.08 | 0.22 |
| F Physical / structural (SGE, CB) | 0.06 | 0.07 | 0.08 |
| G Kalendarz | 0.04 | 0.03 | 0.04 |

**Merge quant/overlay:** 1D = 0.70·quant + 0.30·overlay. 1W = 0.55·quant + 0.45·overlay.

## Zasady, które podnoszą trafność

1. Predykuj **log-return / znak**, nie USD/oz.
2. **Event gate:** przed CPI/NFP/FOMC nie zgaduj 1D. Po NFP: **72-hour rule** — pierwsza 1–6h reakcja ustawia bias na 1–3 sesje; nie fade'uj newsa.
3. Złoto handluje **real yield i DXY**, nie nagłówek. Hawkish FOMC + wzrost nominalnych + spadek breakevens = podwójnie bearish (real yields ↑ z obu stron).
4. **CPI print ≠ trade.** r(CPI, gold monthly) ≈ 0.03. Liczy się 5Y breakeven i zaskoczenie vs consensus, transmitowane przez yields/DXY.
5. **VIX ≠ kierunek złota.** r ≈ 0. Miesięczny win rate przy VIX>30 ≈ 55%. HY credit spread jest lepszym „fear”. W panice płynności złoto spada pierwszego dnia.
6. COT: nie poziom MM net. Sygnał = **13-tygodniowy trend** MM + z-score ekstremum jako kruchość, nie timing. COT wychodzi w piątek z danymi wtorku — prawie bezużyteczny na 1D.
7. Technika: struktura (PDH/PDL, EMA20/50, ATR, weekly close) + RSI/MACD tylko jako **potwierdzenie**. Nie stackuj 5 oscylatorów. Daily Hurst ≈ 0.48 → słaba persystencja; po 3–4 dniach spadku P(up) ≈ 55–59%.
8. Confluence: HIGH tylko gdy ≥3 grupy zgodne znakiem **i** |score| ≥ 0.45 **i** brak R4.
9. Fat tails: excess kurtosis ≈ 9. Pasmo min. 1.0× ATR(14); przy R3/R4 1.8–2.2×. Nigdy punktowa cena.
10. W R2 nie shortuj złota tylko dlatego, że real yields rosną.

## Workflow

Skopiuj i odhacz:

```
- [ ] 1. Cena: GC=F / XAUUSD, ATR14, PDH/PDL, EMA20/50/200, RSI, sekwencja up/down
- [ ] 2. Makro: DXY 1d/5d, DFII10 lub 10Y−5Y BE, DGS2, T5YIE, Fed funds futures
- [ ] 3. Cross: SI=F, CL=F, HY OAS, VIX tylko jako vol reżim
- [ ] 4. Flows: GLD+IAU shares/holdings 1d i 5d
- [ ] 5. COT (tylko 1W): MM net 13w MA, 52w z-score, OI
- [ ] 6. SGE premium vs LBMA
- [ ] 7. Kalendarz 48h: CPI PCE NFP FOMC Powell Jackson Hole
- [ ] 8. News 24–72h: Reuters/Bloomberg/Kitco + X geopol (GPR proxy)
- [ ] 9. Reżim R1–R4
- [ ] 10. python scripts/score_gold.py
- [ ] 11. Overlay jakościowy (factors.md)
- [ ] 12. Confluence + event gate → 1D i 1W osobno
- [ ] 13. Output wg output-template.md (PL)
```

Brak danych: obniż confidence, nie zmyślaj. Luka w DXY/yields kasuje HIGH.

## Źródła danych (kolejność)

1. Yahoo: `GC=F`, `DX-Y.NYB`, `SI=F`, `CL=F`, `^TNX`, `^FVX`, `^IRX`, `^VIX`, `^GSPC`, `GLD`, `IAU`, `HYG`
2. FRED CSV: `DFII10`, `T5YIE`, `DGS2`, `DGS10`, `T10Y2Y`, `BAMLH0A0HYM2`
3. CME FedWatch / SOFR futures — path stóp
4. CFTC Disaggregated COT gold 088691
5. WGC ETF flows, Gold Demand Trends (CB = poziom, nie 1D)
6. SGE Au99.99 vs LBMA PM
7. Kalendarz: ForexFactory / investing.com consensus + surprise
8. News: Reuters, Bloomberg, Kitco (sentyment, nie target)
9. GPR daily: matteoiacoviello.com/gpr.htm (filtr 1W, nie sygnał 1D)

## Zakazane

- Losowy train/test split, predykcja raw price, MAE jako jedyna metryka
- „Złoto idzie w górę bo inflacja/CPI”
- VIX spike → automatyczny long
- COT net-long → automatyczny short
- Target 3–4 cyfry bez pasma i invalidation
- Uśrednianie 1D i 1W do jednego wyroku
- YouTube/Twitter TA jako primary signal
- Ignorowanie sesji azjatyckiej przy 1D (historycznie największy drift)

## Examples

### Example 1 — HIGH 1D long, MED 1W long (R2)

Wejście: DXY −0.6% d/d, DFII10 −8 bp, GLD inflow, brak event, 3 down-days, RSI 38, news geopol umiarkowany+, SGE +0.4%.

Ocena: A+ D+ B mean-reversion zgodne. |score_1d| > 0.45, 4 grupy +. 1W: makro sprzyja, COT nie ekstremalny.

Output: 1D LONG HIGH; 1W LONG MED. Invalidation 1D: DXY reclaim + real yields odwrót.

### Example 2 — R4 PASS 1D

Wejście: CPI jutro 12:30 UTC. DXY słaby, technika bycza.

Output: 1D PASS (event gate). 1W LEAN zgodny z makro, LOW/MED. Pasmo 1D 1.8× ATR. Po publikacji: zaskoczenie → yields/DXY, nie sam print; NFP: trzymaj 1h reaction.

### Example 3 — konflikt warstw → NEUTRAL

Wejście: DXY −0.4% (bycze), weekly close pod EMA20, MM COT z-score +2.1, 4 up-months.

Output: 1D NEUTRAL LOW. 1W NEUTRAL/LEAN short MED (mean-reversion miesięczna + crowding). Nie forsuj LONG.

## Instructions — kolejność pracy agenta

1. Zbierz checklistę; uruchom skrypt.
2. Ustal reżim zanim policzysz wagi.
3. Policz 1D i 1W **osobno**.
4. Zastosuj event gate i confluence.
5. Wypisz raport w [output-template.md](output-template.md).
6. Podaj 3 największe drivery i 1 największe ryzyko pomyłki.
7. Jeśli użytkownik chce „dokładną cenę”, oddaj mid pasma + ATR, nie punkt.
