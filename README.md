# Predykcja złota (1D / 1W)

Cursor skill: `.cursor/skills/gold-prediction/`

Agent scoruje **dwa okna osobno** (1D i 1W) z wagami zależnymi od horyzontu i reżimu (R1–R4): makro-taśma, technika, sentyment, przepływy, cross-asset, kalendarz, physical. Trafność przez confluence i PASS, nie przez punktową cenę.

```bash
python3 .cursor/skills/gold-prediction/scripts/score_gold.py --pretty
python3 .cursor/skills/gold-prediction/scripts/score_gold.py --event --pretty   # CPI/NFP/FOMC ≤24h
```

Nie jest to rada inwestycyjna. Bazowa trafność kierunkowa 1D ~55–58%; HIGH ~60–66% przy abstynencji w szumie.
