# Competitive Pricing Intelligence & Simulator

A decision-support tool that turns competitor price movements into pricing recommendations.

**[English](./README.md) | [中文](./README.zh-TW.md)**

> **Portfolio Project Disclaimer**
> This is a portfolio project, not a production pricing system. All demand data, elasticity assumptions, and competitor prices are simulated or assumed values used to demonstrate methodology — not real market predictions.

---

## 1. Business Problem

Assume the role of a Business Analyst at an e-commerce company selling power banks in a competitive market. The real question isn't "what are competitors charging" — it's "how should we reprice when competitors change their prices, in order to maximize profit?"

**Core Narrative**

```
Competitor Monitoring   → What's happening in the market
Demand / Elasticity     → How price changes affect demand
Pricing Simulator       → What different strategies yield
Recommendation          → Supports the decision-maker
```

---

## 2. Project Objective

Build an end-to-end Collect → Monitor → Analyze → Simulate → Recommend pipeline that translates competitor price intelligence into actionable pricing recommendations, grounded in demand elasticity theory.

---

## 3. Data

| Item | Description |
|---|---|
| Product | 10000mAh USB-C fast-charging power bank (a standardized, easily-compared category) |
| Our Company | PowerUp (fictional e-commerce seller) |
| Competitors | Anker (premium), Xiaomi, ROMOSS, PhoneMax (budget/mid-tier) |
| Competitor Data | `data/competitor_prices.csv` — 60 days of simulated history, including 3 simulated promotion events used to validate the price-alert mechanism |

Competitor data is synthetically generated (see `scripts/generate_competitor_data.py`), not scraped. The project deliberately validates the *methodology* first — the core value is the analytical framework from "price intelligence" to "business decision," not the scraping itself.

---

## 4. Methodology

The project uses a **two-stage demand modeling approach** — the most important methodological progression in this project.

### Stage 1 — Constant Elasticity Model (Notebook 1 / Phase 1-2)

```
Q(P) = Q0 × (P / P0)^elasticity
```

Used for our own optimal pricing analysis, without competition. This is a multiplicatively separable functional form.

### Stage 2 — Linear (Bertrand-style) Competitive Model (Notebook 2 / Phase 5-6)

While building the Strategy Simulator, we discovered a **structural limitation** in the Stage 1 model: no matter how a competitor-price term is multiplied in, the profit-maximizing own price is mathematically independent of the competitor's price — this functional form **cannot represent price-war dynamics by construction**.

The fix is a linear/additive demand model:

```
Q(P, P_comp) = Q0 + slope_own × (P - P0) + slope_cross × (P_comp - P_comp0)
```

Under this model, the optimal price genuinely responds to competitor pricing. The full derivation is documented in `notebooks/02_competitive_strategy_analysis.ipynb`.

---

## 5. Pricing Model

| Parameter | Value | Rationale |
|---|---|---|
| Base Price | 690 | Assumed current price |
| Base Demand | 1000 units/month | Assumed baseline |
| Unit Cost | 400 | Estimated from 10000mAh power bank factory pricing (US$5.44–9.00) plus tariffs/certification/logistics — a reasonable, slightly conservative estimate |
| Elasticity | -1.8 | Standardized consumer electronics with many substitutes typically show elasticity >1.3–2.0; this assumption falls within that range |
| Cross-Price Elasticity | Adjustable per competitor, default 1.0 | Substitutability varies by brand (loyalty, positioning overlap) and should be judgment-calibrated |

The profit-maximizing price is cross-validated via grid search and the closed-form Lerner markup rule (`P* = Unit Cost × elasticity/(elasticity+1)`).

---

## 6. Competitor Monitoring

- **Current Market Price**: real-time comparison table with Price Diff / Price Diff %
- **Price Alert**: simple threshold rule (default: ≥5% change over the past 7 days triggers an alert), not complex anomaly detection
- **Historical Price Trend**: multi-competitor price chart, useful for spotting promotion patterns

