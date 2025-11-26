"""
Configurazione per la riconciliazione F24
==========================================
File di configurazione centralizzato per parametri e mapping
"""

# Mapping filiali -> CAB
# Personalizza questo dizionario con le tue filiali
FILIALE_TO_CAB = {
    'PESEGGIA': '36320',
    'SALZANO': '36270',
    'SCORZE': '36321',
    'ZERO BRANCO': '36322',
    'QUINTO': '36330',
    'MOGLIANO': '61741',
    'PREGANZIOL': '61742',
    'MIRANO': '36280',
    'MARTELLAGO': '36290',
    'NOALE': '36300',
}

# Prefissi CAB validi
CAB_VALID_PREFIXES = ['02', '12', '36', '61', '62']

# Range importi validi (min, max) in Euro
IMPORTO_MIN = 10.0
IMPORTO_MAX = 1000000.0

# Parametri OCR
OCR_DPI = 200  # Risoluzione per conversione PDF -> immagini
OCR_LANG = 'ita'  # Lingua per Tesseract

# Soglia tolleranza per confronto importi (in Euro)
TOLLERANZA_IMPORTO = 0.01

# Correzioni OCR per caratteri comuni
# Mapping: carattere_errato -> carattere_corretto
OCR_CORRECTIONS = {
    'O': '0',
    'I': '1',
    'l': '1',
    'S': '5',
    'Z': '2',
    'B': '8',
    'G': '6',
    'Q': '0',
}

# Pattern per estrazione dati
# Questi pattern vengono usati negli estrattori

# Pattern Codice Fiscale
CF_PATTERNS = [
    r'CODICE\s+FISCALE\s+([A-Z0-9]{16})',
    r'COD(?:ICE)?\s*(?:FISC(?:ALE)?)?[:\s]+([A-Z0-9]{16})',
    r'\b([A-Z]{6}\d{2}[A-Z]\d{2}[A-Z]\d{3}[A-Z])\b',
]

# Pattern Importo EURO
EURO_PATTERNS = [
    r'EURO\s*[|:+\s]*?([\d]+[.,][\d]+[.,]?\d*)',
    r'EURO\s*\+\s*([\d.,]+)',
    r'(\d{1,3}\.?\d{0,3},\d{2})\s*\]?\s*$',
    r'TOTALE.*?EURO.*?([\d.,]+)',
    r'SALDO\s*\(A-B\)[^\d]*([\d.,]+)',
]

# Pattern CAB
CAB_PATTERNS = [
    r'08749\s*[|\sO0]*(\d{5})',  # Con ABI
    r'CAB[/\s]*SPORTELLO\s*[:\s]*(\d{5})',
    r'(\d{5})\s+[Tt]ratto',
    r'ABI[:\s]*08749[^\d]*CAB[:\s]*(\d{5})',
]

# Pattern Data Pagamento
DATA_PATTERNS = [
    r'(\d{1,2})\s*(GEN|FEB|MAR|APR|MAG|GIU|LUG|AGO|SET|OTT|NOV|DIC)[A-Z]*\.?\s*(\d{4})',
    r'(\d{1,2})[/-](\d{1,2})[/-](\d{4})',
    r'DATA\s+PAG(?:AMENTO)?[:\s]+(\d{1,2}[/-]\d{1,2}[/-]\d{4})',
]

# Logging
LOG_FORMAT = '%(asctime)s - %(levelname)s - %(message)s'
LOG_DATE_FORMAT = '%Y-%m-%d %H:%M:%S'

# File temporanei
TEMP_DIR = '/tmp/f24_ocr'

# Report
REPORT_DATE_FORMAT = '%d/%m/%Y %H:%M'
MAX_DETTAGLIO_DISCREPANZE = 10  # Numero massimo di deleghe da mostrare nei dettagli
