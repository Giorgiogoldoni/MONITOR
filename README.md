# RAPTOR ETF MONITOR

Dashboard di monitoraggio holdings per 8 ETF multi-asset + CFTC COT data.

## Struttura

```
monitor/
├── .github/workflows/fetch_holdings.yml   # GitHub Actions — fetch giornaliero
├── scripts/
│   ├── fetch_holdings.py                  # Fetcher Python
│   └── build_index.py                     # Generatore index.json
├── data/
│   ├── index.json                         # Manifest snapshot disponibili
│   ├── holdings/
│   │   ├── GMOM/  RPAR/  DBMF/
│   │   ├── AOA/   AOR/   MAGR/
│   │   ├── F701/  F703/
│   │   └── (ogni file = YYYY-MM-DD.json)
│   └── cftc/
│       └── (ogni file = YYYY-MM-DD.json, venerdì)
└── index.html                             # Dashboard
```

## Setup

### 1. Crea il repository su GitHub
```bash
git init
git remote add origin https://github.com/TUOUSER/monitor.git
```

### 2. Abilita GitHub Pages
Settings → Pages → Source: **Deploy from branch** → Branch: `main` → Folder: `/ (root)`

### 3. Configura BASE_URL nella pagina HTML
In `index.html`, riga ~180:
```js
const BASE_URL = 'https://TUOUSER.github.io/monitor';
```

### 4. Crea le cartelle data iniziali
```bash
mkdir -p data/holdings/{GMOM,RPAR,DBMF,AOA,AOR,MAGR,F701,F703}
mkdir -p data/cftc
echo '{"etfs":{},"cftc":[]}' > data/index.json
git add . && git commit -m "init" && git push
```

### 5. Esecuzione manuale iniziale (opzionale)
```bash
pip install requests
python scripts/fetch_holdings.py
python scripts/build_index.py
git add data/ && git commit -m "data: primo fetch" && git push
```

## ETF Monitorati

| Ticker | Nome | Mercato | Frequenza |
|--------|------|---------|-----------|
| GMOM | Cambria Global Momentum | USA | Daily |
| RPAR | RPAR Risk Parity | USA | Daily |
| DBMF | iMGP DBi Managed Futures | USA | Daily |
| AOA  | iShares Core Aggressive Alloc. | USA | Weekly |
| AOR  | iShares Core Moderate Alloc. | USA | Weekly |
| MAGR | iShares Growth Portfolio UCITS | UCITS | Weekly |
| F701 | Amundi Multi-Asset Portfolio | UCITS | Monthly |
| F703 | Amundi Multi-Asset Portfolio AGG | UCITS | Monthly |

## Logica Movimenti Strategici

Una variazione di peso è classificata come **strategica** (non solo drift di mercato) quando supera **±1.5 punti percentuali** rispetto allo snapshot precedente.

## CFTC COT

Dati scaricati ogni venerdì dal report **Traders in Financial Futures (TFF)** — CFTC.gov.
Mercati monitorati: S&P 500, Nasdaq 100, Treasury 10Y, Treasury 2Y, Gold, Crude Oil, EUR/USD, Copper.
Categoria principale: **Leveraged Funds** (= CTA + Hedge Fund sistematici).

## Note Tecniche

- Le URL di fetch delle holdings sono hardcoded in `fetch_holdings.py`. Se un emittente cambia endpoint, aggiornare lì.
- Il fetch di F701/F703 usa justETF API — verificare periodicamente la disponibilità.
- MAGR usa l'endpoint iShares UK — può richiedere aggiustamento User-Agent.
- In caso di CORS issues su GitHub Pages, i dati vengono serviti dallo stesso repo (no fetch cross-origin).
