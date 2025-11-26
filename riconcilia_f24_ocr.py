#!/usr/bin/env python3
"""
RICONCILIAZIONE F24 CARTACEE CON OCR
=====================================
Confronta le deleghe F24 (PDF scansionati) con il tabulato TXT della procedura.

Requisiti:
    pip install -r requirements.txt
    apt-get install tesseract-ocr tesseract-ocr-ita poppler-utils

Uso:
    python riconcilia_f24_ocr.py --tabulato FILE.txt --pdf-folder CARTELLA_PDF
    python riconcilia_f24_ocr.py --tabulato FILE.txt --pdf-folder CARTELLA_PDF --output report.json
    python riconcilia_f24_ocr.py --help
"""

import re
import os
import sys
import json
import csv
import argparse
import logging
from pathlib import Path
from collections import defaultdict
from datetime import datetime
from typing import Dict, List, Optional, Tuple, Any
from dataclasses import dataclass, asdict


# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger(__name__)


# Installa dipendenze se necessario
def check_dependencies() -> None:
    """Verifica e installa le dipendenze necessarie."""
    try:
        from pdf2image import convert_from_path
        import pytesseract
        import pdfplumber
        logger.info("Tutte le dipendenze sono già installate")
    except ImportError as e:
        logger.warning(f"Dipendenze mancanti: {e}")
        logger.info("Installazione dipendenze in corso...")
        try:
            os.system("pip install pdf2image pytesseract pillow pdfplumber --break-system-packages -q")
            logger.info("Dipendenze installate con successo")
        except Exception as install_error:
            logger.error(f"Errore durante l'installazione: {install_error}")
            raise


check_dependencies()

from pdf2image import convert_from_path
import pytesseract
import pdfplumber


# Mapping filiali -> CAB (da personalizzare)
FILIALE_TO_CAB: Dict[str, str] = {
    'PESEGGIA': '36320',
    'SALZANO': '36270',
    'SCORZE': '36321',
    'ZERO BRANCO': '36322',
    'QUINTO': '36330',
    'MOGLIANO': '61741',
    'PREGANZIOL': '61742',
}


@dataclass
class DelegaF24:
    """Rappresenta una delega F24 estratta da PDF."""
    file: str
    pagina: int
    codice_fiscale: Optional[str] = None
    importo: Optional[float] = None
    cab: Optional[str] = None
    filiale: Optional[str] = None
    data_pagamento: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        """Converte in dizionario."""
        return asdict(self)


@dataclass
class DatiCAB:
    """Dati aggregati per CAB dal tabulato."""
    n_deleghe: int
    totale: float


@dataclass
class RisultatoTabulato:
    """Risultato del parsing del tabulato."""
    data: str
    per_cab: Dict[str, DatiCAB]
    totale: Optional[DatiCAB]


def valida_codice_fiscale(cf: str) -> bool:
    """
    Valida il formato di un codice fiscale italiano.

    Args:
        cf: Codice fiscale da validare

    Returns:
        True se il formato è valido, False altrimenti
    """
    if not cf or len(cf) != 16:
        return False

    # Pattern: 6 lettere + 2 numeri + 1 lettera + 2 numeri + 1 lettera + 3 numeri + 1 lettera
    pattern = r'^[A-Z]{6}\d{2}[A-Z]\d{2}[A-Z]\d{3}[A-Z]$'
    return bool(re.match(pattern, cf.upper()))


def pulisci_codice_fiscale(cf: str) -> Optional[str]:
    """
    Pulisce un codice fiscale da errori OCR comuni.

    Args:
        cf: Codice fiscale grezzo

    Returns:
        Codice fiscale pulito o None se non valido
    """
    if not cf:
        return None

    # Rimuovi spazi e converti in maiuscolo
    cf = cf.upper().strip().replace(' ', '')

    # Correzioni comuni OCR
    correzioni = {
        'O': '0', 'I': '1', 'S': '5', 'Z': '2',
        'B': '8', 'G': '6', 'Q': '0'
    }

    # Applica correzioni solo alle posizioni numeriche
    cf_pulito = list(cf)
    posizioni_numeriche = [6, 7, 9, 10, 12, 13, 14]

    for pos in posizioni_numeriche:
        if pos < len(cf_pulito) and cf_pulito[pos] in correzioni:
            cf_pulito[pos] = correzioni[cf_pulito[pos]]

    cf_result = ''.join(cf_pulito)

    return cf_result if valida_codice_fiscale(cf_result) else None


