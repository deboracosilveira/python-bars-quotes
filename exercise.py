import json
from stock_processor import StockProcessor


def main():
    quote_url = "https://universal.hellopublic.com/exercises/fs/quote.json"
    bars_url = "https://universal.hellopublic.com/exercises/fs/bars.json"
    
    processor = StockProcessor(quote_url, bars_url)
    result = processor.fill_missing_bars_and_calculate_change()
    
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
