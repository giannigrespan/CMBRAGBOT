# CMBRAGBOT

Chatbot RAG per CMB

## F24 OCR Reconciliation Tool

Sistema di riconciliazione automatica delle deleghe F24 cartacee tramite OCR (Optical Character Recognition).

### Descrizione

Questo strumento confronta le deleghe F24 cartacee (PDF scansionati o nativi) con il tabulato TXT generato dalla procedura contabile, identificando automaticamente discrepanze tra i dati estratti e quelli attesi.

### Caratteristiche

- ✅ **Supporto multiplo PDF**: Gestisce sia PDF nativi (con testo selezionabile) che scansionati (OCR)
- ✅ **Estrazione intelligente**: Riconosce codici fiscali, importi, CAB, filiali e date di pagamento
- ✅ **Validazione automatica**: Verifica i codici fiscali e corregge errori OCR comuni
- ✅ **Report dettagliati**: Genera report in console, JSON o CSV
- ✅ **Gestione errori robusta**: Logging completo e gestione errori avanzata
- ✅ **Configurabile**: Parametri personalizzabili tramite file di configurazione

### Requisiti di Sistema

#### Dipendenze di Sistema

```bash
# Debian/Ubuntu
sudo apt-get update
sudo apt-get install -y tesseract-ocr tesseract-ocr-ita poppler-utils

# macOS
brew install tesseract tesseract-lang poppler

# Windows
# Scarica e installa:
# - Tesseract: https://github.com/UB-Mannheim/tesseract/wiki
# - Poppler: https://github.com/oschwartz10612/poppler-windows/releases/
```

#### Dipendenze Python

```bash
pip install -r requirements.txt
```

Oppure manualmente:

```bash
pip install pdf2image pytesseract pdfplumber Pillow tqdm
```

### Installazione

```bash
# Clona il repository
git clone https://github.com/giannigrespan/CMBRAGBOT.git
cd CMBRAGBOT

# Installa dipendenze di sistema (vedi sopra)

# Installa dipendenze Python
pip install -r requirements.txt

# Rendi eseguibile lo script (Linux/macOS)
chmod +x riconcilia_f24_ocr.py
```

### Configurazione

Modifica il file `config.py` per personalizzare:

- **Mapping Filiali-CAB**: Aggiungi le tue filiali e i relativi codici CAB
- **Pattern di estrazione**: Personalizza i pattern regex per i tuoi documenti
- **Parametri OCR**: Regola DPI e lingua
- **Tolleranze**: Imposta le soglie di tolleranza per gli importi

```python
# Esempio: Aggiungere una nuova filiale
FILIALE_TO_CAB = {
    'PESEGGIA': '36320',
    'SALZANO': '36270',
    'TUA_FILIALE': 'XXXXX',  # Aggiungi qui
}
```

### Uso

#### Sintassi Base

```bash
python riconcilia_f24_ocr.py --tabulato FILE.txt --pdf-folder CARTELLA_PDF
```

#### Esempi

```bash
# Riconciliazione semplice con output su console
python riconcilia_f24_ocr.py -t dati/tabulato.txt -p dati/deleghe_pdf/

# Esportazione report in JSON
python riconcilia_f24_ocr.py -t dati/tabulato.txt -p dati/deleghe_pdf/ \
    --output report.json --format json

# Esportazione deleghe in CSV
python riconcilia_f24_ocr.py -t dati/tabulato.txt -p dati/deleghe_pdf/ \
    --output deleghe.csv --format csv

# Modalità verbosa (debug)
python riconcilia_f24_ocr.py -t dati/tabulato.txt -p dati/deleghe_pdf/ \
    --verbose

# Modifica risoluzione OCR (migliore qualità)
python riconcilia_f24_ocr.py -t dati/tabulato.txt -p dati/deleghe_pdf/ \
    --dpi 300
```

#### Parametri

| Parametro | Alias | Descrizione | Obbligatorio |
|-----------|-------|-------------|--------------|
| `--tabulato` | `-t` | File TXT del tabulato | ✅ |
| `--pdf-folder` | `-p` | Cartella con i PDF delle deleghe | ✅ |
| `--output` | `-o` | File di output per il report | ❌ |
| `--format` | `-f` | Formato output: console, json, csv | ❌ (default: console) |
| `--verbose` | `-v` | Output dettagliato (debug) | ❌ |
| `--dpi` | | Risoluzione OCR (default: 200) | ❌ |

