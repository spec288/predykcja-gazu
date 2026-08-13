# Szablon wyjścia

Pisz po polsku. Dwa okna osobno. Zero punktowej ceny bez pasma.

```markdown
# Predykcja złota — {data UTC} {HH:MM} UTC
**Spot:** {XAUUSD / GC=F close lub last} | **ATR(14):** {usd} ({pct}%)
**Reżim:** R1/R2/R3/R4 — {1 zdanie dlaczego}
**Event gate:** brak | {ticker wydarzenia, czas UTC}
**Data quality:** OK | luki: {lista}

## 1D (następna sesja / ~24h)
- **Bias:** LONG | SHORT | NEUTRAL
- **Conviction:** HIGH | MED | LOW | PASS
- **Score:** {composite −2…+2} | quant {q} + overlay {o}
- **Pasmo (80% subiektywne, 1.0–1.3× ATR; R3/R4 1.8–2.2×):** {low} – {high}
- **Mid implikowany:** {mid} ({chng%})
- **Invalidation:** {poziom lub warunek makro, np. DXY close nad X}
- **Drivery (+/−):** 1. … 2. … 3. …
- **Główne ryzyko pomyłki:** {1 zdanie}

## 1W (5 sesji)
- **Bias:** LONG | SHORT | NEUTRAL
- **Conviction:** HIGH | MED | LOW | PASS
- **Score:** {composite} | quant {q} + overlay {o}
- **Pasmo (1.6–2.2× weekly-ish; użyj ATR×√5):** {low} – {high}
- **Mid implikowany:** {mid} ({chng%})
- **Invalidation:** …
- **Drivery (+/−):** 1. … 2. … 3. …
- **Główne ryzyko pomyłki:** …

## Confluence
| Grupa | 1D | 1W |
| A Makro | +/−/0 | |
| B Technika | | |
| C Sentyment | | |
| D Flows | | |
| E Cross | | |
| F Kalendarz | | |
| G Physical | | |

Zgodnych grup 1D: n/7 | 1W: n/7

## If/then (obowiązkowe przy R4 lub MED/LOW)
- Jeśli {event} hot → {2Y/DXY/gold}
- Jeśli {event} cold → …

## Disclaimer
To nie jest rada inwestycyjna. Trafność bazowa 1D ~55–58%, HIGH ~60–66%. Fat tails: dzień −5–9% zdarza się empirycznie.
```

Zasady wypełniania:

- HIGH bez spełnienia checklisty z factors.md → obniż do MED.
- PASS: bias NEUTRAL, pasmo szerokie, if/then zamiast kierunku.
- Nie uśredniaj 1D i 1W do „ogólnie byczo”.
- Podaj tickery i Δ (DXY %, yields bp), nie ogólniki.
- Jeśli skrypt padł: napisz to i policz ręcznie z factors.md; conviction max MED.