---

## 7. Dashboard

The Streamlit app (`app.py`) has three tabs:

| Tab | Content |
|---|---|
| 📊 Pricing Model | Input panel, Current vs Recommended Price comparison, Demand/Revenue/Profit sensitivity charts |
| 🔍 Competitor Monitoring | Comparison table, Price Alerts, Historical Trend |
| ⚔️ Strategy Simulator | Competitor price-drop scenario simulation, Maintain/Match/Partial Cut strategy comparison (with adjustable Cross-Price Elasticity) |

### How to Run

```bash
pip install -r requirements.txt
streamlit run app.py
```

---

## 8. Business Insights

1. **Profit maximization ≠ revenue maximization.** Under elastic demand (|elasticity| > 1), revenue decreases monotonically with price, but profit has a distinct peak — they are not maximized at the same price point.
2. **A price competitors can afford doesn't mean we can afford it.** Competitors may have different cost structures (scale, vertical integration). Naively matching a competitor's price can push our own margin to zero or negative.
3. **Whether — and how much — to respond to a competitor's price cut depends on how close it gets to our own cost line.** For moderate cuts, "maintain price" is usually optimal; only when a competitor's price approaches our cost structure does matching or partial-cutting become worthwhile.
4. **Rising costs and intensifying competition call for different responses.** Cost increases can be passed through via a higher price while margin stays constant; intensifying competition (higher elasticity) directly compresses the achievable margin and can't simply be passed through.

---

## 9. Limitations

- Demand, elasticity, and cross-price elasticity are all assumed values, not estimated from real sales or market research data.
- Competitor price data is synthetically generated, not scraped from real sources.
- Cross-price elasticity currently requires manual adjustment per competitor brand; there's no systematic, persisted per-brand calibration.
- Price alerts use a single-point comparison (latest vs. N days ago), which is sensitive to how the lookback window aligns with the actual event — not a rigorous anomaly-detection method.
- The model does not account for seasonality, inventory, platform ranking algorithms, advertising, or other factors that affect sales.
- All recommended prices/strategies are model-based estimates, not guaranteed outcomes.

---

## 10. Future Improvements

- With real sales and competitor price history, estimate true elasticities via regression instead of using assumed values.
- Store cross-price elasticity per competitor brand persistently, rather than requiring manual adjustment each time.
- Integrate real scraping (`requests` / `BeautifulSoup` / `Playwright`), respecting each site's robots.txt and terms of service.
- Introduce more rigorous anomaly detection (e.g., moving average, standard-deviation thresholds) instead of single-point comparison.
- Extend Scenario Analysis to systematically cover all competitors, not just a single example.

---

## Repository Structure

```
pricing-project/
├── app.py                          # Streamlit dashboard
├── requirements.txt
├── .gitignore
├── src/
│   ├── demand_model.py             # Constant elasticity + competitive linear demand models
│   ├── pricing_model.py            # Revenue/Cost/Profit + grid search optimizer
│   ├── visualize.py                # Plotly chart functions
│   ├── competitor_analysis.py      # Comparison table + price alerts
│   ├── strategy_simulator.py       # Strategy comparison (competitive model)
│   └── scenario_analysis.py        # Cost/elasticity/competitor scenario analysis
├── scripts/
│   └── generate_competitor_data.py # Synthetic competitor data generator
├── data/
│   └── competitor_prices.csv
└── notebooks/
    ├── 01_pricing_simulator.ipynb              # Phase 1: own pricing model
    └── 02_competitive_strategy_analysis.ipynb  # Phase 3-6: competitor-aware model
```

---

## Author's Note

This project is a portfolio piece, demonstrating the application of demand theory (elasticity, marginal analysis) to business pricing decisions. Developed with AI pair-programming assistance (Claude) for coding and debugging; methodology design, assumption validation, and business interpretation were author-led.
