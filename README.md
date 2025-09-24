# Supermarket Sales Forecasting Dashboard

This project is a Streamlit application designed to visualize and forecast sales data from a supermarket. It provides an interactive dashboard that allows users to filter sales data by various parameters and view key performance indicators (KPIs) and visualizations.

## Project Structure

```
supermarket-streamlit-forecast
├── src
│   ├── Supermarkt.py          # Main Streamlit application code
│   ├── data_loader.py         # Data loading and preprocessing functions
│   ├── forecasting.py         # Time series forecasting implementation
│   ├── utils.py               # Utility functions for data handling
│   └── requirements.txt       # Python dependencies
│   └── __init__.py       
                     
├── data
│   └── Supermarket.xlsx       # Excel file containing sales data
├── models
│   └── .gitkeep               # Placeholder for future model files
├── tests
│   └── test_forecasting.py    # Unit tests for forecasting functionality
├── .streamlit
│   └── config.toml            # Streamlit configuration settings
└── README.md                  # Project documentation
```

## Installation

To run this project, you need to have Python installed on your machine. Follow these steps to set up the project:

1. Clone the repository:
   ```
   git clone <repository-url>
   cd supermarket-streamlit-forecast
   ```

2. Create a virtual environment (optional but recommended):
   ```
   python -m venv venv
   source venv/bin/activate  # On Windows use `venv\Scripts\activate`
   ```

3. Install the required packages:
   ```
   pip install -r src/requirements.txt
   ```

## Usage

1. Ensure that the `Supermarket.xlsx` file is located in the `data` directory.
2. Run the Streamlit application:
   ```
   streamlit run src/Supermarkt.py
   ```

3. Open your web browser and navigate to `http://localhost:8501` to view the dashboard.

## Features

- **Data Filtering**: Filter sales data by city, customer type, and gender.
- **Sales Visualizations**: View sales data through various charts, including total sales, average ratings, and sales by product line.
- **Forecasting**: Utilize time series forecasting to predict future sales trends based on historical data.

## Contributing

Contributions are welcome! Please open an issue or submit a pull request for any enhancements or bug fixes.

## License

This project is licensed under the MIT License. See the [LICENSE file](https://github.com/phunhm9798-collab/supermarket-streamlit-forecast/blob/fad8e84752ebb80c8dcbdbd53393ef47d5a4aa78/LICENSE) for more details.
