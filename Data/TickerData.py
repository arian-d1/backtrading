import yfinance as yf
import datetime

def getTickerData(ticker, period):
    # Get today's dte
    endDate = datetime.datetime.now().date()

    # Calculate the start date (one year ago)
    startDate = endDate - datetime.timedelta(days=period)

    # Download the data
    data = yf.download(ticker, start=startDate, end=endDate, interval='1d')

    data.columns = ["Open", "High", "Low", "Close", "Volume"]

    # Save to CSV
    fileName = f"./data/{ticker}_data_{period}d.csv"
    data.to_csv(fileName)

    print(f"Data saved to {fileName}")

    return fileName
