# Guida di Installazione Locale - F24 OCR

Questa guida ti accompagna nell'installazione del sistema di riconciliazione F24 OCR sul tuo sistema locale.

## ✅ Installazione Completata

L'installazione è già stata completata su questo sistema con successo!

## 📋 Componenti Installati

### Dipendenze di Sistema

| Componente | Versione | Stato |
|------------|----------|-------|
| Python | 3.11.14 | ✅ Installato |
| Tesseract OCR | 5.3.4 | ✅ Installato |
| Tesseract ITA | 4.1.0 | ✅ Installato |
| Poppler Utils | 24.02.0 | ✅ Installato |

### Dipendenze Python

| Pacchetto | Versione | Stato |
|-----------|----------|-------|
| pdf2image | 1.17.0 | ✅ Installato |
| pdfplumber | 0.11.8 | ✅ Installato |
| pytesseract | 0.3.13 | ✅ Installato |
| Pillow | 12.0.0 | ✅ Installato |

## 🚀 Come Usare

### Test Rapido

```bash
# Verifica che tutto funzioni
./test_installation.sh
```

### Uso Base

```bash
# Sintassi base
python3 riconcilia_f24_ocr.py -t TABULATO.txt -p CARTELLA_PDF/

# Visualizza aiuto completo
python3 riconcilia_f24_ocr.py --help
```

### Esempi Pratici

```bash
# 1. Riconciliazione semplice (output su console)
python3 riconcilia_f24_ocr.py \
  --tabulato /percorso/tabulato_f24.txt \
  --pdf-folder /percorso/deleghe_pdf/

# 2. Export in formato JSON
python3 riconcilia_f24_ocr.py \
  -t /percorso/tabulato_f24.txt \
  -p /percorso/deleghe_pdf/ \
  --output report.json \
  --format json

# 3. Export in formato CSV per Excel
python3 riconcilia_f24_ocr.py \
  -t /percorso/tabulato_f24.txt \
  -p /percorso/deleghe_pdf/ \
  --output deleghe.csv \
  --format csv

# 4. Modalità verbose (debug)
python3 riconcilia_f24_ocr.py \
  -t /percorso/tabulato_f24.txt \
  -p /percorso/deleghe_pdf/ \
  --verbose

# 5. OCR alta qualità (DPI aumentato)
python3 riconcilia_f24_ocr.py \
  -t /percorso/tabulato_f24.txt \
  -p /percorso/deleghe_pdf/ \
  --dpi 300
```

## 🔧 Configurazione

Il file `config.py` contiene i parametri configurabili:

```python
# Esempio: Aggiungere una nuova filiale
FILIALE_TO_CAB = {
    'PESEGGIA': '36320',
    'SALZANO': '36270',
    # Aggiungi le tue filiali qui
    'NUOVA_FILIALE': 'XXXXX',
}
```

## 🧪 Test dell'Installazione

Per verificare che tutto sia installato correttamente:

```bash
# Esegui lo script di test
./test_installation.sh

# Oppure verifica manualmente
python3 -c "
import pdf2image
import pytesseract
import pdfplumber
from PIL import Image
print('✅ Tutti i moduli sono disponibili')
"
```

## 📊 Struttura File di Input

### File Tabulato (TXT)

Il file tabulato deve avere questo formato:

```
DATA: 15 11 2024

DIP/CAB  MINISTERIALI         CORPORATE            CARTACEE
         N.TOT  SALDO TOTALE  N.TOT  SALDO TOTALE  N.TOT  SALDO TOTALE
36320    5      1.234,56      10     5.678,90      8      2.345,67
36270    3      987,65        7      3.456,78      5      1.234,56

TOT.:    45     12.345,67     89     45.678,90     67     23.456,78
```

### Cartella PDF

La cartella deve contenere i file PDF delle deleghe F24 (possono essere scansionati o nativi).

## ❓ Risoluzione Problemi

### Errore: "tesseract: command not found"

```bash
sudo apt-get install tesseract-ocr tesseract-ocr-ita
```

### Errore: "pdftoppm: command not found"

```bash
sudo apt-get install poppler-utils
```

### Errore: ModuleNotFoundError

```bash
pip install -r requirements.txt --break-system-packages
```

### OCR non riconosce testo italiano

```bash
# Verifica che il language pack italiano sia installato
tesseract --list-langs | grep ita

# Se manca, installalo
sudo apt-get install tesseract-ocr-ita
```

## 🔄 Reinstallazione

Se hai problemi, puoi reinstallare tutto:

```bash
# 1. Reinstalla dipendenze di sistema
sudo apt-get update
sudo apt-get install -y tesseract-ocr tesseract-ocr-ita poppler-utils

# 2. Reinstalla dipendenze Python
pip install -r requirements.txt --break-system-packages --force-reinstall

# 3. Testa l'installazione
./test_installation.sh
```

## 📝 Note Importanti

- ✅ L'installazione è stata completata con successo su questo sistema
- ✅ Tesseract supporta sia italiano che inglese
- ✅ Lo script gestisce automaticamente PDF nativi e scansionati
- ✅ Tutti i componenti sono testati e funzionanti

## 🆘 Supporto

Per problemi o domande:

1. Controlla la documentazione nel file README.md
2. Esegui `./test_installation.sh` per diagnostica
3. Usa `--verbose` per vedere dettagli di debug
4. Apri una issue su GitHub

---

**Ultima verifica:** 26/11/2024 18:09 UTC
**Stato:** ✅ Funzionante
