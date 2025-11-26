# 🚀 Guida Rapida - Come Usare F24 OCR

## Preparazione

### 1. Prepara i tuoi file

Hai bisogno di:
- ✅ **File tabulato** (es: `F24_cartacee.txt`) - Il file dalla procedura
- ✅ **Cartella PDF** (es: `deleghe/`) - Cartella con i PDF delle deleghe F24

### 2. Esempio di struttura file

```
/tua/cartella/
├── F24_cartacee.txt          ← File tabulato
└── deleghe/                  ← Cartella PDF
    ├── delega_001.pdf
    ├── delega_002.pdf
    ├── delega_003.pdf
    └── ...
```

## 🎯 Uso Rapido

### Caso 1: Riconciliazione Base (Output su console)

```bash
python3 riconcilia_f24_ocr.py -t F24_cartacee.txt -p deleghe/
```

**Cosa fa:** Confronta il tabulato con i PDF e mostra il report a schermo.

### Caso 2: Salvare Report in JSON

```bash
python3 riconcilia_f24_ocr.py -t F24_cartacee.txt -p deleghe/ -o report.json -f json
```

**Cosa fa:** Come sopra, ma salva i risultati in formato JSON per analisi successive.

### Caso 3: Esportare Deleghe in CSV (per Excel)

```bash
python3 riconcilia_f24_ocr.py -t F24_cartacee.txt -p deleghe/ -o deleghe.csv -f csv
```

**Cosa fa:** Estrae tutte le deleghe in formato CSV che puoi aprire con Excel.

### Caso 4: Modalità Debug (se qualcosa non va)

```bash
python3 riconcilia_f24_ocr.py -t F24_cartacee.txt -p deleghe/ --verbose
```

**Cosa fa:** Mostra tutti i dettagli dell'elaborazione per capire eventuali problemi.

### Caso 5: PDF con Qualità Bassa (aumenta il DPI)

```bash
python3 riconcilia_f24_ocr.py -t F24_cartacee.txt -p deleghe/ --dpi 300
```

**Cosa fa:** Usa una risoluzione più alta per PDF scansionati di bassa qualità.

## 📊 Cosa Vedrai

### Output Console (Esempio)

```
======================================================================
RICONCILIAZIONE F24 CARTACEE
======================================================================
Eseguito: 26/11/2024 18:30
Data tabulato: 15/11/2024
Totale atteso: 67 deleghe, €23.456,78

======================================================================
CONFRONTO PER CAB
======================================================================

CAB      TXT N.   TXT €        PDF N.   PDF €        ESITO
----------------------------------------------------------------------
36320    8        2.345,67     8        2.345,67     ✅ OK
36270    5        1.234,56     4        1.100,00     ❌ DIFF
36321    12       5.678,90     12       5.678,90     ✅ OK

======================================================================
RIEPILOGO
======================================================================
   CAB corrispondenti:    15
   CAB con discrepanze:   2
```

## 🔧 Parametri Completi

| Parametro | Breve | Descrizione | Esempio |
|-----------|-------|-------------|---------|
| `--tabulato` | `-t` | File TXT tabulato | `-t dati.txt` |
| `--pdf-folder` | `-p` | Cartella PDF | `-p ./deleghe/` |
| `--output` | `-o` | File output | `-o report.json` |
| `--format` | `-f` | Formato: console, json, csv | `-f json` |
| `--verbose` | `-v` | Debug dettagliato | `-v` |
| `--dpi` | | Risoluzione OCR | `--dpi 300` |
| `--help` | `-h` | Mostra aiuto | `--help` |

## 🎬 Workflow Tipico

### Step 1: Primo Test
```bash
# Prova con pochi file per vedere se funziona
python3 riconcilia_f24_ocr.py -t test.txt -p deleghe_test/ --verbose
```

### Step 2: Elaborazione Completa
```bash
# Quando tutto funziona, elabora tutti i file
python3 riconcilia_f24_ocr.py -t F24_cartacee.txt -p tutte_deleghe/
```

### Step 3: Esporta Risultati
```bash
# Salva i risultati per analisi
python3 riconcilia_f24_ocr.py -t F24_cartacee.txt -p tutte_deleghe/ -o risultati.json -f json
```

## ⚡ Comandi Rapidi

### Vedere l'aiuto
```bash
python3 riconcilia_f24_ocr.py --help
```

### Testare l'installazione
```bash
./test_installation.sh
```

### Vedere esempi
```bash
./esempio_uso.sh
```

## ❓ Problemi Comuni

### ❌ "File tabulato non trovato"
**Soluzione:** Verifica il percorso del file. Usa percorsi assoluti se necessario:
```bash
python3 riconcilia_f24_ocr.py -t /percorso/completo/file.txt -p /percorso/completo/pdf/
```

### ❌ "Cartella PDF non trovata"
**Soluzione:** Assicurati che la cartella esista e contenga file PDF:
```bash
ls deleghe/*.pdf  # Verifica che ci siano file PDF
```

### ❌ OCR non riconosce testo
**Soluzione:**
1. Aumenta il DPI: `--dpi 300`
2. Verifica qualità scansioni (minimo 200 DPI)
3. Usa modalità verbose per vedere cosa viene estratto: `--verbose`

### ❌ Importi o CF non trovati
**Soluzione:** Personalizza i pattern in `config.py` per i tuoi documenti specifici.

## 💡 Tips

1. **Prima volta?** Usa `--verbose` per capire cosa succede
2. **Pochi file?** Inizia con una cartella test con 2-3 PDF
3. **PDF di bassa qualità?** Usa `--dpi 300` o `--dpi 400`
4. **Molti file?** Il programma elabora automaticamente tutti i PDF nella cartella
5. **Serve Excel?** Esporta in CSV con `-f csv`

## 📞 Serve Aiuto?

```bash
# Guida completa
cat README.md

# Guida installazione
cat INSTALLATION.md

# Test sistema
./test_installation.sh
```

---

**Pronto?** Prova con un comando semplice:
```bash
python3 riconcilia_f24_ocr.py -t tuo_file.txt -p tua_cartella/ --verbose
```