def parse_importo(importo_str: str) -> Optional[float]:
    """
    Parsa una stringa importo in float.

    Args:
        importo_str: Stringa contenente l'importo

    Returns:
        Importo come float o None se non valido
    """
    try:
        # Rimuovi punti come separatori delle migliaia e sostituisci virgola con punto
        importo_clean = importo_str.replace('.', '').replace(',', '.').strip()
        importo = float(importo_clean)

        # Validazione range ragionevole (da 10€ a 1M€)
        if 10 <= importo <= 1000000:
            return importo
        else:
            logger.debug(f"Importo fuori range: {importo}")
            return None
    except (ValueError, AttributeError) as e:
        logger.debug(f"Errore parsing importo '{importo_str}': {e}")
        return None


def parse_tabulato_txt(filepath: str) -> RisultatoTabulato:
    """
    Parsa il file TXT del tabulato e restituisce i dati per CAB.

    Args:
        filepath: Percorso del file tabulato

    Returns:
        RisultatoTabulato con i dati estratti

    Raises:
        FileNotFoundError: Se il file non esiste
        ValueError: Se il formato non è valido
    """
    logger.info(f"Parsing tabulato: {filepath}")

    if not os.path.exists(filepath):
        raise FileNotFoundError(f"File tabulato non trovato: {filepath}")

    try:
        with open(filepath, 'r', encoding='utf-8', errors='ignore') as f:
            content = f.read()
    except Exception as e:
        raise ValueError(f"Errore lettura file: {e}")

    # Trova la data del tabulato
    data_match = re.search(r'DATA:\s*(\d{2}\s+\d{2}\s+\d{4})', content)
    data_tabulato = data_match.group(1).replace(' ', '/') if data_match else "N/D"

    # Pattern per le righe con i dati per filiale (DIP/CAB)
    pattern = re.compile(
        r'^\s*(\d{5})\s+'  # CAB (5 cifre)
        r'(\d+)\s+([\d.,]+)\s+'  # ministeriali: n.tot, saldo
        r'(\d+)\s+([\d.,]+)\s+'  # corporate: n.tot, saldo
        r'(\d+)\s+([\d.,]+)',    # cartacee: n.tot, saldo
        re.MULTILINE
    )

    risultati: Dict[str, DatiCAB] = {}

    for match in pattern.finditer(content):
        cab = match.group(1)
        n_cartacee = int(match.group(6))
        saldo_str = match.group(7)

        importo = parse_importo(saldo_str)
        if importo is None:
            logger.warning(f"Impossibile parsare importo per CAB {cab}: {saldo_str}")
            importo = 0.0

        risultati[cab] = DatiCAB(n_deleghe=n_cartacee, totale=importo)
        logger.debug(f"CAB {cab}: {n_cartacee} deleghe, €{importo:,.2f}")

    # Estrai totali generali
    tot_match = re.search(
        r'TOT\.:\s+\d+\s+[\d.,]+\s+\d+\s+[\d.,]+\s+(\d+)\s+([\d.,]+)',
        content
    )

    totale_generale = None
    if tot_match:
        n_tot = int(tot_match.group(1))
        saldo_tot = parse_importo(tot_match.group(2))
        if saldo_tot:
            totale_generale = DatiCAB(n_deleghe=n_tot, totale=saldo_tot)

    logger.info(f"Estratti dati per {len(risultati)} CAB")

    return RisultatoTabulato(
        data=data_tabulato,
        per_cab=risultati,
        totale=totale_generale
    )


