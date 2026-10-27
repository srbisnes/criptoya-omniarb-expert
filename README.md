# CryptoYa OmniArb Expert

**El mejor arquitecto web3 omnichaín de arbitrajes LatAm.**

Sistema experto en detección de oportunidades de arbitraje que se alimenta **100% de la API pública de CryptoYa** (`https://criptoya.com/api`). Combina:

- **Web2**: Scanner en tiempo real + dashboard
- **Web3**: Smart contract de escrow/settlement omnichaín (LayerZero-ready)
- **AI**: Análisis de riesgo y ranking de oportunidades (integrable con LLMs)
- **Fintech / Tokens**: Cálculo de profit neto considerando fees, volumen y cross-fiat
- **Layers 0-1-2-3**: Arquitectura preparada para settlement via LayerZero, Axelar o CCTP

## Arquitectura

```
[CryptoYa API] → Scanner (Python/Next.js Edge) → Detector de Arb
                                      ↓
                         Dashboard Web3 (Next.js + Wagmi)
                                      ↓
                    Smart Contract Escrow (Solidity + LayerZero)
                                      ↓
                           Settlement Omnichaín + Notificaciones
```

### Endpoints CryptoYa usados
- `GET /api/{coin}/{fiat}/{volumen}` → Cotizaciones agregadas de todos los exchanges
- `GET /api/{exchange}/{coin}/{fiat}/{volumen}` → Detalle por exchange
- `GET /api/fees` → Fees de retiro
- `GET /api/dolar` → Cotizaciones oficiales / blue / cripto para cross-rate

## Cómo funciona el arbitraje

1. Fetch de todas las cotizaciones para un par (ej: USDT/ARS volumen 1000)
2. Filtra quotes válidas (ask/bid > 0, timestamps frescos)
3. Encuentra el **mínimo totalAsk** (mejor compra) y **máximo totalBid** (mejor venta)
4. Calcula spread y profit % neto estimado
5. Rankea oportunidades por profit, liquidez y riesgo
6. Opcional: propone ruta de settlement on-chain

## Setup local

```bash
# Python scanner
pip install requests
python scripts/arb_scanner.py --coin USDT --fiat ARS --volume 1000 --min-profit 0.5

# Frontend (Next.js)
cd frontend
pnpm install
pnpm dev
```

## Deploy

- Frontend: Vercel (push a main)
- Contracts: Foundry (`forge build && forge test`)

## Innovación Elcryptoboy

- Detector de arbs CEX-P2P y cross-exchange en mercados LatAm
- Integración nativa con CryptoYa (sin API keys)
- Preparado para ejecución omnichaín y account abstraction
- Listo para presentar a fintechs, bancos y protocolos

**API Base**: https://criptoya.com/api  
**Docs**: https://docs.criptoya.com
