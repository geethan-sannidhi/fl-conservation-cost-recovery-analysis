#!/usr/bin/env bash
# Download the source filings and convert to text. Usage: scripts/fetch_sources.sh <outdir>
set -euo pipefail
OUT="${1:?outdir}"; mkdir -p "$OUT"; cd "$OUT"
B="https://floridapsc.com/pscfiles/website-files/PDF/Utilities/Electricgas/ARDemandSide/2025"
get() { curl -sSfL -m 180 "$1" -o "$2.pdf"; pdftotext -layout "$2.pdf" "$2.txt"; }
get "$B/Florida%20Power%20and%20Light%20Company.pdf" dsm_2025_FloridaPowerandLightCompany
get "$B/Duke%20Energy%20Florida.pdf"                 dsm_2025_DukeEnergyFlorida
get "$B/Tampa%20Electric%20Company.pdf"              dsm_2025_TampaElectricCompany
get "$B/Florida%20Public%20Utilities%20Company.pdf"  dsm_2025_FloridaPublicUtilitiesCompany
# 2025 ECCR final true-up exhibits, Docket 20260002-EG (filed 2026-05-05)
get "https://www.floridapsc.com/library/filings/2026/02616-2026/02616-2026.pdf" fpl_eccr_2025_lsn1    # FPL, Exhibit LSN-1
get "https://www.floridapsc.com/library/filings/2026/02608-2026/02608-2026.pdf" def_eccr_2025_kr1t    # Duke, Exhibit KR-1T
get "https://www.floridapsc.com/library/filings/2026/02603-2026/02603-2026.pdf" teco_eccr_2025_rgj1   # TECO, Exhibit RGJ-1
# FPUC Tables 3-1 and 3-2 are images: render with `pdftoppm -f 9 -l 10 -png` and read them (see data/fpuc_programs_2025_manual.csv)