def is_scanned_pdf(pdf_path: str) -> bool:
    """
    Verifica se un PDF è scansionato (immagine) o nativo (testo).

    Args:
        pdf_path: Percorso del PDF

    Returns:
        True se il PDF è scansionato, False se è nativo
    """
    try:
        with pdfplumber.open(pdf_path) as pdf:
            # Controlla le prime 2 pagine
            for page in pdf.pages[:2]:
                text = page.extract_text()
                if text and len(text.strip()) > 50:
                    logger.debug(f"{pdf_path}: PDF nativo (testo estratto)")
                    return False
        logger.debug(f"{pdf_path}: PDF scansionato")
        return True
    except Exception as e:
        logger.warning(f"Errore verifica tipo PDF {pdf_path}: {e}")
        return True  # Assume scansionato in caso di errore


def extract_from_native_pdf(pdf_path: str) -> List[DelegaF24]:
    """
    Estrae dati da PDF con testo nativo (selezionabile).

    Args:
        pdf_path: Percorso del PDF

    Returns:
        Lista di deleghe estratte
    """
    deleghe = []

    try:
        with pdfplumber.open(pdf_path) as pdf:
            for page_num, page in enumerate(pdf.pages, 1):
                text = page.extract_text() or ""
                delega = extract_data_from_text(text, page_num, pdf_path)
                if delega.codice_fiscale or delega.importo:
                    deleghe.append(delega)
    except Exception as e:
        logger.error(f"Errore estrazione da PDF nativo {pdf_path}: {e}")

    return deleghe


def extract_from_scanned_pdf(pdf_path: str, dpi: int = 200) -> List[DelegaF24]:
    """
    Estrae dati da PDF scansionato usando OCR.

    Args:
        pdf_path: Percorso del PDF
        dpi: Risoluzione per la conversione (default: 200)

    Returns:
        Lista di deleghe estratte
    """
    deleghe = []

    try:
        logger.debug(f"Conversione PDF in immagini: {pdf_path}")
        images = convert_from_path(pdf_path, dpi=dpi)
    except Exception as e:
        logger.error(f"Errore conversione PDF {pdf_path}: {e}")
        return deleghe

    for page_num, img in enumerate(images, 1):
        try:
            logger.debug(f"OCR pagina {page_num}/{len(images)}")
            text = pytesseract.image_to_string(img, lang='ita')
            delega = extract_data_from_text(text, page_num, pdf_path)
            if delega.codice_fiscale or delega.importo:
                deleghe.append(delega)
        except Exception as e:
            logger.error(f"Errore OCR pagina {page_num} di {pdf_path}: {e}")

    return deleghe


