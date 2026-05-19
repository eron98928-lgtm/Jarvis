import yfinance as yf
import pandas as pd
import requests
from concurrent.futures import ThreadPoolExecutor, TimeoutError

class FinanceModule:
    def __init__(self):
        # Lista de índices principais das maiores economias
        self.major_indices = {
            "USA": "^GSPC",
            "Brazil": "^BVSP",
            "UK": "^FTSE",
            "Germany": "^GDAXI",
            "Japan": "^N225",
            "China": "000001.SS"
        }
        # Sessão com timeout configurado para evitar travamento da thread principal
        self.session = requests.Session()
        self.timeout = 5  # Timeout agressivo de 5 segundos

    def _fetch_ticker_data(self, ticker_symbol: str, period: str = "1d"):
        """Isola a chamada ao yfinance para permitir controle de timeout."""
        ticker = yf.Ticker(ticker_symbol, session=self.session)
        return ticker.history(period=period)

    def get_market_summary(self):
        summary = {}
        # Uso de ThreadPoolExecutor para não travar o FastAPI se o Yahoo Finance estiver lento
        with ThreadPoolExecutor(max_workers=5) as executor:
            future_to_country = {
                executor.submit(self._fetch_ticker_data, ticker): country 
                for country, ticker in self.major_indices.items()
            }
            
            for future in future_to_country:
                country = future_to_country[future]
                try:
                    data = future.result(timeout=self.timeout)
                    if not data.empty:
                        last_price = data['Close'].iloc[-1]
                        open_price = data['Open'].iloc[-1]
                        change = ((last_price - open_price) / open_price) * 100
                        summary[country] = {
                            "price": round(last_price, 2),
                            "change_pct": round(change, 2)
                        }
                    else:
                        summary[country] = {"error": "No data"}
                except TimeoutError:
                    summary[country] = {"error": "Timeout"}
                except Exception as e:
                    summary[country] = {"error": "Service Unavailable"}
        return summary

    def analyze_stock(self, ticker_symbol: str):
        try:
            with ThreadPoolExecutor(max_workers=1) as executor:
                future = executor.submit(self._fetch_ticker_data, ticker_symbol, "1mo")
                hist = future.result(timeout=self.timeout)
                
            if hist.empty:
                return {"error": "No data found"}
            
            start_price = hist['Close'].iloc[0]
            end_price = hist['Close'].iloc[-1]
            trend = "Bullish" if end_price > start_price else "Bearish"
            
            return {
                "ticker": ticker_symbol,
                "current_price": round(end_price, 2),
                "monthly_trend": trend,
                "volatility": round(hist['Close'].std(), 2)
            }
        except TimeoutError:
            return {"error": "Market data request timed out"}
        except Exception:
            return {"error": "Failed to fetch market data"}
