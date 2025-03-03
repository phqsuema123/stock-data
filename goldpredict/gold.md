# Gold Price Forecasting Analysis

## Overview
This project focuses on analyzing historical gold price data and forecasting future prices using different models. The dataset includes monthly gold prices spanning multiple decades.

## Data Preprocessing
- The dataset is loaded and the date column is converted into a datetime format.
- Monthly data is indexed for time series analysis.
- The dataset is split into training and testing sets for model evaluation.

## Data Analysis
- Visualizations of gold prices over time.
- Boxplot analysis of gold prices by year to identify trends and variations.
- Summary statistics for yearly, quarterly, and decade-based aggregations.

## Forecasting Models
1. **Linear Regression Model:**
   - Trained using time as the independent variable.
   - Predictions are made on the test dataset.
   - Performance is evaluated using Mean Absolute Percentage Error (MAPE).

2. **Naive Forecast Model:**
   - Uses the last observed value as the forecast for future prices.
   - Compared against the linear regression model using MAPE.

## 10-Year Forecast
- A naive forecast is extended for 10 years into the future.
- Confidence intervals (±5%) are included for uncertainty estimation.
- Future price predictions are stored in a dataframe.

## Results
- The naive forecast performed better than the linear regression model based on MAPE.
- The 10-year forecast predicts stable prices based on the last observed value.
- Visualizations illustrate historical trends and future expectations.

## Usage
To replicate this analysis:
1. Load the dataset.
2. Ensure dependencies such as `pandas`, `matplotlib`, and `sklearn` are installed.
3. Run the scripts to perform analysis and forecasting.

## Future Work
- Implement advanced time-series models like ARIMA, LSTM, or Prophet for improved accuracy.
- Evaluate external factors influencing gold prices, such as inflation or market indices.
- Improve confidence interval estimations with statistical techniques.

## Author
This project was created for gold price trend analysis and forecasting. Contributions and improvements are welcome!