def extract_data_from_text(text: str, page_num: int, pdf_path: str) -> DelegaF24:
    """
    Estrae i dati F24 dal testo (sia OCR che nativo).

    Args:
        text: Testo estratto
        page_num: Numero pagina
        pdf_path: Percorso del PDF

    Returns:
        DelegaF24 con i dati estratti
    """

    # Codice Fiscale
    cf = None
    cf_patterns = [
        r'CODICE\s+FISCALE\s+([A-Z0-9]{16})',
        r'COD(?:ICE)?\s*(?:FISC(?:ALE)?)?[:\s]+([A-Z0-9]{16})',
        r'\b([A-Z]{6}\d{2}[A-Z]\d{2}[A-Z]\d{3}[A-Z])\b',
    ]

    for pattern in cf_patterns:
        match = re.search(pattern, text, re.IGNORECASE)
        if match:
            cf_raw = match.group(1).upper()
            cf = pulisci_codice_fiscale(cf_raw)
            if cf:
                logger.debug(f"CF trovato: {cf}")
                break

    # Importo EURO
    importo = None
    euro_patterns = [
        r'EURO\s*[|:+\s]*?([\d]+[.,][\d]+[.,]?\d*)',
        r'EURO\s*\+\s*([\d.,]+)',
        r'(\d{1,3}\.?\d{0,3},\d{2})\s*\]?\s*$',
        r'TOTALE.*?EURO.*?([\d.,]+)',
    ]

    for pattern in euro_patterns:
        matches = re.findall(pattern, text, re.MULTILINE | re.IGNORECASE)
        if matches:
            for m in reversed(matches):
                val = parse_importo(m)
                if val:
                    importo = val
                    logger.debug(f"Importo trovato: €{importo:,.2f}")
                    break
            if importo:
                break

    # Fallback: cerca SALDO (A-B)
    if not importo:
        saldo_match = re.search(r'SALDO\s*\(A-B\)[^\d]*([\d.,]+)', text)
        if saldo_match:
            importo = parse_importo(saldo_match.group(1))
            if importo:
                logger.debug(f"Importo da SALDO: €{importo:,.2f}")

    # CAB
    cab = None
    cab_patterns = [
        r'08749\s*[|\sO0]*(\d{5})',
        r'CAB[/\s]*SPORTELLO\s*[:\s]*(\d{5})',
        r'(\d{5})\s+[Tt]ratto',
        r'ABI[:\s]*08749[^\d]*CAB[:\s]*(\d{5})',
    ]

    for pattern in cab_patterns:
        match = re.search(pattern, text)
        if match:
            potential_cab = match.group(1)
            # Valida che il CAB inizi con prefissi comuni
            if potential_cab[:2] in ['02', '12', '36', '61', '62']:
                cab = potential_cab
                logger.debug(f"CAB trovato: {cab}")
                break

    # Filiale (dal timbro o intestazione)
    filiale = None
    for f_name, f_cab in FILIALE_TO_CAB.items():
        if f_name.lower() in text.lower():
            filiale = f_name
            if not cab:
                cab = f_cab
                logger.debug(f"CAB derivato da filiale {filiale}: {cab}")
            break

    # Data pagamento
    data_pag = None
    data_patterns = [
        r'(\d{1,2})\s*(GEN|FEB|MAR|APR|MAG|GIU|LUG|AGO|SET|OTT|NOV|DIC)[A-Z]*\.?\s*(\d{4})',
        r'(\d{1,2})[/-](\d{1,2})[/-](\d{4})',
        r'DATA\s+PAG(?:AMENTO)?[:\s]+(\d{1,2}[/-]\d{1,2}[/-]\d{4})',
    ]

    for pattern in data_patterns:
        match = re.search(pattern, text, re.IGNORECASE)
        if match:
            data_pag = match.group(0)
            logger.debug(f"Data pagamento trovata: {data_pag}")
            break

    return DelegaF24(
        file=os.path.basename(pdf_path),
        pagina=page_num,
        codice_fiscale=cf,
        importo=importo,
        cab=cab,
        filiale=filiale,
        data_pagamento=data_pag
    )


def estrai_deleghe_da_pdf(pdf_path: str) -> List[DelegaF24]:
    """
    Estrae le deleghe da un PDF, scegliendo automaticamente il metodo.

    Args:
        pdf_path: Percorso del PDF

    Returns:
        Lista di deleghe estratte
    """
    logger.info(f"Elaborazione PDF: {os.path.basename(pdf_path)}")

    if is_scanned_pdf(pdf_path):
        logger.debug("Usando OCR per PDF scansionato")
        return extract_from_scanned_pdf(pdf_path)
    else:
        logger.debug("Estrazione testo da PDF nativo")
        return extract_from_native_pdf(pdf_path)


