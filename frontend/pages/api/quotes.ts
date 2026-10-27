import type { NextApiRequest, NextApiResponse } from 'next';

export default async function handler(req: NextApiRequest, res: NextApiResponse) {
  const { coin = 'USDT', fiat = 'ARS', volume = '1000' } = req.query;
  try {
    const url = `https://criptoya.com/api/${coin}/${fiat}/${volume}`;
    const r = await fetch(url);
    const data = await r.json();
    res.status(200).json(data);
  } catch (e) {
    res.status(500).json({ error: 'Failed to fetch CryptoYa' });
  }
}
