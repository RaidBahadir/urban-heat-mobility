"""
DSA 210 Final Project - Data Loader & Pipeline
Author: [Your Name]

This script executes the data engineering pipeline:
1. Loads raw Citi Bike trip CSVs (chunked/globbed).
2. Aggregates trips by station.
3. Performs a Spatial Join (Point-In-Polygon) to map Stations -> Zip Codes.
4. Enriches station data with Heat Vulnerability Index (HVI) scores.
5. Exports the final dataset for analysis.
"""
import pandas as pd
import geopandas as gpd
from shapely.geometry import Point
import os
import glob

def load_and_process_data(
    trips_pattern='202408-citibike-tripdata_*.csv', 
    geojson_path='nyc-zip-code-tabulation-areas-polygons.geojson',
    hvi_path='Heat_Vulnerability_Index_Rankings_20251130.csv',
    output_path='final_station_data.csv'
):
    """
    Loads Citi Bike trips (multiple files), performs spatial join with Zip Codes, 
    merges with HVI data, and exports the final dataset.
    """
    print("--- Starting Data Processing ---")
    
    # 1. Load Citi Bike Data
    print(f"Looking for Trip files matching: {trips_pattern}")
    trip_files = glob.glob(trips_pattern)
    
    if not trip_files:
        raise FileNotFoundError(f"No files found matching pattern: {trips_pattern}")
        
    print(f"Found {len(trip_files)} files: {trip_files}")
    
    dfs = []
    for f in trip_files:
        print(f"Loading {f}...")
        dfs.append(pd.read_csv(f))
        
    print("Concatenating trip data...")
    df_trips = pd.concat(dfs, ignore_index=True)
    print(f"Total trips loaded: {len(df_trips)}")
    
    # Group by Station to get Trip Counts and Location
    print("Aggregating trips by station...")
    # Ensure columns exist
    if 'start_station_name' not in df_trips.columns:
         # Try to handle potential column name variations if needed
         pass

    # Count trips
    station_counts = df_trips.groupby('start_station_name').size().reset_index(name='total_trips')
    
    # Get Location (Lat/Lon) - taking first occurrence
    station_locs = df_trips.groupby('start_station_name')[['start_lat', 'start_lng']].first().reset_index()
    
    # Merge
    df_stations = pd.merge(station_counts, station_locs, on='start_station_name')
    
    # Create GeoDataFrame (Points)
    geometry = [Point(xy) for xy in zip(df_stations.start_lng, df_stations.start_lat)]
    gdf_stations = gpd.GeoDataFrame(df_stations, geometry=geometry)
    # Citi Bike lat/lon is WGS84
    gdf_stations.set_crs(epsg=4326, inplace=True)
    print(f"Created GeoDataFrame with {len(gdf_stations)} stations.")

    # 2. Load Zip Code Polygons
    print(f"Loading GeoJSON from {geojson_path}...")
    if not os.path.exists(geojson_path):
        raise FileNotFoundError(f"File not found: {geojson_path}")
        
    gdf_zips = gpd.read_file(geojson_path)
    # Ensure CRS matches (GeoJSON is usually 4326, but good to check/convert)
    if gdf_zips.crs != gdf_stations.crs:
        print(f"Re-projecting Zip Codes from {gdf_zips.crs} to {gdf_stations.crs}...")
        gdf_zips = gdf_zips.to_crs(gdf_stations.crs)

    # 3. Spatial Join (Points in Polygons)
    print("Performing Spatial Join...")
    # We want to know which Zip Code each Station is in.
    # gdf_zips should have a column like 'postalCode'
    
    gdf_joined = gpd.sjoin(gdf_stations, gdf_zips, how="left", predicate="within")
    
    # Check for unmatched stations
    unmatched = gdf_joined['postalCode'].isna().sum()
    if unmatched > 0:
        print(f"Warning: {unmatched} stations fell outside NYC Zip Code boundaries.")
    
    # Keep relevant columns
    # We need 'postalCode' to merge with HVI
    gdf_joined = gdf_joined[['start_station_name', 'total_trips', 'start_lat', 'start_lng', 'postalCode', 'geometry']]
    
    # 4. Load HVI Data
    print(f"Loading HVI Data from {hvi_path}...")
    if not os.path.exists(hvi_path):
        raise FileNotFoundError(f"File not found: {hvi_path}")
        
    df_hvi = pd.read_csv(hvi_path)
    
    # Clean HVI Data
    # We need to match 'postalCode' (string) with HVI Zip Code.
    # Check HVI columns. Expected: "ZIP Code Tabulation Area (ZCTA) 2020" and "Heat Vulnerability Index (HVI)"
    
    # Normalize column names
    hvi_zip_col = None
    hvi_score_col = None
    
    for col in df_hvi.columns:
        if 'zip' in col.lower() and 'code' in col.lower():
            hvi_zip_col = col
        if 'heat' in col.lower() and 'index' in col.lower():
            hvi_score_col = col
            
    if not hvi_zip_col or not hvi_score_col:
        print(f"Columns in HVI file: {df_hvi.columns}")
        raise ValueError("Could not identify Zip Code or HVI Score columns in HVI file.")
        
    print(f"Using HVI columns: Zip='{hvi_zip_col}', Score='{hvi_score_col}'")
    
    # Rename for clarity
    df_hvi = df_hvi.rename(columns={hvi_zip_col: 'zip_code', hvi_score_col: 'HVI_Score'})
    
    # Ensure zip_code is string for merging
    df_hvi['zip_code'] = df_hvi['zip_code'].astype(str)
    gdf_joined['postalCode'] = gdf_joined['postalCode'].astype(str)
    
    # 5. Merge Station Data with HVI
    print("Merging Station Data with HVI...")
    final_df = pd.merge(gdf_joined, df_hvi[['zip_code', 'HVI_Score']], left_on='postalCode', right_on='zip_code', how='left')
    
    # Drop stations with missing HVI (if any)
    missing_hvi = final_df['HVI_Score'].isna().sum()
    if missing_hvi > 0:
        print(f"Warning: {missing_hvi} stations do not have HVI data (likely no matching Zip Code in HVI file).")
        # Optional: Drop them for analysis
        final_df = final_df.dropna(subset=['HVI_Score'])
        
    # 6. Export
    print(f"Exporting to {output_path}...")
    final_df.to_csv(output_path, index=False)
    print("Done.")
    
    return final_df

if __name__ == "__main__":
    try:
        load_and_process_data()
    except Exception as e:
        print(f"Error: {e}")
