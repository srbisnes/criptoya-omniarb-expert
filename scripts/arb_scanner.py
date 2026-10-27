#!/usr/bin/env python3
"""
CryptoYa OmniArb Scanner
Experto en arbitrajes alimentado 100% por https://criptoya.com/api
"""

import requests
import argparse
import time
from datetime import datetime
from typing import Dict, List, Tuple, Optional

BASE_URL = "https://criptoya.com/api"
TIMEOUT = 10

class CryptoYaArbExpert:
    def __init__(self, min_profit_pct: float = 0.3, max_spread_filter: float = 50.0):
        self.min_profit = min_profit_pct
        self.max_spread = max_spread_filter  # filtrar outliers irreales

    def fetch_quotes(self, coin: str, fiat: str, volume: float) -> Optional[Dict]:
        url = f"{BASE_URL}/{coin}/{fiat}/{volume}"
        try:
            r = requests.get(url, timeout=TIMEOUT)
            r.raise_for_status()
            data = r.json()
            if isinstance(data, dict) and "Invalid pair" not in str(data):
                return data
            return None
        except Exception as e:
            print(f"[ERROR] Fetch {coin}/{fiat}: {e}")
            return None

    def fetch_fees(self) -> Optional[Dict]:
        try:
            r = requests.get(f"{BASE_URL}/fees", timeout=TIMEOUT)
            r.raise_for_status()
            return r.json()
        except Exception as e:
            print(f"[WARN] Fees: {e}")
            return None

    def detect_opportunities(self, quotes: Dict, coin: str, fiat: str, volume: float) -> List[Dict]:
        if not quotes:
            return []

        valid = []
        now = int(time.time())
        for exchange, q in quotes.items():
            if not isinstance(q, dict):
                continue
            ask = q.get("totalAsk") or q.get("ask") or 0
            bid = q.get("totalBid") or q.get("bid") or 0
            ts = q.get("time", 0)
            # Filtros de calidad
            if ask <= 0 or bid <= 0:
                continue
            if abs(now - ts) > 300:  # >5 min viejo
                continue
            if ask > bid * 10:  # outlier extremo
                continue
            valid.append({
                "exchange": exchange,
                "ask": float(ask),
                "bid": float(bid),
                "time": ts,
            })

        if len(valid) < 2:
            return []

        # Mejor compra (min ask) y mejor venta (max bid)
        best_buy = min(valid, key=lambda x: x["ask"])
        best_sell = max(valid, key=lambda x: x["bid"])

        opportunities = []
        if best_sell["bid"] > best_buy["ask"] and best_sell["exchange"] != best_buy["exchange"]:
            profit_pct = ((best_sell["bid"] - best_buy["ask"]) / best_buy["ask"]) * 100
            if self.min_profit <= profit_pct <= self.max_spread:
                profit_amount = (best_sell["bid"] - best_buy["ask"]) * volume
                opportunities.append({
                    "coin": coin,
                    "fiat": fiat,
                    "volume": volume,
                    "buy_exchange": best_buy["exchange"],
                    "buy_price": best_buy["ask"],
                    "sell_exchange": best_sell["exchange"],
                    "sell_price": best_sell["bid"],
                    "profit_pct": round(profit_pct, 2),
                    "profit_amount": round(profit_amount, 2),
                    "timestamp": datetime.utcnow().isoformat(),
                    "type": "cross-exchange",
                })

        return opportunities

    def scan(self, coins: List[str], fiats: List[str], volume: float) -> List[Dict]:
        all_opps = []
        for coin in coins:
            for fiat in fiats:
                print(f"Scanning {coin}/{fiat} vol={volume}...")
                quotes = self.fetch_quotes(coin, fiat, volume)
                if quotes:
                    opps = self.detect_opportunities(quotes, coin, fiat, volume)
                    all_opps.extend(opps)
                time.sleep(0.5)  # respect rate limit ~120/min
        return sorted(all_opps, key=lambda x: x["profit_pct"], reverse=True)

def main():
    parser = argparse.ArgumentParser(description="CryptoYa OmniArb Expert Scanner")
    parser.add_argument("--coin", default="USDT", help="Coin (USDT, BTC, ETH...)")
    parser.add_argument("--fiat", default="ARS", help="Fiat (ARS, BRL, CLP...)")
    parser.add_argument("--volume", type=float, default=1000, help="Volume")
    parser.add_argument("--min-profit", type=float, default=0.5, help="Min profit %")
    parser.add_argument("--multi", action="store_true", help="Scan multiple pairs")
    args = parser.parse_args()

    expert = CryptoYaArbExpert(min_profit_pct=args.min_profit)

    if args.multi:
        coins = ["USDT", "USDC", "BTC", "ETH"]
        fiats = ["ARS", "BRL", "CLP", "COP", "MXN"]
        opps = expert.scan(coins, fiats, args.volume)
    else:
        quotes = expert.fetch_quotes(args.coin, args.fiat, args.volume)
        opps = expert.detect_opportunities(quotes, args.coin, args.fiat, args.volume) if quotes else []

    if not opps:
        print("No opportunities found above threshold.")
        return

    print(f"\n{'='*70}")
    print(f"OMNIARB OPPORTUNITIES FOUND: {len(opps)}")
    print(f"{'='*70}")
    for i, o in enumerate(opps[:15], 1):
        print(f"{i}. {o['coin']}/{o['fiat']} | Buy {o['buy_exchange']} @ {o['buy_price']:.2f} "
              f"→ Sell {o['sell_exchange']} @ {o['sell_price']:.2f} | "
              f"Profit: {o['profit_pct']:.2f}% (${o['profit_amount']:.2f})")

if __name__ == "__main__":
    main()
