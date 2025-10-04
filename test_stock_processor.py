import pytest
from datetime import datetime
from stock_processor import StockProcessor


class TestStockProcessor:
    @pytest.fixture
    def mock_quote(self):
        return {
            "open": 408.94,
            "high": 409.93,
            "low": 407.74,
            "last": 407.925,
            "previousClose": 409.64
        }
    
    @pytest.fixture
    def mock_bars_with_single_gap(self):
        return [
            {
                "startDateTime": "2025-02-19T09:30:00-05:00",
                "endDateTime": "2025-02-19T09:35:00-05:00",
                "open": 407.88,
                "close": 408.695,
                "high": 409.07,
                "low": 407.65
            },
            {
                "startDateTime": "2025-02-19T09:40:00-05:00",
                "endDateTime": "2025-02-19T09:45:00-05:00",
                "open": 408.6,
                "close": 408.775,
                "high": 409.45,
                "low": 408.6
            }
        ]
    
    @pytest.fixture
    def mock_bars_with_multiple_gaps(self):
        return [
            {
                "startDateTime": "2025-02-19T09:30:00-05:00",
                "endDateTime": "2025-02-19T09:35:00-05:00",
                "open": 407.88,
                "close": 408.695,
                "high": 409.07,
                "low": 407.65
            },
            {
                "startDateTime": "2025-02-19T09:50:00-05:00",
                "endDateTime": "2025-02-19T09:55:00-05:00",
                "open": 409.1,
                "close": 409.005,
                "high": 409.93,
                "low": 408.89
            }
        ]
    
    @pytest.fixture
    def mock_bars_with_first_bar_missing(self):
        return [
            {
                "startDateTime": "2025-02-19T09:35:00-05:00",
                "endDateTime": "2025-02-19T09:40:00-05:00",
                "open": 408.6,
                "close": 408.775,
                "high": 409.45,
                "low": 408.6
            }
        ]
    
    @pytest.fixture
    def mock_bars_for_complete_flow(self):
        return [
            {
                "startDateTime": "2025-02-19T09:30:00-05:00",
                "endDateTime": "2025-02-19T09:35:00-05:00",
                "open": 407.88,
                "close": 408.695,
                "high": 409.07,
                "low": 407.65
            },
            {
                "startDateTime": "2025-02-19T09:40:00-05:00",
                "endDateTime": "2025-02-19T09:45:00-05:00",
                "open": 408.6,
                "close": 408.775,
                "high": 409.45,
                "low": 408.6
            }
        ]
    
    @pytest.fixture
    def mock_bars_for_change_calculation(self):
        return [
            {
                'startDateTime': "2025-02-19T09:30:00-05:00",
                'open': 407.88,
                'close': 408.695
            },
            {
                'startDateTime': "2025-02-19T09:35:00-05:00",
                'open': 408.695,
                'close': 408.775
            }
        ]
    
    def test_single_missing_bar_is_filled_correctly(self, mock_quote, mock_bars_with_single_gap):
        processor = StockProcessor("", "")
        processor.quote = mock_quote
        processor.bars = mock_bars_with_single_gap
        
        filled = processor._fill_missing_bars()
        
        assert len(filled) == 79
        assert filled[0]['startDateTime'] == "2025-02-19T09:30:00-05:00"
        assert filled[1]['startDateTime'] == "2025-02-19T09:35:00-05:00"
        assert filled[1]['open'] == 408.695
        assert filled[1]['close'] == 408.695
        assert filled[2]['startDateTime'] == "2025-02-19T09:40:00-05:00"
    
    def test_multiple_consecutive_missing_bars_are_filled_correctly(self, mock_quote, mock_bars_with_multiple_gaps):
        processor = StockProcessor("", "")
        processor.quote = mock_quote
        processor.bars = mock_bars_with_multiple_gaps
        
        filled = processor._fill_missing_bars()
        
        assert len(filled) == 79
        assert filled[0]['startDateTime'] == "2025-02-19T09:30:00-05:00"
        assert filled[1]['startDateTime'] == "2025-02-19T09:35:00-05:00"
        assert filled[1]['close'] == 408.695
        assert filled[2]['startDateTime'] == "2025-02-19T09:40:00-05:00"
        assert filled[2]['close'] == 408.695
        assert filled[3]['startDateTime'] == "2025-02-19T09:45:00-05:00"
        assert filled[3]['close'] == 408.695
        assert filled[4]['startDateTime'] == "2025-02-19T09:50:00-05:00"
    
    def test_first_bar_of_day_uses_quote_open_when_missing(self, mock_quote, mock_bars_with_first_bar_missing):
        processor = StockProcessor("", "")
        processor.quote = mock_quote
        processor.bars = mock_bars_with_first_bar_missing
        
        filled = processor._fill_missing_bars()
        
        assert len(filled) == 79
        assert filled[0]['startDateTime'] == "2025-02-19T09:30:00-05:00"
        assert filled[0]['open'] == mock_quote['open']
        assert filled[0]['close'] == mock_quote['open']
        assert filled[1]['startDateTime'] == "2025-02-19T09:35:00-05:00"
    
    def test_bar_changes_are_calculated_relative_to_previous_close(self, mock_quote, mock_bars_for_change_calculation):
        processor = StockProcessor("", "")
        processor.quote = mock_quote
        
        result = processor._calculate_bar_changes(mock_bars_for_change_calculation)
        
        assert len(result) == 2
        assert result[0]['change'] == round(408.695 - 409.64, 2)
        assert result[0]['percentChange'] == round(((408.695 - 409.64) / 409.64) * 100, 2)
        assert result[1]['change'] == round(408.775 - 408.695, 2)
        assert result[1]['percentChange'] == round(((408.775 - 408.695) / 408.695) * 100, 2)
    
    def test_day_change_is_calculated_from_previous_day_close(self, mock_quote):
        processor = StockProcessor("", "")
        processor.quote = mock_quote
        
        day_change = mock_quote['last'] - mock_quote['previousClose']
        expected_change = round(day_change, 2)
        expected_percent = round((day_change / mock_quote['previousClose']) * 100, 2)
        
        assert expected_change == round(407.925 - 409.64, 2)
        assert expected_percent == round(((407.925 - 409.64) / 409.64) * 100, 2)
    
    def test_complete_flow_fills_gaps_and_calculates_changes(self, mock_quote, mock_bars_for_complete_flow):
        processor = StockProcessor("", "")
        processor.quote = mock_quote
        processor.bars = mock_bars_for_complete_flow
        
        filled = processor._fill_missing_bars()
        result = processor._calculate_bar_changes(filled)
        
        assert len(result) == 79
        assert result[0]['dateTime'] == "2025-02-19T09:30:00-05:00"
        assert result[0]['open'] == 407.88
        assert result[0]['close'] == 408.695
        assert 'change' in result[0]
        assert 'percentChange' in result[0]
