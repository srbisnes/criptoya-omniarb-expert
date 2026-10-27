import { useEffect, useState } from 'react';

interface Opportunity {
  buy_exchange: string;
  sell_exchange: string;
  buy_price: number;
  sell_price: number;
  profit_pct: number;
  profit_amount: number;
}

export default function Home() {
  const [opps, setOpps] = useState<Opportunity[]>([]);
  const [loading, setLoading] = useState(false);
  const [coin, setCoin] = useState('USDT');
  const [fiat, setFiat] = useState('ARS');
  const [volume, setVolume] = useState(1000);

  const scan = async () => {
    setLoading(true);
    try {
      const r = await fetch(`/api/quotes?coin=${coin}&fiat=${fiat}&volume=${volume}`);
      const quotes = await r.json();
      // Simple client-side detection
      const valid: any[] = [];
      Object.entries(quotes).forEach(([ex, q]: [string, any]) => {
        if (q.totalAsk > 0 && q.totalBid > 0) {
          valid.push({ exchange: ex, ask: q.totalAsk, bid: q.totalBid });
        }
      });
      if (valid.length >= 2) {
        const bestBuy = valid.reduce((a, b) => a.ask < b.ask ? a : b);
        const bestSell = valid.reduce((a, b) => a.bid > b.bid ? a : b);
        if (bestSell.bid > bestBuy.ask && bestSell.exchange !== bestBuy.exchange) {
          const profitPct = ((bestSell.bid - bestBuy.ask) / bestBuy.ask) * 100;
          const profitAmt = (bestSell.bid - bestBuy.ask) * volume;
          if (profitPct > 0.3 && profitPct < 50) {
            setOpps([{
              buy_exchange: bestBuy.exchange,
              sell_exchange: bestSell.exchange,
              buy_price: bestBuy.ask,
              sell_price: bestSell.bid,
              profit_pct: Number(profitPct.toFixed(2)),
              profit_amount: Number(profitAmt.toFixed(2)),
            }]);
            return;
          }
        }
      }
      setOpps([]);
    } catch (e) {
      console.error(e);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => { scan(); }, []);

  return (
    <div style={{ fontFamily: 'system-ui', padding: '2rem', background: '#0a0a0a', color: '#fff', minHeight: '100vh' }}>
      <h1>CryptoYa OmniArb Expert</h1>
      <p>Alimentado 100% por <a href="https://criptoya.com/api" style={{color:'#0f0'}}>criptoya.com/api</a></p>
      
      <div style={{ display: 'flex', gap: '1rem', margin: '1.5rem 0' }}>
        <input value={coin} onChange={e => setCoin(e.target.value)} placeholder="Coin" />
        <input value={fiat} onChange={e => setFiat(e.target.value)} placeholder="Fiat" />
        <input type="number" value={volume} onChange={e => setVolume(Number(e.target.value))} />
        <button onClick={scan} disabled={loading} style={{ padding: '0.5rem 1rem', background: '#0f0', color: '#000' }}>
          {loading ? 'Scanning...' : 'Scan Arbs'}
        </button>
      </div>

      {opps.length === 0 ? (
        <p>No opportunities above threshold. Try different volume or pair.</p>
      ) : (
        <div>
          {opps.map((o, i) => (
            <div key={i} style={{ border: '1px solid #333', padding: '1rem', margin: '0.5rem 0', borderRadius: '8px' }}>
              <strong>{coin}/{fiat}</strong> — Profit: <span style={{color:'#0f0'}}>{o.profit_pct}%</span> ({o.profit_amount} {fiat})
              <br />
              Buy on <strong>{o.buy_exchange}</strong> @ {o.buy_price.toFixed(2)}
              <br />
              Sell on <strong>{o.sell_exchange}</strong> @ {o.sell_price.toFixed(2)}
            </div>
          ))}
        </div>
      )}

      <hr style={{ margin: '2rem 0' }} />
      <h2>Omnichaín Settlement Ready</h2>
      <p>Smart contract OmniArbEscrow.sol incluido para escrow + LayerZero messaging.</p>
      <p>Arquitectura Elcryptoboy: AI + Crypto + Blockchain + Web3 + Fintech + Tokens + L0-L3</p>
    </div>
  );
}
