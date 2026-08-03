#!/usr/bin/env python3
"""Regression tests for the public-investment model artifact audit."""

from __future__ import annotations

import subprocess
import sys
import tempfile
from pathlib import Path

import openpyxl
from docx import Document
from openpyxl.styles import Font


HERE = Path(__file__).resolve().parent
AUDIT = HERE / "artifact_audit.py"
ARIAL = Font(name="Arial", color="FF000000")
BLUE = Font(name="Arial", color="FF0000FF")


def set_value(cell, value, font=ARIAL, number_format=None) -> None:
    cell.value = value
    cell.font = font
    if number_format:
        cell.number_format = number_format


def source_comment(basis: str) -> str:
    return (
        "Class=Fact; Source=Test Company 2025 Form 10-K; Date=2026-02-20; "
        f"Locator=Item 8, p.10; Basis={basis}"
    )


def derived_comment(basis: str) -> str:
    return f"Class=Derived; Source=N/A; Date=N/A; Locator=N/A; Basis={basis}"


def build_model(path: Path) -> None:
    wb = openpyxl.Workbook()
    wb.remove(wb.active)
    for name in (
        "Revenue Model",
        "Calculation Support",
        "Income Statement",
        "Cash Flow Statement",
        "Balance Sheet",
        "Scenarios",
        "DCF Inputs",
        "Comps",
        "Valuation Summary",
    ):
        wb.create_sheet(name)

    ws = wb["Revenue Model"]
    for col, value in enumerate(("Metric", "Unit", "2027E", "Comments"), 1):
        set_value(ws.cell(1, col), value)
    rows = (
        ("Energy revenue", "$M", "=C4*C5", derived_comment("quantity times price times period"), ARIAL, "$0.0"),
        ("YoY growth", "%", "=10%", derived_comment("current year revenue divided by prior year revenue minus one"), ARIAL, "0.0%"),
        ("Quantity", "MWh", 100, source_comment("forecast volume calibrated to disclosed capacity"), BLUE, "0.0"),
        ("Price / yield", "$/MWh", 50, source_comment("forecast price calibrated to disclosed realized price"), BLUE, "$0.0"),
    )
    for row, (metric, unit, value, comment, font, fmt) in enumerate(rows, 2):
        set_value(ws.cell(row, 1), metric)
        set_value(ws.cell(row, 2), unit)
        set_value(ws.cell(row, 3), value, font=font, number_format=fmt)
        set_value(ws.cell(row, 4), comment)

    support = wb["Calculation Support"]
    for col, value in enumerate(("Metric", "2027E", "Comments"), 1):
        set_value(support.cell(1, col), value)
    set_value(support["A2"], "Volume sanity check")
    set_value(support["B2"], "='Revenue Model'!C4")
    set_value(support["C2"], derived_comment("links displayed quantity to the physical sanity check"))

    income = wb["Income Statement"]
    set_value(income["A1"], "Revenue")
    set_value(income["B1"], "='Revenue Model'!C2")

    cash = wb["Cash Flow Statement"]
    for row, label in enumerate(("Maintenance CapEx", "Growth CapEx", "Acquisition / Integration CapEx"), 1):
        set_value(cash.cell(row, 1), label)
        set_value(cash.cell(row, 2), 1)

    balance = wb["Balance Sheet"]
    set_value(balance["A1"], "Balance Check")
    set_value(balance["B1"], "=0")

    for sheet in ("Scenarios", "DCF Inputs"):
        set_value(wb[sheet]["A1"], sheet)

    comps = wb["Comps"]
    set_value(comps["A1"], "Company")
    set_value(comps["B1"], "Role")
    for row, company in enumerate(("Peer A", "Peer B", "Peer C"), 2):
        set_value(comps.cell(row, 1), company)
        set_value(comps.cell(row, 2), "Central primary")

    valuation = wb["Valuation Summary"]
    set_value(valuation["A1"], "Valuation Method Manifest")
    headers = ("Method ID", "Method Label", "Role", "Low", "Mid", "High", "Weight", "Source Range / Formula", "Notes")
    for col, value in enumerate(headers, 1):
        set_value(valuation.cell(2, col), value)
    methods = (
        ("VAL-PE", "2027E Forward P/E", "Central", 90, 100, 110, 0.5, "Comps!A2:B4", "next-year EPS"),
        ("VAL-PS", "2027E Forward P/S", "Central", 85, 100, 115, 0.5, "Comps!A2:B4", "same-year revenue"),
    )
    for row, values in enumerate(methods, 3):
        for col, value in enumerate(values, 1):
            set_value(valuation.cell(row, col), value, number_format="0.0%" if col == 7 else None)
    wb.save(path)


def run_audit(model: Path, report: Path | None = None) -> subprocess.CompletedProcess[str]:
    command = [sys.executable, str(AUDIT), "--excel", str(model)]
    if report:
        command.extend(("--report", str(report)))
    return subprocess.run(command, capture_output=True, text=True, encoding="utf-8")


def main() -> int:
    with tempfile.TemporaryDirectory() as directory:
        root = Path(directory)
        model = root / "positive.xlsx"
        report = root / "report.docx"
        build_model(model)
        doc = Document()
        doc.add_paragraph("2027E Forward P/E 50%; 2027E Forward P/S 50%")
        doc.save(report)
        positive = run_audit(model, report)
        if positive.returncode != 0:
            print(positive.stdout)
            raise AssertionError("positive fixture must pass")

        negative = root / "negative.xlsx"
        wb = openpyxl.load_workbook(model)
        wb.create_sheet("Assumption Guide", 0)
        wb["Assumption Guide"]["A1"] = "deprecated"
        wb["Assumption Guide"]["A1"].font = ARIAL
        wb["Calculation Support"].sheet_state = "hidden"
        wb["Revenue Model"]["D4"] = "company commentary"
        wb["Revenue Model"]["D4"].font = ARIAL
        wb["Valuation Summary"]["B4"] = "2028E Forward P/S"
        wb["Valuation Summary"]["B4"].font = ARIAL
        wb.save(negative)
        failed = run_audit(negative)
        combined = failed.stdout + failed.stderr
        expected = (
            "remove deprecated governance sheet",
            "Calculation Support must be visible",
            "missing field(s)",
            "Forward P/E uses 2027 but Forward P/S uses 2028",
        )
        if failed.returncode == 0 or any(message not in combined for message in expected):
            print(combined)
            raise AssertionError("negative fixture did not trigger every expected rule")

    print("artifact_audit regression tests: PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
