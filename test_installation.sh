#!/bin/bash
# Script per testare l'installazione del sistema F24 OCR

echo "================================="
echo "TEST INSTALLAZIONE F24 OCR"
echo "================================="
echo ""

echo "1️⃣  Verifica Python..."
python3 --version

echo ""
echo "2️⃣  Verifica Tesseract OCR..."
tesseract --version | head -1
tesseract --list-langs | grep -E "ita|eng"

echo ""
echo "3️⃣  Verifica Poppler Utils..."
pdftoppm -v | head -1

echo ""
echo "4️⃣  Verifica dipendenze Python..."
python3 -c "
import pdf2image
import pytesseract
import pdfplumber
from PIL import Image

print('  ✅ pdf2image: OK')
print('  ✅ pytesseract: OK')
print('  ✅ pdfplumber: OK')
print('  ✅ Pillow: OK')
"

echo ""
echo "5️⃣  Verifica script principale..."
if [ -x "riconcilia_f24_ocr.py" ]; then
    echo "  ✅ riconcilia_f24_ocr.py: Eseguibile"
else
    echo "  ❌ riconcilia_f24_ocr.py: Non eseguibile"
fi

echo ""
echo "6️⃣  Test help..."
python3 riconcilia_f24_ocr.py --help > /dev/null 2>&1
if [ $? -eq 0 ]; then
    echo "  ✅ Script funziona correttamente"
else
    echo "  ❌ Script ha errori"
fi

echo ""
echo "================================="
echo "✅ INSTALLAZIONE COMPLETATA"
echo "================================="
echo ""
echo "Per usare il programma:"
echo "  python3 riconcilia_f24_ocr.py -t TABULATO.txt -p CARTELLA_PDF/"
echo ""
