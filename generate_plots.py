
import pandas as pd
import geopandas as gpd
import matplotlib.pyplot as plt
import seaborn as sns
import os

def generate_plots():
    print("Generating EDA plots...")
    
    # Load Data
    if not os.path.exists('final_station_data.csv'):
        print("Error: final_station_data.csv not found.")
        return

    df = pd.read_csv('final_station_data.csv')
    
    # Create GeoDataFrame
    gdf_stations = gpd.GeoDataFrame(
        df, geometry=gpd.points_from_xy(df.start_lng, df.start_lat), crs="EPSG:4326"
    )
    
    # Load Zip Codes
    gdf_zips = gpd.read_file('nyc-zip-code-tabulation-areas-polygons.geojson')
    gdf_zips = gdf_zips.to_crs(gdf_stations.crs)
    
    # Load HVI
    hvi_df = pd.read_csv('Heat_Vulnerability_Index_Rankings_20251130.csv')
    
    # Normalize columns
    hvi_zip_col = 'ZIP Code Tabulation Area (ZCTA) 2020'
    hvi_score_col = 'Heat Vulnerability Index (HVI)'
    
    hvi_df.rename(columns={hvi_zip_col: 'zip_code', hvi_score_col: 'HVI_Score'}, inplace=True)
    hvi_df['zip_code'] = hvi_df['zip_code'].astype(str)
    gdf_zips['postalCode'] = gdf_zips['postalCode'].astype(str)
    
    # Merge for Map
    gdf_zips_hvi = gdf_zips.merge(hvi_df, left_on='postalCode', right_on='zip_code', how='left')
    
    # Plot 1: HVI Map
    print("Saving hvi_map.png...")
    fig, ax = plt.subplots(figsize=(12, 12))
    gdf_zips_hvi.plot(column='HVI_Score', cmap='OrRd', legend=True, ax=ax, edgecolor='lightgrey', 
                      missing_kwds={'color': 'lightgrey'}, legend_kwds={'label': "HVI Score"})
    gdf_stations.plot(ax=ax, color='blue', markersize=2, alpha=0.3, label='Citi Bike Stations')
    plt.title('NYC Heat Vulnerability Index (HVI) & Citi Bike Stations')
    plt.axis('off')
    plt.savefig('hvi_map.png', dpi=300, bbox_inches='tight')
    plt.close()
    
    # Plot 2: Boxplot
    print("Saving hvi_boxplot.png...")
    plt.figure(figsize=(10, 6))
    sns.boxplot(data=df, x='HVI_Score', y='total_trips')
    plt.yscale('log')
    plt.title('Distribution of Trip Counts by HVI Score')
    plt.ylabel('Total Trips (Log Scale)')
    plt.xlabel('HVI Score (1=Low Risk, 5=High Risk)')
    plt.savefig('hvi_boxplot.png', dpi=300, bbox_inches='tight')
    plt.close()
    
    print("Done. Images saved.")

if __name__ == "__main__":
    generate_plots()
