# Urban Heat Island & Citi Bike Analysis - Results Overview

## Key Findings

### 1. Data Processing
- **Trips Loaded**: 4,603,575 trips (Aug 2024).
- **Stations Mapped**: 2,139 stations successfully assigned to a Zip Code and HVI Score.

### 2. Statistical Analysis

#### Hypothesis Test (Mann-Whitney U)
We compared the mean daily trips of stations in **High Heat Vulnerability** zones (HVI 4-5) versus **Low Heat Vulnerability** zones (HVI 1-2).

- **High HVI (4-5) Mean Trips**: 929.78
- **Low HVI (1-2) Mean Trips**: 3,959.31
- **Result**: Significant difference (p < 0.001).
- **Insight**: Stations in cooler (low risk) areas have **4x more trips** on average than those in high heat risk areas.

#### Poisson Regression
We modeled the relationship between HVI Score and Trip Counts: `trips ~ HVI_Score`.

- **HVI Coefficient**: -0.4310
- **Interpretation**: For every 1 unit increase in Heat Vulnerability Index, the expected trip count decreases by ~35% (Factor: 0.65).
- **Statistical Significance**: p < 0.001 (Highly significant).

## Visualizations
The analysis includes:
- A map of NYC Zip Codes colored by HVI Score with Citi Bike stations overlaid.
- A boxplot showing the distribution of trips across HVI scores.

*(See `eda.ipynb` for charts)*