def genera_report_console(
    tabulato: RisultatoTabulato,
    tutte_deleghe: List[DelegaF24],
    discrepanze: List[Dict],
    ok_count: int,
    per_cab_pdf: Dict
) -> None:
    """Genera il report su console."""

    print("\n" + "=" * 70)
    print("RICONCILIAZIONE F24 CARTACEE")
    print("=" * 70)
    print(f"Eseguito: {datetime.now().strftime('%d/%m/%Y %H:%M')}")
    print(f"Data tabulato: {tabulato.data}")

    if tabulato.totale:
        print(f"Totale atteso: {tabulato.totale.n_deleghe} deleghe, "
              f"€{tabulato.totale.totale:,.2f}")

    print(f"Totale estratto: {len(tutte_deleghe)} deleghe")

    # Confronto per CAB
    print("\n" + "=" * 70)
    print("CONFRONTO PER CAB")
    print("=" * 70)

    print(f"\n{'CAB':<8} {'TXT N.':<8} {'TXT €':>12} {'PDF N.':<8} {'PDF €':>12} {'ESITO':<8}")
    print("-" * 70)

    tutti_cab = set(tabulato.per_cab.keys()) | set(per_cab_pdf.keys())

    for cab in sorted(tutti_cab):
        txt_data = tabulato.per_cab.get(cab, DatiCAB(n_deleghe=0, totale=0.0))
        pdf_data = per_cab_pdf.get(cab, {'deleghe': [], 'totale': 0.0})

        n_txt = txt_data.n_deleghe
        tot_txt = txt_data.totale
        n_pdf = len(pdf_data['deleghe'])
        tot_pdf = pdf_data['totale']

        if n_txt == 0 and n_pdf == 0:
            continue

        n_ok = n_txt == n_pdf
        tot_ok = abs(tot_txt - tot_pdf) < 0.01

        esito = "✅ OK" if (n_ok and tot_ok) else "❌ DIFF"

        print(f"{cab:<8} {n_txt:<8} {tot_txt:>12,.2f} {n_pdf:<8} {tot_pdf:>12,.2f} {esito:<8}")

    # Totali
    tot_n_pdf = len(tutte_deleghe)
    tot_importo_pdf = sum(d.importo or 0 for d in tutte_deleghe)

    print("-" * 70)
    if tabulato.totale:
        print(f"{'TOTALE':<8} {tabulato.totale.n_deleghe:<8} "
              f"{tabulato.totale.totale:>12,.2f} "
              f"{tot_n_pdf:<8} {tot_importo_pdf:>12,.2f}")

    # Riepilogo
    print("\n" + "=" * 70)
    print("RIEPILOGO")
    print("=" * 70)
    print(f"   CAB corrispondenti:    {ok_count}")
    print(f"   CAB con discrepanze:   {len(discrepanze)}")

    # Dettaglio discrepanze
    if discrepanze:
        print("\n" + "=" * 70)
        print("DETTAGLIO DISCREPANZE")
        print("=" * 70)

        for disc in discrepanze:
            diff_n = disc['pdf']['n_deleghe'] - disc['txt']['n_deleghe']
            diff_tot = disc['pdf']['totale'] - disc['txt']['totale']

            print(f"\n🔍 CAB {disc['cab']}:")
            print(f"   Tabulato: {disc['txt']['n_deleghe']} deleghe, €{disc['txt']['totale']:,.2f}")
            print(f"   PDF:      {disc['pdf']['n_deleghe']} deleghe, €{disc['pdf']['totale']:,.2f}")
            print(f"   Diff:     {diff_n:+d} deleghe, €{diff_tot:+,.2f}")

            if disc['pdf']['dettaglio']:
                print("   Deleghe PDF:")
                for d in disc['pdf']['dettaglio'][:10]:  # Limita a 10
                    print(f"      • {d.codice_fiscale or 'CF N/D':<18} "
                          f"€{d.importo or 0:>10,.2f}  {d.data_pagamento or ''}")

                if len(disc['pdf']['dettaglio']) > 10:
                    print(f"      ... e altre {len(disc['pdf']['dettaglio']) - 10} deleghe")


def esporta_csv(deleghe: List[DelegaF24], output_file: str) -> None:
    """
    Esporta le deleghe in formato CSV.

    Args:
        deleghe: Lista di deleghe da esportare
        output_file: Percorso file di output
    """
    try:
        with open(output_file, 'w', newline='', encoding='utf-8') as f:
            writer = csv.DictWriter(f, fieldnames=[
                'cab', 'codice_fiscale', 'importo', 'data_pagamento',
                'filiale', 'file', 'pagina'
            ])
            writer.writeheader()

            for d in deleghe:
                writer.writerow(d.to_dict())

        logger.info(f"Export CSV completato: {output_file}")
    except Exception as e:
        logger.error(f"Errore export CSV: {e}")