### Formato Tabulato

Lo script si aspetta un file TXT con questo formato:

```
DATA: 15 11 2024

DIP/CAB  MINISTERIALI         CORPORATE            CARTACEE
         N.TOT  SALDO TOTALE  N.TOT  SALDO TOTALE  N.TOT  SALDO TOTALE
36320    5      1.234,56      10     5.678,90      8      2.345,67
36270    3      987,65        7      3.456,78      5      1.234,56
...

TOT.:    45     12.345,67     89     45.678,90     67     23.456,78
```

### Output

#### Report Console

```
======================================================================
RICONCILIAZIONE F24 CARTACEE
======================================================================
Eseguito: 26/11/2024 15:30
Data tabulato: 15/11/2024
Totale atteso: 67 deleghe, €23.456,78

======================================================================
CONFRONTO PER CAB
======================================================================

CAB      TXT N.   TXT €        PDF N.   PDF €        ESITO
----------------------------------------------------------------------
36320    8        2.345,67     8        2.345,67     ✅ OK
36270    5        1.234,56     4        1.100,00     ❌ DIFF
...

======================================================================
RIEPILOGO
======================================================================
   CAB corrispondenti:    15
   CAB con discrepanze:   2
```

#### Export JSON

```json
{
  "timestamp": "2024-11-26T15:30:00",
  "statistiche": {
    "n_cab_analizzati": 17,
    "n_pdf_elaborati": 67,
    "n_deleghe_estratte": 65,
    "importo_totale_pdf": 23123.45,
    "importo_totale_txt": 23456.78
  },
  "discrepanze": [
    {
      "cab": "36270",
      "txt": {"n_deleghe": 5, "totale": 1234.56},
      "pdf": {"n_deleghe": 4, "totale": 1100.00}
    }
  ]
}
```

#### Export CSV

```csv
cab,codice_fiscale,importo,data_pagamento,filiale,file,pagina
36320,RSSMRA80A01H501Z,234.56,15/11/2024,PESEGGIA,delega_001.pdf,1
36270,BNCGNN70B02L736K,567.89,15/11/2024,SALZANO,delega_002.pdf,1
...
```

### Risoluzione Problemi

#### Tesseract non trovato

```bash
# Verifica installazione
tesseract --version

# Se non installato, installare tramite package manager
sudo apt-get install tesseract-ocr tesseract-ocr-ita
```

#### Errori OCR su PDF scansionati

- Aumenta il DPI: `--dpi 300`
- Verifica qualità scansioni (minimo 200 DPI consigliato)
- Assicurati che Tesseract abbia i language pack italiani installati

#### Codici fiscali non riconosciuti

- Controlla che i documenti siano leggibili
- Personalizza i pattern in `config.py`
- Usa `--verbose` per vedere i dettagli dell'estrazione

#### Importi non trovati

- Verifica che gli importi siano nel formato standard italiano (1.234,56)
- Personalizza i pattern EURO in `config.py`

### Struttura del Progetto

```
CMBRAGBOT/
├── riconcilia_f24_ocr.py   # Script principale
├── config.py               # Configurazione
├── requirements.txt        # Dipendenze Python
├── README.md              # Questo file
├── .gitignore             # File da ignorare in git
└── deepseek_typescript_20251125_a4d05f.ts  # Altri componenti
```

### Miglioramenti Futuri

- [ ] Supporto multi-threading per elaborazione parallela PDF
- [ ] Cache OCR per evitare riprocessamento
- [ ] Web interface per upload e visualizzazione risultati
- [ ] Integrazione con database per storicizzazione
- [ ] Export in formato Excel con formattazione
- [ ] Training personalizzato Tesseract per documenti specifici

### Contributi

Per contribuire al progetto:

1. Fork del repository
2. Crea un branch per la tua feature (`git checkout -b feature/AmazingFeature`)
3. Commit delle modifiche (`git commit -m 'Add some AmazingFeature'`)
4. Push al branch (`git push origin feature/AmazingFeature`)
5. Apri una Pull Request

### Licenza

Progetto interno CMB

### Supporto

Per problemi o domande, aprire una issue su GitHub o contattare il team di sviluppo.

---

**Nota**: Questo strumento è progettato per assistere nell'attività di riconciliazione, ma la verifica finale rimane sempre a carico dell'operatore.
