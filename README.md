# K-Food Growth Intelligence & Product Opportunity Simulator

A business analytics and market intelligence prototype for identifying attractive K-Food product opportunities across selected global markets.

This project combines real public data, synthetic business simulation data, machine learning-assisted review intelligence, market opportunity scoring, product idea recommendation, and scenario-based financial simulation into an interactive Streamlit dashboard.

The main business question is:

> Which K-Food product idea should be prioritized, in which market, and why?

---

## 1. Project Overview

Food companies expanding internationally often need to evaluate product opportunities across multiple markets using incomplete data. Real company sales data, distributor data, customer-level data, and competitor sell-out data are often proprietary or unavailable.

This project simulates how a business planning or market intelligence team could build a structured decision-support system using available public signals and simulated business data.

The system evaluates K-Food product opportunities across selected countries and categories by combining:

- Consumer search interest
- Macro-market readiness
- Simulated competitor landscape
- Simulated customer review pain points
- Product opportunity scoring
- Product idea recommendation
- Scenario-based business planning and P&L simulation

The project is designed as a portfolio prototype, not as a real company-specific market entry recommendation.

---

## 2. Business Problem

When evaluating new product opportunities, business teams often face questions such as:

- Which countries show stronger consumer interest in K-Food?
- Which product categories have stronger trend momentum?
- Which markets look more attractive from a macro and consumer readiness perspective?
- What customer pain points should guide product adaptation?
- What product ideas can be generated from market and review signals?
- How would different business scenarios affect revenue, margin, and break-even units?

This project addresses those questions through a structured analytics workflow.

---

## 3. Project Objectives

The objectives of this project are to:

1. Build a market intelligence dashboard for K-Food product opportunity analysis.
2. Use Google Trends as a consumer interest signal.
3. Use World Bank indicators as macro-market readiness signals.
4. Generate synthetic competitor and review datasets to simulate unavailable proprietary data.
5. Apply NLP-based review theme detection to identify customer pain points.
6. Build a product opportunity scoring model.
7. Translate opportunity signals into product ideas.
8. Simulate business scenarios using synthetic financial assumptions.
9. Present the results in a business-friendly Streamlit dashboard.

---

## 4. Data Transparency

This project uses a hybrid data strategy.

### Real Public Data

| Data Source | Purpose |
|---|---|
| Google Trends | Relative consumer search interest for selected K-Food keywords |
| World Bank WDI | Macro-market indicators such as population, GDP per capita, urbanization, internet usage, household consumption, and inflation |

### Synthetic Data

| Synthetic Dataset | Purpose |
|---|---|
| Anonymized competitor benchmark | Simulates marketplace product availability, pricing, brand type, review count, rating, and positioning |
| Synthetic customer review corpus | Simulates product feedback themes such as price sensitivity, spiciness, halal labeling, packaging, convenience, authenticity, and health concerns |
| Scenario-based business assumptions | Simulates price, estimated units, cost of goods sold, logistics, marketing, trade promotion, distributor margin, revenue, and contribution margin |

Synthetic data are used because real company sales, distributor, competitor, and customer-level data are usually proprietary and unavailable for portfolio projects.

The project should not be interpreted as a real company-specific recommendation or actual commercial forecast.

---

## 5. Countries and Product Categories

### Target Countries

The analysis covers the following markets:

- Indonesia
- Malaysia
- Philippines
- Singapore
- Thailand
- Viet Nam
- United States
- Australia

### Product Categories

The project evaluates selected K-Food-related categories:

- Korean ramen
- Kimchi
- Gochujang sauce
- Frozen mandu
- Ready meal
- Seaweed snack

---

## 6. System Architecture

The project follows an end-to-end business analytics pipeline:

```text
Real Public Data
├── Google Trends
└── World Bank macro indicators

Synthetic Simulation Data
├── Competitor product benchmark
├── Customer review corpus
└── Business assumptions

Data Processing Layer
├── Trend feature engineering
├── Macro feature engineering
├── Competitor feature aggregation
├── Review text cleaning
└── Scenario output generation

ML & Analytics Layer
├── Review topic modeling
├── Review opportunity scoring
├── Country-category clustering
├── Opportunity scoring
└── Product idea recommendation

Business Planning Layer
├── Product opportunity ranking
├── Market segmentation
├── Product idea board
├── Scenario-based revenue simulation
└── Contribution margin and break-even analysis

Dashboard Layer
└── Streamlit multi-page business dashboard