"""The Excel review model must reproduce the Python analysis (scripts/verify_excel.py)."""
import sys
import unittest
from pathlib import Path

from openpyxl import load_workbook

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
import verify_excel  # noqa: E402


class ExcelModel(unittest.TestCase):
    def test_matches_python_analysis(self):
        self.assertEqual(verify_excel.check(), [])

    def test_results_are_formulas(self):
        wb = load_workbook(verify_excel.XLSX)
        for sheet, cell in (("Programs", "K4"), ("Programs", "Q4"), ("Reconciliation", "F4"), ("Summary", "B5")):
            self.assertTrue(str(wb[sheet][cell].value).startswith("="), f"{sheet}!{cell}")


if __name__ == "__main__":
    unittest.main()
