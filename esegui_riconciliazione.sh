#!/bin/bash
# Script per eseguire la riconciliazione F24
# PERSONALIZZA I PERCORSI QUI SOTTO

# =====================================
# MODIFICA QUESTI PERCORSI
# =====================================

# Percorso del file tabulato TXT
TABULATO="/percorso/al/tuo/F24_cartacee.txt"

# Percorso della cartella contenente i PDF
CARTELLA_PDF="/percorso/alla/tua/cartella_pdf"

# =====================================
# NON MODIFICARE DA QUI IN GIÙ
# =====================================

echo "🚀 Avvio Riconciliazione F24 OCR"
echo ""

# Verifica che i file esistano
if [ ! -f "$TABULATO" ]; then
    echo "❌ ERRORE: File tabulato non trovato"
    echo "   Percorso: $TABULATO"
    echo ""
    echo "📝 Modifica lo script e imposta il percorso corretto nella variabile TABULATO"
    echo ""
    echo "Esempio di come usare lo script:"
    echo "   1. Apri il file: nano esegui_riconciliazione.sh"
    echo "   2. Modifica TABULATO=\"/tuo/percorso/file.txt\""
    echo "   3. Modifica CARTELLA_PDF=\"/tuo/percorso/pdf/\""
    echo "   4. Salva e riesegui: ./esegui_riconciliazione.sh"
    exit 1
fi

if [ ! -d "$CARTELLA_PDF" ]; then
    echo "❌ ERRORE: Cartella PDF non trovata"
    echo "   Percorso: $CARTELLA_PDF"
    echo ""
    echo "📝 Modifica lo script e imposta il percorso corretto nella variabile CARTELLA_PDF"
    exit 1
fi

# Conta i PDF
N_PDF=$(ls "$CARTELLA_PDF"/*.pdf "$CARTELLA_PDF"/*.PDF 2>/dev/null | wc -l)
if [ "$N_PDF" -eq 0 ]; then
    echo "⚠️  ATTENZIONE: Nessun file PDF trovato nella cartella"
    echo "   Cartella: $CARTELLA_PDF"
    exit 1
fi

echo "✅ File tabulato: $TABULATO"
echo "✅ Cartella PDF: $CARTELLA_PDF"
echo "✅ PDF trovati: $N_PDF file"
echo ""
echo "⏳ Elaborazione in corso..."
echo ""

# Esegui la riconciliazione
python3 riconcilia_f24_ocr.py \
    --tabulato "$TABULATO" \
    --pdf-folder "$CARTELLA_PDF" \
    --verbose

echo ""
echo "✅ Elaborazione completata!"
echo ""
echo "💡 Per salvare i risultati:"
echo "   - JSON: python3 riconcilia_f24_ocr.py -t \"$TABULATO\" -p \"$CARTELLA_PDF\" -o report.json -f json"
echo "   - CSV:  python3 riconcilia_f24_ocr.py -t \"$TABULATO\" -p \"$CARTELLA_PDF\" -o deleghe.csv -f csv"
