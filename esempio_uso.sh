#!/bin/bash
# Script di esempio per l'uso del sistema F24 OCR
# Modifica i percorsi secondo le tue necessità

# Colori per output
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo -e "${BLUE}=================================${NC}"
echo -e "${BLUE}ESEMPIO USO F24 OCR${NC}"
echo -e "${BLUE}=================================${NC}"
echo ""

# Percorsi di esempio (MODIFICA QUESTI)
TABULATO="/percorso/al/tabulato_f24.txt"
CARTELLA_PDF="/percorso/alla/cartella_pdf"

echo -e "${YELLOW}NOTA: Modifica questo script con i tuoi percorsi!${NC}"
echo ""
echo "Percorsi da configurare:"
echo "  TABULATO: $TABULATO"
echo "  CARTELLA_PDF: $CARTELLA_PDF"
echo ""

# Verifica se i file esistono
if [ ! -f "$TABULATO" ]; then
    echo -e "${YELLOW}⚠️  File tabulato non trovato: $TABULATO${NC}"
    echo ""
    echo "📝 Esempi di uso con percorsi personalizzati:"
    echo ""

    echo -e "${GREEN}1. Riconciliazione base (output su console)${NC}"
    echo "   python3 riconcilia_f24_ocr.py -t /tuo/percorso/tabulato.txt -p /tuo/percorso/pdf/"
    echo ""

    echo -e "${GREEN}2. Export in JSON${NC}"
    echo "   python3 riconcilia_f24_ocr.py -t /tuo/percorso/tabulato.txt -p /tuo/percorso/pdf/ \\"
    echo "       --output report.json --format json"
    echo ""

    echo -e "${GREEN}3. Export in CSV per Excel${NC}"
    echo "   python3 riconcilia_f24_ocr.py -t /tuo/percorso/tabulato.txt -p /tuo/percorso/pdf/ \\"
    echo "       --output deleghe.csv --format csv"
    echo ""

    echo -e "${GREEN}4. Modalità debug (verbose)${NC}"
    echo "   python3 riconcilia_f24_ocr.py -t /tuo/percorso/tabulato.txt -p /tuo/percorso/pdf/ \\"
    echo "       --verbose"
    echo ""

    echo -e "${GREEN}5. OCR alta qualità (300 DPI)${NC}"
    echo "   python3 riconcilia_f24_ocr.py -t /tuo/percorso/tabulato.txt -p /tuo/percorso/pdf/ \\"
    echo "       --dpi 300"
    echo ""

    exit 0
fi

# Se i file esistono, esegui la riconciliazione
echo -e "${GREEN}✅ File trovati, avvio riconciliazione...${NC}"
echo ""

python3 riconcilia_f24_ocr.py \
    --tabulato "$TABULATO" \
    --pdf-folder "$CARTELLA_PDF" \
    --verbose

echo ""
echo -e "${BLUE}=================================${NC}"
echo -e "${GREEN}✅ Elaborazione completata${NC}"
echo -e "${BLUE}=================================${NC}"
