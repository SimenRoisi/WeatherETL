You are not create a weather ETL pipeline, extracting data from yr.no and open-meteo.com, transforming the data and loading it into a database. The goal here is to create an end to end pipeline that can be used to extract weather data and store it in a database. The goal is to prove my knowledge of ETL pipelines and data engineering for my resumé.
The problem we are solving here is systematical deviations between the weather data from yr.no and open-meteo.com. This pipeline will normalize, compare and aggregate prognosis' to give a more robust estimate. 
Make no mistake, the project is about proving my knowledge of ETL pipelines and data engineering for my resumé. The project is not about proving the accuracy of the weather data.

Extract:
We want to extract different APIs, different timezones, different coordinate formats and different variable names.

Transform:
Time normalization, spacial normalization (lat/lon vs location names), unit convertion (m/s vs km/h, mm vs cm, etc), variable normalization (precipitation vs precipitation_amount), data quality such as missing values, outliers, etc.

Load:
Raw tables per source, normalized tables per source, aggregated views, indexing for time and location queries.

Aggregation:
Suggestions: Simple average as baseline, weighted average based on historic deviation and source. Confidence interval based on historic deviation and source.

API we publish:
Examples:

/weather/current?lat=..&lon=..

/weather/daily-average?location=Oslo

/weather/source-deviation?date=2026-01-10