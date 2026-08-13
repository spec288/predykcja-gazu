# Źródła i kalibracja wag

Skill kalibrowany pod 1D/1W, nie pod kwartał. Wagi = synteza (nie kopiowanie jednego modelu).

## Instytucje / makro

- **PIMCO, Understanding Gold Prices (2025):** real yields główny driver 2 dekad; 100 bp 10Y real ≈ −18% real gold (duration empiryczna). Residual po 2022: CB buying.
- **J.P. Morgan AM, Is Gold’s Old Playbook Broken?:** 1990–2021 10Y real yield tłumaczy ~85% wariancji spot; od 2022 R² ~16%, beta potrafi zmienić znak. Gold reaguje na term premium / fiscal credibility, nie tylko poziom real rates.
- **Chicago Fed Letter 464 (2021):** 1 pp innowacji expected 10Y real ≈ −3.4% real gold; pesymizm survey podbija cenę.
- **World Gold Council GRAM:** 4 bloki short-run: Economic expansion, Risk & uncertainty, Opportunity cost (FX + rates), Momentum (ETF + futures). Residual = nowy driver / szok. Okno estymacji skracane do ~5y.
- **WGC Gold Demand Trends Q1–Q2 2026:** CB 700–900 t/rok jako structural bid; ETF rotacja regionalna (US outflow vs Europe/Asia inflow) = 1W momentum.
- **WGC short-term performance model (2021, Iyer):** na oknie 1m momentum (ETF+COMEX) potrafi > opportunity cost; współczynniki niestabilne — dlatego reżim R1/R2.
- **State Street (2026):** erosion of Treasury convenience yield; złoto jako repricing safe-asset premium, nie „zepsuty” real-rate channel.
- **BrokersDB (2003–2025, 7016 dni, 67 wskaźników):**
  - DXY monthly r = −0.448 (dominanta)
  - 5Y yield −0.344, 2Y −0.338, 10Y −0.292
  - 5Y BE +0.195; CPI returns r ≈ 0.028 (NS); VIX r ≈ −0.023 (NS); Fed funds NS
  - CPI level r ≈ 0.90 — hedge dekadowy, nie trade
  - DXY i gold same direction 42% miesięcy
  - HY OAS >6%: gold +1.49%/m, wr 60% vs VIX>30 wr ~55% i 15 worst VIX spikes wr 46.7%
  - NFP 72h: pierwsza godzina ustawia bias
  - Inwersja 10s2s: +11.8 pp / 12m vs normal curve
  - Hurst daily 0.48; po 4 down days P(up) 58.9%; po 4 up-months P(kontynuacja) niska
  - Excess kurtosis 9.11; 5σ dni 4724× częstsze niż Gaussian
  - Piątek +0.114% wr 57%; poniedziałek −0.042%; Azja 00–08 UTC ≈ cały 22y drift
  - Styczeń +2.99% wr 64%; czerwiec najsłabszy w ich sample (inne source: wrzesień)

## Modele predykcyjne 2024–2026

- Medium/JIN (2026) + Chaos Solitons Fractals (2023): **XGBoost > LSTM** na 1–5D tabular+makro. RF jako stabilny baseline. LSTM-Attention dopiero na dłuższym sekwencyjnym.
- MDPI IJFS 13(2):102 (2025): fusion financial + macro + sentiment; Prophet/BiLSTM vs czyste ekonometryczne.
- IEEE ISCMI 2024: LSTM / N-HiTS / TSMixer + silver + sentiment biją ARIMA 2020–24.
- MDPI Entropy 28(3):271 (2026): news sentiment + CNN-QRLSTM; lexicon geopol/policy.
- IEEE ICCAIS 2024: heterogeneous ensemble (LR, RF, GBM, SVM, GPR → XGBoost meta) > pojedyncze i > LSTM.
- Fusion BERT+GRU (8115 labeled gold headlines): BERT 86% na sentymencie; GRU+sentiment > GRU; DM test p<0.01.
- SSRN 4877214 (2024): ChatGPT daily gold sentiment → short-term futures returns, silniej w kryzysie.
- IJAI 2025: news sentiment Granger-przyczynowy dla gold; negatywny > pozytywny.
- Deakin/Monash 2024: w niepewności 2020–24 feature combo (silver, sentiment) istotnie obniża błąd.

## Pozycjonowanie / microstructure

- COT: Granger (SSRN 2382299) — sentyment COT słabo **prowadzi** returns; returns prowadzą sentyment. Ekstrema = crowding.
- COT 13w MA MM (2026 practitioner tests): ~57% weekly dir. vs ~50% na raw weekly net — wciąż słaby sam, filtr 1W.
- COT lag: wtorek→piątek. 1D ≈ 0.
- GLD flows: VAR (Huang) lag 1–2d FLOW→RETURN +, lag 3–5d reversion.
- LBMA Alchemist 83: SGE premium ≥1% vs discount −0.2% — różne forward LBMA returns.
- Session: London–NY overlap max liquidity; London PM fix 14:55–15:05 UTC sweep-reverse ~70% (mikro, nie close-to-close).
- Seasonax / IGWT 2024 / BrokersDB: Friday strength, Monday weakness.

## Fora / X / YT (consensus, nie edge)

- r/algotrading: EA 90%+ hit rate na XAUUSD = overfit. Real ML 55–65% dir. + R:R.
- TradingView/ICT/SMC: przydatne do egzekucji (sweep, FVG), nie do close-to-close 1D forecast. Nie wkładaj OB/FVG do scoringu kierunku dnia.
- Kitco comments / gold Twitter: lagging narrative. Użyj volume geopol keywords jako GPR proxy, nie targetów.
- YT TA (RSI/Fib daily calls): zero edge vs DXY+yields. Ignoruj jako primary.
- BabyPips/forex: „gold = inverse DXY” — prawdziwe, ale 42% wyjątków; wymaga potwierdzenia yields.

## Świadome odrzucenia

| Popularne | Dlaczego waga ≈ 0 na 1D/1W |
|---|---|
| Headline CPI / Core CPI print | returns corr ~0; lag ~35m do hedging |
| Fed funds rate level | NS monthly; liczy się path vs pricing |
| VIX jako long trigger | corr 0; crash-day gold często spada |
| COT net-long level | crowding bez timing |
| Mine supply / jewelry | wolne, WGC quarterly |
| GDX / miners | beta + idiosynkrazja, nie spot |
| Fibonacci / ichimoku solo | brak walk-forward edge |
| Bitcoin as digital gold 1D | korelacja niestabilna |

## Mapowanie research → wagi

1. DXY i yields dominują monthly → największy blok A, większy na 1W.
2. 1D bliżej microstructure + mean-reversion (Hurst<0.5) → B większe na 1D niż klasyczne „makro only”.
3. Sentiment poprawia modele 2024–26, ale słabiej niż taśma → C 0.12–0.14.
4. ETF lag 1–2d → D na 1D; COT tylko 1W.
5. VIX wycięty z kierunku; HY w E i R3.
6. Post-2022 break → R2 tłumi A2.
7. Fat tails → pasma ATR, nie punkt.
8. Trafność przez abstynencję (PASS) — zgodne z desk ML i z low SNR złota.