def esporta_json(risultati: Dict[str, Any], output_file: str) -> None:
    """
    Esporta i risultati completi in formato JSON.

    Args:
        risultati: Dizionario con tutti i risultati
        output_file: Percorso file di output
    """
    try:
        # Converti oggetti non serializzabili
        def convert_to_serializable(obj):
            if isinstance(obj, (DelegaF24, DatiCAB)):
                return obj.to_dict() if hasattr(obj, 'to_dict') else asdict(obj)
            elif isinstance(obj, RisultatoTabulato):
                return {
                    'data': obj.data,
                    'per_cab': {k: asdict(v) for k, v in obj.per_cab.items()},
                    'totale': asdict(obj.totale) if obj.totale else None
                }
            return obj

        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(risultati, f, indent=2, ensure_ascii=False, default=convert_to_serializable)

        logger.info(f"Export JSON completato: {output_file}")
    except Exception as e:
        logger.error(f"Errore export JSON: {e}")


def riconcilia(
    tabulato_path: str,
    pdf_folder: str,
    output_file: Optional[str] = None,
    output_format: str = 'console'
) -> Dict[str, Any]:
    """
    Esegue la riconciliazione completa.

    Args:
        tabulato_path: Percorso file tabulato TXT
        pdf_folder: Cartella contenente i PDF
        output_file: File di output (opzionale)
        output_format: Formato output (console, json, csv)

    Returns:
        Dizionario con i risultati della riconciliazione
    """

    logger.info("Inizio riconciliazione F24 cartacee")

    # 1. Parsa tabulato
    try:
        tabulato = parse_tabulato_txt(tabulato_path)
    except Exception as e:
        logger.error(f"Errore parsing tabulato: {e}")
        raise

    # 2. Scansiona PDF
    pdf_folder_path = Path(pdf_folder)
    if not pdf_folder_path.exists():
        raise FileNotFoundError(f"Cartella PDF non trovata: {pdf_folder}")

    pdf_files = list(pdf_folder_path.glob("*.pdf")) + list(pdf_folder_path.glob("*.PDF"))
    logger.info(f"Trovati {len(pdf_files)} file PDF")

    tutte_deleghe: List[DelegaF24] = []

    for i, pdf_file in enumerate(pdf_files, 1):
        logger.info(f"[{i}/{len(pdf_files)}] Elaborazione {pdf_file.name}")
        try:
            deleghe = estrai_deleghe_da_pdf(str(pdf_file))
            logger.info(f"   Estratte {len(deleghe)} deleghe")
            tutte_deleghe.extend(deleghe)
        except Exception as e:
            logger.error(f"   Errore elaborazione {pdf_file.name}: {e}")

    logger.info(f"Totale deleghe estratte: {len(tutte_deleghe)}")

    # 3. Raggruppa per CAB
    per_cab_pdf = defaultdict(lambda: {'deleghe': [], 'totale': 0.0})

    for d in tutte_deleghe:
        cab = d.cab or 'SCONOSCIUTO'
        per_cab_pdf[cab]['deleghe'].append(d)
        if d.importo:
            per_cab_pdf[cab]['totale'] += d.importo

    # 4. Confronto
    discrepanze = []
    ok_count = 0

    tutti_cab = set(tabulato.per_cab.keys()) | set(per_cab_pdf.keys())

    for cab in tutti_cab:
        txt_data = tabulato.per_cab.get(cab, DatiCAB(n_deleghe=0, totale=0.0))
        pdf_data = per_cab_pdf.get(cab, {'deleghe': [], 'totale': 0.0})

        n_txt = txt_data.n_deleghe
        tot_txt = txt_data.totale
        n_pdf = len(pdf_data['deleghe'])
        tot_pdf = pdf_data['totale']

        if n_txt == 0 and n_pdf == 0:
            continue

        n_ok = n_txt == n_pdf
        tot_ok = abs(tot_txt - tot_pdf) < 0.01

        if n_ok and tot_ok:
            ok_count += 1
        else:
            discrepanze.append({
                'cab': cab,
                'txt': {'n_deleghe': n_txt, 'totale': tot_txt},
                'pdf': {
                    'n_deleghe': n_pdf,
                    'totale': tot_pdf,
                    'dettaglio': pdf_data['deleghe']
                }
            })

    # 5. Output
    risultati = {
        'timestamp': datetime.now().isoformat(),
        'tabulato': tabulato,
        'deleghe_pdf': tutte_deleghe,
        'discrepanze': discrepanze,
        'ok_count': ok_count,
        'statistiche': {
            'n_cab_analizzati': len(tutti_cab),
            'n_pdf_elaborati': len(pdf_files),
            'n_deleghe_estratte': len(tutte_deleghe),
            'importo_totale_pdf': sum(d.importo or 0 for d in tutte_deleghe),
            'importo_totale_txt': tabulato.totale.totale if tabulato.totale else 0
        }
    }

    # Genera output
    genera_report_console(tabulato, tutte_deleghe, discrepanze, ok_count, per_cab_pdf)

    if output_file:
        if output_format == 'json':
            esporta_json(risultati, output_file)
        elif output_format == 'csv':
            esporta_csv(tutte_deleghe, output_file)

    logger.info("Riconciliazione completata")

    return risultati


