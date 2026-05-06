# K-Food Growth Intelligence & Product Opportunity Simulator

A business analytics dashboard for identifying K-Food product opportunities across selected global markets. This project combines real public data, synthetic business simulation data, review intelligence, market opportunity scoring, product idea recommendation, and scenario-based business planning into one Streamlit dashboard.

The main question this project answers is:

**Which K-Food product idea should be prioritized, in which market, and why?**

## Project Overview

International food expansion decisions often require teams to evaluate markets with incomplete data. Real company sales, distributor performance, competitor sell-out, and customer-level data are usually proprietary and unavailable for public portfolio work.

This project simulates how a business planning or market intelligence team can use available public signals and synthetic business data to structure product opportunity analysis. It does not attempt to predict exact sales. Instead, it creates a decision-support workflow that connects consumer interest, macro-market readiness, simulated competitor conditions, customer pain points, product ideas, and scenario-based business outcomes.

## Data Used

This project uses a hybrid data strategy.

**Real public data**
- Google Trends: relative consumer search interest for K-Food keywords
- World Bank WDI: macro indicators such as population, GDP per capita, urbanization, internet usage, household consumption, and inflation

**Synthetic data**
- Anonymized competitor product benchmark
- Simulated customer review corpus
- Scenario-based financial assumptions

Synthetic data are used to demonstrate the analytics workflow when proprietary company, marketplace, and customer-level data are unavailable. The results should not be interpreted as real company-specific recommendations, real customer sentiment, or actual financial forecasts.

## Countries and Categories

The dashboard covers eight markets: Indonesia, Malaysia, Philippines, Singapore, Thailand, Viet Nam, United States, and Australia.

The product categories include Korean ramen, kimchi, gochujang sauce, frozen mandu, ready meal, and seaweed snack.

## Analytics Workflow

The project follows an end-to-end business analytics pipeline:

1. Generate synthetic competitor, review, and business assumption data
2. Fetch Google Trends search interest data
3. Prepare Google Trends features such as average interest, recent momentum, volatility, and trend consistency
4. Prepare World Bank macro features and macro-market readiness scores
5. Build review intelligence using TF-IDF and NMF topic modeling
6. Create market opportunity scores by combining trend, macro, competitor, review, and price feasibility signals
7. Generate product idea recommendations using business rules
8. Build scenario-based revenue, margin, and break-even outputs
9. Cluster country-category opportunities into market segments
10. Present the full workflow in a multi-page Streamlit dashboard

## Methodology

Google Trends is used as a relative consumer interest signal. A value of 100 represents the highest relative search interest within the selected query, geography, and period. It does not represent actual search volume, sales volume, market size, or purchase intent.

The review intelligence module uses synthetic reviews to demonstrate how customer feedback can be translated into business themes such as taste authenticity, spiciness, price sensitivity, portion size, packaging, halal labeling, convenience, and health concerns.

The product opportunity score is a 0–100 decision-support index. It combines consumer interest, trend momentum, macro-market readiness, review-based opportunity signals, competitive space, price feasibility, and trend consistency. The score is not a predictive sales model.

The scenario simulator uses synthetic assumptions to estimate net revenue, contribution profit, contribution margin, and break-even units under conservative, base, and aggressive scenarios.

## Dashboard Pages

The Streamlit dashboard is structured as a business story:

- **Executive Overview**: summarizes the strongest product-market opportunity and recommended next action
- **Trend Radar**: shows relative K-Food search interest from Google Trends
- **Market Opportunity**: compares countries and categories using a world map, ranking table, and segmentation chart
- **Review Intelligence**: summarizes customer pain points and product adaptation themes
- **Product Idea Board**: converts market signals into product concepts, target segments, and channel suggestions
- **Scenario Simulator**: estimates revenue, margin, and break-even outcomes under different scenarios
- **Methodology Notes**: explains data sources, assumptions, limitations, and modeling approach

## Repository Structure

```text
.
├── app/
│   ├── streamlit_app.py
│   ├── dashboard_utils.py
│   └── pages/
├── data/
│   ├── raw/
│   ├── synthetic/
│   └── processed/
├── src/
│   ├── generate_synthetic_data.py
│   ├── fetch_google_trends.py
│   ├── prepare_trend_features.py
│   ├── prepare_macro_features.py
│   ├── build_review_nlp_features.py
│   ├── build_market_opportunity_scores.py
│   ├── build_product_ideas.py
│   ├── build_scenario_outputs.py
│   └── build_country_category_clusters.py
├── notebooks/
├── outputs/
├── requirements.txt
└── README.md