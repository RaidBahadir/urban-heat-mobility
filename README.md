# urban-heat-mobility

# DSA 210 Project: Hot Streets and Empty Bikes?

**An Analysis of Urban Heat Islands and Citi Bike Rider Behavior**

## Project Proposal

My project will investigate the relationship between the "urban heat island" (UHI) effect in New York City and the usage patterns of the Citi Bike share system.

### Motivation

I've always been interested in how our city's environment shapes our day-to-day choices. New York City gets incredibly hot in the summer, and it's well-known that some neighborhoods feel much hotter than others due to the "urban heat island" (UHI) effect.

At the same time, the city is pushing for more sustainable transport like Citi Bike. My core question is: **is it simply too hot to ride?**

I want to see if people actively avoid starting or ending bike trips in the hottest parts of the city during heat waves. If we find that UHI is a major deterrent, it could help city planners pinpoint exactly where cooling infrastructure (like planting more trees or adding shaded bike lanes) is needed most to support green transportation.

## Data and Collection Plan

As required, I will use a publicly available dataset and enrich it with a second data source.

### 1. Primary Dataset: Bike-Share Trip Data

* **Data:** NYC Citi Bike Trip Histories
* **Source:** This data is publicly available and hosted by [Citi Bike on an S3 bucket](httpss://s3.amazonaws.com/tripdata/index.html).
* **Collection Plan:** I will download the monthly CSV files for the summer months (e.g., June-August 2025). These files contain detailed trip data, including trip duration and, most importantly, the latitude and longitude for the start and end stations.

### 2. Enrichment Dataset: Land Surface Temperature (LST)

* **Data:** Land Surface Temperature (LST) satellite data. This is different from air temperature and shows the actual radiated heat from surfaces (like asphalt and rooftops), which is the core of the UHI effect.
* **Source:** This data is publicly available from the [USGS EarthExplorer](httpss://earthexplorer.usgs.gov/). I will use data from the Landsat 8 or 2 satellite.
* **Collection Plan:** I will download Landsat 8 or 2 satellite images for the NYC area from the same summer period. Using Python, I will process these images (which come in GeoTIFF format) to create a high-resolution map of the hottest and coolest areas of the city. I will then be able to link the Citi Bike station locations to this UHI map to see which stations are in "hotspots."

### 3. (If Needed) Enrichment Dataset #2: Hourly Air Temperature

* **Data:** Hourly weather data (air temperature, humidity, precipitation).
* **Source:** A public weather API, such as [Visual Crossing](httpss://www.visualcrossing.com/) or OpenWeatherMap.
* **Collection Plan:** While LST is my main focus, I will also pull hourly weather data. This will allow me to control for general weather conditions (e.g., "was it just a hot day everywhere?" or "was it raining?") and see how the specific UHI hotspots compare.

## Analysis Plan & Methodology

My plan isn't just to download the data; I need to make it all communicate to each other.

1.  **Data Preparation:** The first step is to combine these different datasets. My plan is to use Python (likely with libraries like `pandas` and `geopandas`) to "tag" each Citi Bike station with its corresponding LST value from the satellite map. I'll probably have to draw a small circle (like a 300-meter buffer) around each station's coordinates and find the average LST in that circle. Then, I'll merge this with the trip data and the hourly weather API data, so every single trip has a "start station UHI" and "hourly air temp" associated with it.

2.  **Exploratory Data Analysis (EDA):** Once the data is merged, I'll start exploring. The first thing I'll do is make a map of NYC with the LST data as a heatmap and plot the Citi Bike stations on top. This will instantly show which stations are in the hottest areas. I'll also create plots to see how trip counts change on hot days vs. cool days, and if that change is more extreme in the UHI "hotspots."

3.  **Machine Learning:** For the machine learning part, my main goal is to see *how much* the heat matters. I'm planning to build a regression model to predict the number of bike trips starting from a station in a given hour.
    * My **features** will be things like: time of day, day of the week, is it a weekend, air temperature, humidity, precipitation, and of course, the **LST value** for that station's zone.
    * Since trip counts are numbers like 0, 1, 2... (what's called "count data"), a simple linear regression isn't the best fit. I'll plan to use a **Poisson or Negative Binomial regression**, which is designed for this kind of data. This will help me see if LST is a statistically significant predictor of ride counts, even when controlling for all those other factors.

## Known Limitations (and potential challenges)

I know this plan isn't perfect, and currently there are a few big challenges I'll need to address in my final report:

* **The "Snapshot vs. Real-Time" Problem:** This is the biggest challenge. Landsat satellites give amazing detail, but they only pass over NYC every 16 days. So, the LST map will show *where* it's consistently hot, but it can't tell me the temperature at 2 PM on a specific Tuesday. This means I'll have to be very careful to use the LST map for *spatial* analysis (hot zones) and the hourly weather API for the *temporal* "what's the weather *right now*" analysis.
* **Correlation vs. Causation:** This project will show if there's a link (correlation) between heat and bike-share use. I can't definitively prove that a person *chose* not to ride *because* of the heat. They might have taken the subway for other reasons. I will have to be very careful in my report to say "is associated with" instead of "causes."
* **LST vs. Air Temp:** The satellite measures *ground* heat (asphalt, roofs), which can be much hotter than the "feels like" air temperature a rider actually experiences. I'll need to discuss this difference in my findings.

## Ethics and Licensing

* **Privacy:** The Citi Bike data is already pretty well anonymized; it doesn't contain personal rider information, just trip times and locations. I will not be doing any analysis that could try to de-anonymize or track individual users.
* **Licensing:** All the data sources I plan to use are public. The Citi Bike data is provided under their own [data license agreement](httpss://ride.citibikenyc.com/data-sharing-policy), and the USGS Landsat data is in the public domain. I will make sure to properly cite all my data sources in my final report.
* **Academic Integrity Note:** As per the course guidelines, I am documenting my use of AI. I used a large language model (LLM) to help me refine the structure and the grammar of this proposal document.

## Reproduction Instructions
To reproduce this analysis on your local machine:

1.  **Clone the Repository**:
    ```bash
    git clone https://github.com/RaidBahadir/urban-heat-mobility.git
    cd urban-heat-mobility
    ```

2.  **Download Data**:
    -   **Citi Bike**: Download the August 2024 zip files from [Citi Bike Data](https://s3.amazonaws.com/tripdata/index.html).
    -   **Unzip**: Extract the CSV files directly into the **root directory** of this project.
    -   **Naming**: Ensure files match the pattern `202408-citibike-tripdata_*.csv`. (e.g., `202408-citibike-tripdata_1.csv`, etc.).

3.  **Install Dependencies**:
    ```bash
    pip install -r requirements.txt
    ```

4.  **Run the Pipeline**:
    -   **Step 1: Process Data**:
        ```bash
        python data_loader.py
        ```
        *This will generate `final_station_data.csv`.*

    -   **Step 2: Generate Visuals**:
        ```bash
        python generate_plots.py
        ```
        *This will save `hvi_map.png` and `hvi_boxplot.png`.*

    -   **Step 3: Run Analysis**:
        ```bash
        python analysis.py
        ```
        *This will print the statistical results to the console.*