def main():
    """Entry point principale."""
    parser = argparse.ArgumentParser(
        description='Riconciliazione F24 Cartacee - Confronta PDF deleghe con tabulato TXT',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Esempi:
  %(prog)s --tabulato dati.txt --pdf-folder ./deleghe/
  %(prog)s -t dati.txt -p ./deleghe/ --output report.json --format json
  %(prog)s -t dati.txt -p ./deleghe/ --output deleghe.csv --format csv --verbose
        """
    )

    parser.add_argument(
        '--tabulato', '-t',
        required=True,
        help='File TXT del tabulato dalla procedura'
    )
    parser.add_argument(
        '--pdf-folder', '-p',
        required=True,
        help='Cartella contenente i PDF delle deleghe'
    )
    parser.add_argument(
        '--output', '-o',
        help='File di output per il report (opzionale)'
    )
    parser.add_argument(
        '--format', '-f',
        choices=['console', 'json', 'csv'],
        default='console',
        help='Formato output (default: console)'
    )
    parser.add_argument(
        '--verbose', '-v',
        action='store_true',
        help='Abilita output verboso'
    )
    parser.add_argument(
        '--dpi',
        type=int,
        default=200,
        help='Risoluzione DPI per OCR (default: 200)'
    )

    args = parser.parse_args()

    # Configura logging
    if args.verbose:
        logger.setLevel(logging.DEBUG)

    # Validazione input
    if not os.path.exists(args.tabulato):
        logger.error(f"File tabulato non trovato: {args.tabulato}")
        sys.exit(1)

    if not os.path.isdir(args.pdf_folder):
        logger.error(f"Cartella PDF non trovata: {args.pdf_folder}")
        sys.exit(1)

    # Esegui riconciliazione
    try:
        riconcilia(
            args.tabulato,
            args.pdf_folder,
            args.output,
            args.format
        )
    except Exception as e:
        logger.error(f"Errore durante la riconciliazione: {e}", exc_info=args.verbose)
        sys.exit(1)


if __name__ == "__main__":
    # Se eseguito senza argomenti, mostra help
    if len(sys.argv) == 1:
        print("Uso: python riconcilia_f24_ocr.py --tabulato FILE.txt --pdf-folder CARTELLA")
        print("Per maggiori informazioni: python riconcilia_f24_ocr.py --help")
        sys.exit(0)

    main()
