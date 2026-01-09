"""
DSA 210 Final Project - Analysis Script
Author: [Your Name]

This script performs the statistical analysis for the Urban Heat Island vs. Citi Bike project.
It loads the processed station data and runs:
1. Mann-Whitney U Test: To compare trip counts between High and Low HVI zones.
2. Poisson Regression: To model the relationship between HVI Score and Trip Counts.
"""
import pandas as pd
import numpy as np
import statsmodels.api as sm
import statsmodels.formula.api as smf
from scipy.stats import mannwhitneyu
import os

def run_analysis(data_path='final_station_data.csv'):
    print("--- Starting Analysis ---")
    
    # 1. Load Data
    if not os.path.exists(data_path):
        print(f"Error: {data_path} not found. Run data_loader.py first.")
        return
        
    df = pd.read_csv(data_path)
    print(f"Data Loaded. Shape: {df.shape}")
    print(df.head())
    
    # 2. Hypothesis Testing: High HVI vs Low HVI
    # HVI Score is 1-5.
    # High: 4-5, Low: 1-2 (as per prompt)
    
    high_hvi = df[df['HVI_Score'].isin([4, 5])]['total_trips']
    low_hvi = df[df['HVI_Score'].isin([1, 2])]['total_trips']
    
    print(f"\n--- Hypothesis Test (Mann-Whitney U) ---")
    print(f"High HVI (4-5) Stations: {len(high_hvi)}")
    print(f"Mean Trips: {high_hvi.mean():.2f}")
    
    print(f"Low HVI (1-2) Stations: {len(low_hvi)}")
    print(f"Mean Trips: {low_hvi.mean():.2f}")
    
    if len(high_hvi) > 0 and len(low_hvi) > 0:
        stat, p_value = mannwhitneyu(high_hvi, low_hvi, alternative='two-sided')
        print(f"Mann-Whitney U Statistic: {stat}")
        print(f"P-Value: {p_value:.5f}")
        
        if p_value < 0.05:
            print("Result: Significant difference in trip counts between High and Low HVI zones.")
        else:
            print("Result: No significant difference found.")
    else:
        print("Insufficient data for hypothesis test.")
        
    # 3. Poisson Regression
    print("\n--- Poisson Regression Model ---")
    # Formula: total_trips ~ HVI_Score
    # We treat HVI_Score as numeric (ordinal) or categorical?
    # Prompt implies "trips ~ HVI_Score", usually treated as numeric trend or categorical.
    # Let's try numeric first to see the trend direction.
    
    try:
        model = smf.glm(formula="total_trips ~ HVI_Score", data=df, family=sm.families.Poisson())
        result = model.fit()
        
        print(result.summary())
        
        # Interpretation
        coef_hvi = result.params['HVI_Score']
        print(f"\nInterpretation:")
        print(f"HVI Coefficient: {coef_hvi:.4f}")
        print(f"Effect: For every 1 unit increase in HVI, expected trips change by factor of {np.exp(coef_hvi):.4f}")
    except Exception as e:
        print(f"Regression failed: {e}")

if __name__ == "__main__":
    run_analysis()
