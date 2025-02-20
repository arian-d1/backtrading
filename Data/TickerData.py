import yfinance as yf
import datetime

# Define the ticker symbol
ticker = 'SPY'

# Get today's date
end_date = datetime.datetime.now().date()

# Calculate the start date (one year ago)
start_date = end_date - datetime.timedelta(days=365)

# Download the data
data = yf.download(ticker, start=start_date, end=end_date, interval='1d')

# Save to CSV
file_name = "SPY_data_365d.csv"
data.to_csv(file_name)

print(f"Data saved to {file_name}")