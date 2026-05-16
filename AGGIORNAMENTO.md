# RAPTOR ETF MONITOR — Procedura aggiornamento holdings

## Ogni settimana (5 minuti)

### 1. Scarica i CSV da investing.com

| ETF  | Link |
|------|------|
| GMOM | https://www.investing.com/etfs/cambria-global-momentum-etf-holdings |
| RPAR | https://www.investing.com/etfs/rpar-risk-parity-etf-holdings |
| DBMF | https://www.investing.com/etfs/imgp-dbi-managed-futures-strategy-etf-holdings |
| AOA  | https://www.investing.com/etfs/ishares-aggressive-allocation-holdings |
| AOR  | https://www.investing.com/etfs/ishares-growth-allocation-holdings |
| MAGR | https://it.investing.com/etfs/magr-holdings?cid=1208413 |
| F701 | https://it.investing.com/etfs/comstage-vermogensstrategie-holdings |
| F703 | https://it.investing.com/etfs/f703-holdings |

Su ogni pagina: tasto **Download** (icona freccia in basso).

### 2. Rinomina i file

Rinomina ogni file scaricato esattamente così (maiuscolo, .csv):

```
GMOM.csv
RPAR.csv
DBMF.csv
AOA.csv
AOR.csv
MAGR.csv
F701.csv
F703.csv
```

### 3. Carica nel repo

Metti tutti i file in `data/manual/` nel repo GitHub.

Puoi farlo via browser:
- Vai su `https://github.com/Giorgiogoldoni/MONITOR/tree/main/data/manual`
- Trascina i file o usa "Add file → Upload files"
- Commit direttamente su `main`

### 4. Esegui il workflow

- Vai su `https://github.com/Giorgiogoldoni/MONITOR/actions/workflows/fetch_holdings.yml`
- Clicca **Run workflow → Run workflow**

Il workflow:
- Legge i CSV da `data/manual/`
- Salva gli snapshot JSON in `data/holdings/TICKER/YYYY-MM-DD.json`
- Scarica automaticamente il CFTC COT con la data corretta del report
- Aggiorna `data/index.json`

---

## Note

- **CFTC** è automatico — non devi fare nulla. Il report esce ogni venerdì
  (dati del martedì precedente) e viene salvato con la data interna del report.
- Se un CSV non è presente in `data/manual/`, quell'ETF viene saltato senza errori.
- Il file CSV viene riconosciuto dalla sua data di modifica — se carichi lo stesso
  file due volte non crea duplicati.
