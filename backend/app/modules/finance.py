import yfinance as yf
import pandas as pd

class FinanceModule:
    def __init__(self):
        # List of major indices for the top 50 economies (simplified for demo)
        self.major_indices = {
            "USA": "^GSPC",
            "Brazil": "^BVSP",
            "UK": "^FTSE",
            "Germany": "^GDAXI",
            "Japan": "^N225",
            "China": "000001.SS"
        }

    def get_market_summary(self):
        summary = {}
        for country, ticker in self.major_indices.items():
            try:
                data = yf.Ticker(ticker).history(period="1d")
                if not data.empty:
                    last_price = data['Close'].iloc[-1]
                    change = ((last_price - data['Open'].iloc[-1]) / data['Open'].iloc[-1]) * 100
                    summary[country] = {
                        "price": round(last_price, 2),
                        "change_pct": round(change, 2)
                    }
            except Exception as e:
                summary[country] = {"error": str(e)}
        return summary

    def analyze_stock(self, ticker_symbol: str):
        ticker = yf.Ticker(ticker_symbol)
        hist = ticker.history(period="1mo")
        if hist.empty:
            return {"error": "No data found"}
        
        # Simple pattern identification (e.g., trend)
        start_price = hist['Close'].iloc[0]
        end_price = hist['Close'].iloc[-1]
        trend = "Bullish" if end_price > start_price else "Bearish"
        
        return {
            "ticker": ticker_symbol,
            "current_price": round(end_price, 2),
            "monthly_trend": trend,
            "volatility": round(hist['Close'].std(), 2)
        }
