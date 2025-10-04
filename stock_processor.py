import requests
from datetime import datetime, timedelta
from typing import List, Dict


class StockProcessor:
    def __init__(self, quote_url: str, bars_url: str):
        self.quote_url = quote_url
        self.bars_url = bars_url
        self.quote = None
        self.bars = []
        
    def fetch_data(self):
        self.quote = requests.get(self.quote_url).json()
        self.bars = requests.get(self.bars_url).json()
        
    def fill_missing_bars_and_calculate_change(self) -> Dict:
        self.fetch_data()
        
        filled_bars = self._fill_missing_bars()
        bars_with_change = self._calculate_bar_changes(filled_bars)
        day_change = self.quote['last'] - self.quote['previousClose']
        day_percent_change = (day_change / self.quote['previousClose']) * 100
        
        return {
            "change": round(day_change, 2),
            "percentChange": round(day_percent_change, 2),
            "bars": bars_with_change
        }
    
    def _fill_missing_bars(self) -> List[Dict]:
        sorted_bars = sorted(self.bars, key=lambda x: x['startDateTime'])
        
        start_time = datetime.fromisoformat("2025-02-19T09:30:00-05:00")
        end_time = datetime.fromisoformat("2025-02-19T16:00:00-05:00")
        interval_minutes = 5
        
        filled_bars = []
        current_time = start_time
        bar_index = 0
        previous_bar = None
        
        while current_time <= end_time:
            next_time = current_time + timedelta(minutes=interval_minutes)
            current_time_str = current_time.isoformat()
            
            if bar_index < len(sorted_bars) and sorted_bars[bar_index]['startDateTime'] == current_time_str:
                filled_bars.append(sorted_bars[bar_index])
                previous_bar = sorted_bars[bar_index]
                bar_index += 1
            else:
                if previous_bar:
                    filled_bars.append({
                        'startDateTime': current_time_str,
                        'endDateTime': next_time.isoformat(),
                        'open': previous_bar['close'],
                        'close': previous_bar['close'],
                        'high': previous_bar['close'],
                        'low': previous_bar['close']
                    })
                else:
                    filled_bars.append({
                        'startDateTime': current_time_str,
                        'endDateTime': next_time.isoformat(),
                        'open': self.quote['open'],
                        'close': self.quote['open'],
                        'high': self.quote['open'],
                        'low': self.quote['open']
                    })
                    previous_bar = filled_bars[-1]
            
            current_time = next_time
        
        return filled_bars
    
    def _calculate_bar_changes(self, bars: List[Dict]) -> List[Dict]:
        result = []
        previous_close = self.quote['previousClose']
        
        for bar in bars:
            change = bar['close'] - previous_close
            percent_change = (change / previous_close) * 100
            
            result.append({
                'dateTime': bar['startDateTime'],
                'open': bar['open'],
                'close': bar['close'],
                'change': round(change, 2),
                'percentChange': round(percent_change, 2)
            })
            
            previous_close = bar['close']
        
        return result
