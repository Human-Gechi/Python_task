# Airbnb Data Deep Dive – Python + Pandas Challenge (London)

## Project Overview

This project applies Python and Pandas to analyze Airbnb listing data for **London**.
The goal is to clean, transform, and analyze the dataset to uncover patterns, provide insights, and answer key analytical questions about Airbnb listings in Paris.

---

## Dataset

- Source: [Inside Airbnb](http://insideairbnb.com/get-the-data.html)
- City: London
- File used: `listings.csv`
- The dataset includes information about hosts,listings,reviews ,prices, availability, etc

---

## Project Tasks

### 1. Data Loading and Initial Exploration
- Loaded the dataset using Pandas.
- Explored basic structure using:
  - `.info()`
  - `.describe()`
  - `.head()`
- Checked for:
  - Missing values
  - Duplicated rows
  - Unusual data types

### 2. Data Cleaning
- Converted price columns (e.g., `"$2,100.00"`) to numeric floats.
- Parsed date fields (e.g., `last_review`) into `datetime` objects.
- Handled missing values in critical fields:
  - `reviews_per_month` → replaced NaNs with 0
  - `host_name` → filled with `"Unknown"`
  - `neighbourhood_group` → handled missing entries
- Removed irrelevant rows:
  - Listings with `availability_365 = 0`
  - Listings with `price <= 0`

### 3. Data Enrichment
- Created a `price_per_booking` column using `price` and `minimum_nights`.
- Categorized listings based on availability:
  - **Full-time:** availability > 300
  - **Part-time:** 100–300
  - **Rare:** < 100

### 4. Data Analysis Using Pandas
Performed analysis and answered key questions:

1. **Top 10 most expensive neighborhoods by average price**
   - Calculated average price per neighborhood and sorted descending.

2. **Average availability and price by room type**
   - Grouped by `room_type` and calculated mean of `price` and `availability_365`.

3. **Hosts with the most listings**
   - Counted listings per `host_name` and sorted descending.

4. **Average price variation across districts/boroughs**
   - Grouped by `neighbourhood_group` or `neighbourhood` and calculated mean price.

5. **Listings never reviewed**
   - Counted listings with `number_of_reviews = 0`.

6.

---

## Project Structure
- Airbnb_deep_dive/
  - listings.csv              #Dataset for London dataset
  - London_listings.ipynb     # Main Jupyter notebook with cleaning, enrichment, and analysis
  - README.md                 # Project documentation


