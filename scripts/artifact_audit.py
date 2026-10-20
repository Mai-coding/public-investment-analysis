#!/usr/bin/env python3
"""Audit IC model provenance, formatting and valuation consistency."""

from __future__ import annotations

import argparse
import json
import math
import re
import sys
from collections import defaultdict
from pathlib import Path
from typing import Iterable

import openpyxl
from openpyxl.utils import get_column_letter, range_boundaries
from openpyxl.worksheet.worksheet import Worksheet

from terminal_multiple import TerminalCase, central_valuation


ERROR_TOKENS = ("#REF!", "#DIV/0!", "#VALUE!", "#N/A")
GENERIC_SOURCES = {
    "research estimate",
    "company commentary",
    "company disclosure",
    "filing",
    "web research",
    "management commentary",
    "management claim",
}
COMMENT_CLASSES = {"fact", "inference", "assumption", "user-provided-unverified", "derived"}
COMMENT_FIELDS = ("class", "source", "date", "locator", "basis")
ROLE_WORDS = ("primary", "secondary", "diagnostic", "floor", "option", "central", "主锚", "诊断", "下限", "期权")
ADDRESS_RE = re.compile(r"(?<![A-Z0-9_])\$?([A-Z]{1,3})\$?(\d+)")
SHEET_CELL_RE = re.compile(r"(?:'([^']+)'|([A-Za-z0-9_ .&/-]+))!\$?([A-Z]{1,3})\$?(\d+)")


class Audit:
    def __init__(self) -> None:
        self.failures: list[str] = []
        self.warnings: list[str] = []
        self.passes: list[str] = []

    def fail(self, message: str) -> None:
        self.failures.append(message)

    def warn(self, message: str) -> None:
        self.warnings.append(message)

    def ok(self, message: str) -> None:
        self.passes.append(message)

    def print(self) -> int:
        for message in self.passes:
            print(f"[PASS] {message}")
        for message in self.warnings:
            print(f"[WARN] {message}")
        for message in self.failures:
            print(f"[FAIL] {message}")
        print(
            f"SUMMARY: {len(self.passes)} PASS / "
            f"{len(self.warnings)} WARN / {len(self.failures)} FAIL"
        )
        return 1 if self.failures else 0


def norm(value: object) -> str:
    return re.sub(r"\s+", " ", str(value or "")).strip()


def find_header(ws: Worksheet, required: Iterable[str], max_rows: int = 30) -> tuple[int, dict[str, int]] | None:
    required_l = tuple(x.lower() for x in required)
    for row in range(1, min(ws.max_row, max_rows) + 1):
        values = {norm(ws.cell(row, col).value).lower(): col for col in range(1, ws.max_column + 1)}
        if all(any(req in value for value in values) for req in required_l):
            return row, values
    return None


def header_col(headers: dict[str, int], *aliases: str) -> int | None:
    for alias in aliases:
        alias_l = alias.lower()
        for header, col in headers.items():
            if alias_l == header or alias_l in header:
                return col
    return None


def source_is_generic(value: object) -> bool:
    text = norm(value)
    low = text.lower().strip(" .:;|")
    if not text:
        return True
    if low in GENERIC_SOURCES:
        return True
    has_locator = bool(
        re.search(r"https?://|[A-Za-z]:\\|/|\.pdf\b|\.htm\b|\.html\b|\bitem\s+\d|\bpage\s+\d|第\s*\d+\s*页", text, re.I)
    )
    return any(low.startswith(item) for item in GENERIC_SOURCES) and not has_locator


def parse_addresses(value: object) -> set[str]:
    return {f"{col}{row}" for col, row in ADDRESS_RE.findall(norm(value))}


def parse_comment_fields(value: object) -> dict[str, str]:
    fields: dict[str, str] = {}
    for part in norm(value).split(";"):
        if "=" not in part:
            continue
        key, item = part.split("=", 1)
        fields[key.strip().lower()] = item.strip()
    return fields


def validate_comment(value: object) -> str | None:
    fields = parse_comment_fields(value)
    missing = [field for field in COMMENT_FIELDS if not fields.get(field)]
    if missing:
        return "missing field(s): " + ", ".join(missing)
    klass = fields["class"].lower()
    if klass not in COMMENT_CLASSES:
        return f"unsupported Class '{fields['class']}'"
    if len(fields["basis"]) < 8:
        return "Basis is too short to explain the derivation or calibration"
    if klass == "derived":
        return None
    if source_is_generic(fields["source"]):
        return f"generic or unresolvable Source '{fields['source']}'"
    if not re.fullmatch(r"\d{4}-\d{2}-\d{2}", fields["date"]):
        return "Date must use YYYY-MM-DD"
    locator = fields["locator"]
    if locator.lower() in {"n/a", "na", "none"} or not re.search(
        r"https?://|[A-Za-z]:\\|\.pdf\b|\bitem\b|\bsection\b|\bpage\b|\bp\.?\s*\d|第\s*\d+\s*页|\d{1,2}:\d{2}",
        locator,
        re.I,
    ):
        return f"Locator is not resolvable: '{locator}'"
    return None


def comments_header(ws: Worksheet, exact: bool = False) -> tuple[int, int, int] | None:
    for row in range(1, min(ws.max_row, 30) + 1):
        values = [norm(ws.cell(row, col).value) for col in range(1, ws.max_column + 1)]
        comment_col = None
        for col, value in enumerate(values, 1):
            low = value.lower()
            if (exact and low == "comments") or (
                not exact and (low == "comments" or "source / rationale" in low or "source & rationale" in low)
            ):
                comment_col = col
                break
        if not comment_col:
            continue
        metric_col = None
        for col, value in enumerate(values[: comment_col - 1], 1):
            low = value.lower()
            if any(alias in low for alias in ("metric", "line item", "revenue stream", "driver")):
                metric_col = col
                break
        if metric_col is None:
            metric_col = next((col for col, value in enumerate(values[: comment_col - 1], 1) if value), 1)
        return row, comment_col, metric_col
    return None


def model_rows(ws: Worksheet, header_row: int, comments_col: int) -> list[int]:
    return [
        row
        for row in range(header_row + 1, ws.max_row + 1)
        if not ws.row_dimensions[row].hidden
        and any(norm(ws.cell(row, col).value) for col in range(1, comments_col))
    ]


def revenue_metric_kind(value: object) -> str | None:
    low = norm(value).lower()
    if not low:
        return None
    if any(t in low for t in ('同比', '增速', '增长率')) or "yoy" in low or "year-over-year" in low or ("growth" in low and "revenue" not in low):
        return "yoy"
    if 'share' in low or '占比' in low or 'mix %' in low:
        return 'share'
    if any(token in low for token in ("quantity", "volume", "units", "customers", "capacity", "generation")):
        return "quantity"
    if any(token in low for token in ("price", "yield", "arpu", "asp", "rate")):
        return "price"
    if "revenue" in low and not any(token in low for token in ("total", "consolidated", "growth")):
        return "revenue"
    return None


def revenue_row_kind(ws: Worksheet, row: int, metric_col: int) -> str | None:
    kind = revenue_metric_kind(ws.cell(row, metric_col).value)
    if kind != "revenue":
        return kind
    label = norm(ws.cell(row, metric_col).value).lower()
    nearby = " | ".join(norm(ws.cell(row, col).value) for col in range(metric_col + 1, min(ws.max_column, metric_col + 3) + 1)).lower()
    if not re.search(r"\$(?:m|mm|b)\b", nearby):
        return None
    if re.search(r"\b(total|consolidated|reported revenue|revenue ex-|bridge)\b|^20\d{2}[ae]\b", label):
        return None
    return "revenue"


def blue_hardcode(cell) -> bool:
    if cell.value is None or (isinstance(cell.value, str) and cell.value.startswith("=")):
        return False
    color = cell.font.color
    return bool(color and color.type == "rgb" and str(color.rgb).upper() in {"000000FF", "FF0000FF"})


def percent_format(number_format: str | None) -> bool:
    return "%" in (number_format or "")


def extract_docx_text(path: Path) -> str:
    from docx import Document

    doc = Document(path)
    parts = [p.text for p in doc.paragraphs]
    for table in doc.tables:
        for row in table.rows:
            parts.extend(cell.text for cell in row.cells)
    return "\n".join(parts)


def audit_governance(wb, audit: Audit) -> None:
    forbidden = [name for name in ("Assumption Guide", "Source Library") if name in wb.sheetnames]
    if forbidden:
        audit.fail("Workbook: remove deprecated governance sheet(s): " + ", ".join(forbidden))
    else:
        audit.ok("Deprecated Assumption Guide and Source Library sheets are absent")
    for required in ("Revenue Model", "Calculation Support"):
        if required not in wb.sheetnames:
            audit.fail(f"Workbook: missing required sheet '{required}'")
    if "Revenue Model" not in wb.sheetnames:
        return
    if "Calculation Support" in wb.sheetnames:
        revenue_index = wb.sheetnames.index("Revenue Model")
        support_index = wb.sheetnames.index("Calculation Support")
        if support_index != revenue_index + 1:
            audit.fail("Workbook: Calculation Support must immediately follow Revenue Model")
        elif wb["Calculation Support"].sheet_state != "visible":
            audit.fail("Calculation Support must be visible")
        else:
            audit.ok("Calculation Support is visible and immediately follows Revenue Model")

    ws = wb["Revenue Model"]
    hidden_rows = [
        row
        for row in range(1, ws.max_row + 1)
        if ws.row_dimensions[row].hidden and any(norm(ws.cell(row, col).value) for col in range(1, ws.max_column + 1))
    ]
    if hidden_rows:
        audit.fail(
            "Revenue Model: populated hidden rows are not allowed; move calculation support to Calculation Support "
            f"(first hidden row: {hidden_rows[0]})"
        )
    found = comments_header(ws, exact=True)
    if not found:
        audit.fail("Revenue Model: missing exact rightmost Comments header")
        return
    header_row, comments_col, metric_col = found
    last_header_col = max((col for col in range(1, ws.max_column + 1) if norm(ws.cell(header_row, col).value)), default=0)
    if comments_col != last_header_col:
        audit.fail(f"Revenue Model!{get_column_letter(comments_col)}{header_row}: Comments must be the rightmost header")
    rows = model_rows(ws, header_row, comments_col)
    for row in rows:
        error = validate_comment(ws.cell(row, comments_col).value)
        if error:
            audit.fail(f"Revenue Model!{get_column_letter(comments_col)}{row}: {error}")
    if rows and not any(validate_comment(ws.cell(row, comments_col).value) for row in rows):
        audit.ok(f"Revenue Model has parseable row-level Comments for {len(rows)} visible model rows")

    ordered = [(row, revenue_row_kind(ws, row, metric_col)) for row in rows]
    methods = {}
    for index, (row, kind) in enumerate(ordered):
        fields = parse_comment_fields(ws.cell(row, comments_col).value)
        match = re.search(r'\bModel=(QuantityPrice|GrowthPercent|RevenueShare)\b', fields.get('basis', ''), re.I)
        method = fields.get('model') or (match.group(1) if match else None)
        if method:
            methods[row] = method.lower()
            ordered[index] = (row, 'revenue')
    for index, (row, kind) in enumerate(ordered):
        if kind is not None or index + 3 >= len(ordered):
            continue
        nearby = " | ".join(
            norm(ws.cell(row, col).value)
            for col in range(metric_col + 1, min(ws.max_column, metric_col + 3) + 1)
        ).lower()
        following = [item_kind for _, item_kind in ordered[index + 1 : index + 4]]
        if re.search(r"\$(?:m|mm|b)\b", nearby) and following == ["yoy", "quantity", "price"]:
            ordered[index] = (row, "revenue")
    revenue_starts = [index for index, (_, kind) in enumerate(ordered) if kind == "revenue"]
    if not revenue_starts:
        audit.fail("Revenue Model: no auditable revenue-stream block found")
    valid_blocks = 0
    for index in revenue_starts:
        row = ordered[index][0]
        method = methods.get(row)
        expected = {'quantityprice': ['revenue', 'yoy', 'quantity', 'price'],
                    'growthpercent': ['revenue', 'yoy'], 'revenueshare': ['revenue', 'share']}.get(method)
        if expected is None:
            audit.fail(f"Revenue Model!{row}: Comments must declare Model=QuantityPrice/GrowthPercent/RevenueShare")
            continue
        sequence = [kind for _, kind in ordered[index : index + len(expected)]]
        if sequence != expected:
            audit.fail(
                f"Revenue Model!{get_column_letter(metric_col)}{row}: revenue stream order must be "
                + ' -> '.join(expected) + f' for {method}'
            )
            continue
        if method == 'quantityprice':
            fields = parse_comment_fields(ws.cell(row, comments_col).value)
            disclosure = fields.get('disclosure', '')
            if len(disclosure) < 12 or any(t in disclosure.lower() for t in ('not disclosed', 'not reported', 'unavailable')):
                audit.fail(f"Revenue Model!{row}: QuantityPrice requires actual filing quantity/price Disclosure locators")
                continue
        valid_blocks += 1
    if revenue_starts and valid_blocks == len(revenue_starts):
        audit.ok(f"Revenue Model contains {valid_blocks} disclosure-appropriate revenue-stream block(s)")


def audit_hardcodes_fonts_formats(wb, audit: Audit) -> None:
    provenance_failures: list[str] = []
    bad_fonts: list[str] = []
    for ws in wb.worksheets:
        support_header = comments_header(ws) if ws.title in {"Revenue Model", "Calculation Support"} else None
        for row in ws.iter_rows():
            for cell in row:
                if cell.value is not None and (cell.font.name or "").lower() != "arial":
                    bad_fonts.append(f"{ws.title}!{cell.coordinate} ({cell.font.name or 'None'})")
                if ws.title in {"Revenue Model", "Calculation Support"} and blue_hardcode(cell):
                    if not support_header:
                        provenance_failures.append(f"{ws.title}!{cell.coordinate} (missing Comments column)")
                    else:
                        _, comment_col, _ = support_header
                        error = validate_comment(ws.cell(cell.row, comment_col).value)
                        if error:
                            provenance_failures.append(f"{ws.title}!{cell.coordinate} ({error})")
    if bad_fonts:
        for item in bad_fonts[:40]:
            audit.fail(f"Font not Arial: {item}")
        if len(bad_fonts) > 40:
            audit.fail(f"Font not Arial: {len(bad_fonts) - 40} additional cells")
    else:
        audit.ok("All populated Excel cells use Arial")

    profile = json.loads((Path(__file__).resolve().parents[1] / 'assets' / 'excel_model_style.json').read_text(encoding='utf-8'))
    allowed = set(profile['font']['allowed_body_pt'])
    for sheet in wb:
        if sheet.sheet_view.showGridLines is not False:
            audit.fail(f'{sheet.title}: reference model style requires hidden gridlines')
        if sheet.title in {'Revenue Model', 'Income Statement', 'Cash Flow Statement', 'Balance Sheet', 'Scenarios'} and not sheet.freeze_panes:
            audit.fail(f'{sheet.title}: freeze model headers/labels for navigation')
        oversized = [c.coordinate for row in sheet for c in row if c.value is not None and c.font.sz not in allowed]
        if oversized:
            audit.fail(f'{sheet.title}: model font size must be 8–10 pt (first: {oversized[0]})')
    if provenance_failures:
        for item in provenance_failures[:60]:
            audit.fail(f"Blue hardcode missing row-level provenance: {item}")
        if len(provenance_failures) > 60:
            audit.fail(f"Blue hardcodes: {len(provenance_failures) - 60} additional provenance failures")
    else:
        audit.ok("Blue hardcodes in Revenue Model and Calculation Support have row-level provenance")

    bad_growth: set[str] = set()
    keywords = re.compile(r"\b(growth|yoy|cagr)\b", re.I)
    def is_growth_label(value: object) -> bool:
        text = norm(value)
        return (
            bool(keywords.search(text))
            and len(text.split()) <= 6
            and not bool(re.search(r"[.;:]|\b(capex|capital expenditure|growth capital)\b", text, re.I))
        )

    for ws in wb.worksheets:
        for row in range(1, ws.max_row + 1):
            labels = [col for col in range(1, min(ws.max_column, 2) + 1) if is_growth_label(ws.cell(row, col).value)]
            for label_col in labels:
                populated = [
                    col for col in range(label_col + 1, ws.max_column + 1)
                    if isinstance(ws.cell(row, col).value, (int, float))
                    or (isinstance(ws.cell(row, col).value, str) and ws.cell(row, col).value.startswith("="))
                ]
                if not populated:
                    continue
                last = max(populated)
                for col in range(label_col + 1, last + 1):
                    cell = ws.cell(row, col)
                    is_value_or_blank = (
                        cell.value is None
                        or isinstance(cell.value, (int, float))
                        or (isinstance(cell.value, str) and cell.value.startswith("="))
                    )
                    if is_value_or_blank and not percent_format(cell.number_format):
                        bad_growth.add(f"{ws.title}!{cell.coordinate}")
        for col in range(1, ws.max_column + 1):
            labels = [row for row in range(1, min(ws.max_row, 20) + 1) if is_growth_label(ws.cell(row, col).value)]
            for label_row in labels:
                populated = [
                    row for row in range(label_row + 1, ws.max_row + 1)
                    if isinstance(ws.cell(row, col).value, (int, float))
                    or (isinstance(ws.cell(row, col).value, str) and ws.cell(row, col).value.startswith("="))
                ]
                if not populated:
                    continue
                for row in range(label_row + 1, max(populated) + 1):
                    cell = ws.cell(row, col)
                    if (
                        isinstance(cell.value, (int, float))
                        or (isinstance(cell.value, str) and cell.value.startswith("="))
                    ) and not percent_format(cell.number_format):
                        bad_growth.add(f"{ws.title}!{cell.coordinate}")
    if bad_growth:
        for item in sorted(bad_growth)[:60]:
            audit.fail(f"Growth/YoY/CAGR cell is not percentage-formatted: {item}")
        if len(bad_growth) > 60:
            audit.fail(f"Growth formats: {len(bad_growth) - 60} additional cells")
    else:
        audit.ok("Growth/YoY/CAGR ranges use percentage formats, including styled blanks")


def formula_dependencies(wb) -> dict[tuple[str, str], set[tuple[str, str]]]:
    graph: dict[tuple[str, str], set[tuple[str, str]]] = defaultdict(set)
    for ws in wb.worksheets:
        for row in ws.iter_rows():
            for cell in row:
                if not isinstance(cell.value, str) or not cell.value.startswith("="):
                    continue
                node = (ws.title, cell.coordinate)
                formula = cell.value
                for match in SHEET_CELL_RE.finditer(formula):
                    sheet = match.group(1) or match.group(2).strip()
                    graph[node].add((sheet, f"{match.group(3)}{match.group(4)}"))
                local_formula = re.sub(
                    r"(?:'[^']+'|[A-Za-z0-9_ .&/-]+)!\$?[A-Z]{1,3}\$?\d+(?::\$?[A-Z]{1,3}\$?\d+)?",
                    "",
                    formula,
                )
                for col, row_num in ADDRESS_RE.findall(local_formula):
                    graph[node].add((ws.title, f"{col}{row_num}"))
    return graph


def audit_errors_cycles_balances(wb, data_wb, audit: Audit) -> None:
    for ws in wb.worksheets:
        data_ws = data_wb[ws.title]
        for row in ws.iter_rows():
            for cell in row:
                formula = norm(cell.value)
                cached = norm(data_ws[cell.coordinate].value)
                for token in ERROR_TOKENS:
                    if token in formula or token == cached:
                        audit.fail(f"{ws.title}!{cell.coordinate}: formula error {token}")
    graph = formula_dependencies(wb)
    state: dict[tuple[str, str], int] = {}
    stack: list[tuple[str, str]] = []
    cycles: set[tuple[tuple[str, str], ...]] = set()

    def visit(node: tuple[str, str]) -> None:
        state[node] = 1
        stack.append(node)
        for dep in graph.get(node, ()):
            if dep not in graph:
                continue
            if state.get(dep, 0) == 0:
                visit(dep)
            elif state.get(dep) == 1:
                start = stack.index(dep)
                cycles.add(tuple(stack[start:] + [dep]))
        stack.pop()
        state[node] = 2

    for node in graph:
        if state.get(node, 0) == 0:
            visit(node)
    for cycle in list(cycles)[:10]:
        audit.fail("Circular reference: " + " -> ".join(f"{s}!{c}" for s, c in cycle))
    if not cycles:
        audit.ok("No formula errors or detectable circular references")

    balance_found = False
    for ws in wb.worksheets:
        data_ws = data_wb[ws.title]
        for row in ws.iter_rows():
            for cell in row:
                if "balance check" not in norm(cell.value).lower():
                    continue
                balance_found = True
                values = []
                for col in range(cell.column + 1, ws.max_column + 1):
                    value = data_ws.cell(cell.row, col).value
                    if isinstance(value, (int, float)):
                        values.append((data_ws.cell(cell.row, col).coordinate, value))
                for address, value in values:
                    if abs(value) > 0.01:
                        audit.fail(f"{ws.title}!{address}: Balance Check is {value}, expected 0")
    if balance_found:
        audit.ok("Balance Check rows found and cached numeric values are within tolerance")
    else:
        audit.warn("No Balance Check row found")


def diagnostic_comp_rows(ws: Worksheet) -> set[int]:
    rows: set[int] = set()
    diagnostic_section = False
    for row in range(1, ws.max_row + 1):
        text = " | ".join(norm(ws.cell(row, col).value) for col in range(1, ws.max_column + 1)).lower()
        if "full-universe" in text or "diagnostic only" in text or "zero final weight" in text:
            diagnostic_section = True
        if "selected segment anchors" in text:
            diagnostic_section = False
        if diagnostic_section or any(word in text for word in ("diagnostic", "not used", "excluded from central", "hardware floor", "zero weight")):
            rows.add(row)
    return rows


def find_method_table(ws: Worksheet, audit: Audit) -> tuple[list[dict[str, object]], bool]:
    manifest_row = None
    for row in range(1, ws.max_row + 1):
        if "valuation method manifest" in norm(ws.cell(row, 1).value).lower():
            manifest_row = row
            break
    exact = manifest_row is not None
    if exact:
        header_row = manifest_row + 1
        while header_row <= ws.max_row and "method" not in norm(ws.cell(header_row, 1).value).lower():
            header_row += 1
        headers = {norm(ws.cell(header_row, col).value).lower(): col for col in range(1, ws.max_column + 1)}
        method_col = header_col(headers, "method label", "method")
        role_col = header_col(headers, "role")
        weight_col = header_col(headers, "weight")
        low_col = header_col(headers, "low")
        mid_col = header_col(headers, "mid", "base")
        high_col = header_col(headers, "high")
        source_formula_col = header_col(headers, "source range / formula", "source range", "formula")
        family_col = header_col(headers, "method family")
        if not all((method_col, role_col, weight_col, low_col, mid_col, high_col)):
            audit.fail(f"Valuation Summary!{header_row}: incomplete Valuation Method Manifest headers")
            return [], exact
    else:
        header_row = None
        for row in range(1, ws.max_row + 1):
            values = [norm(ws.cell(row, col).value).lower() for col in range(1, ws.max_column + 1)]
            if "method" in values and "weight" in values:
                header_row = row
                break
        if not header_row:
            audit.fail("Valuation Summary: missing Valuation Method Manifest")
            return [], exact
        headers = {norm(ws.cell(header_row, col).value).lower(): col for col in range(1, ws.max_column + 1)}
        method_col = header_col(headers, "method")
        weight_col = header_col(headers, "weight")
        role_col = None
        family_col = None
        low_col = mid_col = high_col = None
        audit.warn("Valuation Summary uses legacy method reconciliation; new models must use exact Valuation Method Manifest schema")
    methods: list[dict[str, object]] = []
    for row in range(header_row + 1, ws.max_row + 1):
        label = norm(ws.cell(row, method_col).value)
        if not label:
            if methods:
                break
            continue
        weight = ws.cell(row, weight_col).value
        if not isinstance(weight, (int, float)):
            if methods:
                break
            continue
        role = norm(ws.cell(row, role_col).value).lower() if role_col else ("central" if weight > 0 else "diagnostic")
        methods.append({
            "row": row,
            "label": label,
            "role": role,
            "weight": weight,
            "family": norm(ws.cell(row, family_col).value) if family_col else '',
            "value_cells": [ws.cell(row, col) for col in (low_col, mid_col, high_col, source_formula_col if exact else None) if col],
        })
    return methods, exact


def audit_valuation(wb, audit: Audit, report_text: str | None) -> None:
    if "Comps" not in wb.sheetnames and "Valuation Summary" not in wb.sheetnames:
        return  # Task 2 operating model; Task 3 has not added valuation yet.
    if "Comps" not in wb.sheetnames or "Valuation Summary" not in wb.sheetnames:
        audit.fail("Workbook: Comps and Valuation Summary sheets are required")
        return
    comps = wb["Comps"]
    role_header = None
    central_peer_count = 0
    for row in range(1, min(comps.max_row, 20) + 1):
        values = {norm(comps.cell(row, col).value).lower(): col for col in range(1, comps.max_column + 1)}
        if "company" in values and any(key in values for key in ("role", "peer role", "valuation role")):
            role_header = (row, values)
            break
    if role_header:
        header_row, headers = role_header
        role_col = headers.get("role") or headers.get("peer role") or headers.get("valuation role")
        company_col = header_col(headers, "company")
        for row in range(header_row + 1, comps.max_row + 1):
            company = norm(comps.cell(row, company_col).value)
            if not company:
                break
            role = norm(comps.cell(row, role_col).value)
            if not any(word in role.lower() for word in ROLE_WORDS):
                audit.fail(f"Comps!{get_column_letter(role_col)}{row}: unclassified peer role '{role}'")
            if "central" in role.lower() or "主锚" in role:
                central_peer_count += 1
    else:
        legacy_header = find_header(comps, ("company", "use in valuation"))
        if not legacy_header:
            audit.fail("Comps: missing peer role/use-in-valuation column")
        else:
            header_row, headers = legacy_header
            use_col = header_col(headers, "use in valuation")
            company_col = header_col(headers, "company")
            for row in range(header_row + 1, comps.max_row + 1):
                company = norm(comps.cell(row, company_col).value)
                if not company:
                    break
                use = norm(comps.cell(row, use_col).value).lower()
                if not any(word in use for word in ROLE_WORDS):
                    audit.fail(f"Comps!{get_column_letter(use_col)}{row}: peer role is not explicit")
            audit.warn("Comps uses legacy free-text roles; new models should use an explicit Role column")

    methods, exact = find_method_table(wb["Valuation Summary"], audit)
    if not methods:
        return
    central = []
    for method in methods:
        role = str(method["role"]).lower()
        weight = float(method["weight"])
        label = str(method["label"])
        if role not in {"central", "diagnostic"}:
            audit.fail(f"Valuation Summary!A{method['row']}: Role must be Central or Diagnostic, got '{role}'")
        if role == "diagnostic" and abs(weight) > 1e-12:
            audit.fail(f"Valuation Summary!A{method['row']}: Diagnostic method '{label}' has positive weight {weight}")
        if str(method['family']).lower() == 'terminal' and role != 'diagnostic':
            audit.fail(f"Valuation Summary!A{method['row']}: Terminal must be Diagnostic with zero weight")
        if role == "central" and weight > 0:
            central.append(method)
        if ("full-universe" in label.lower() or "diagnostic" in label.lower()) and abs(weight) > 1e-12:
            audit.fail(f"Valuation Summary!A{method['row']}: full-universe/diagnostic method has positive weight")
    if not central:
        audit.fail("Valuation Summary: no positive-weight Central method")
    else:
        audit.ok(f"Valuation methods: {len(central)} positive-weight Central method(s); Diagnostic methods carry zero weight")
        total_weight = sum(float(method["weight"]) for method in central)
        if abs(total_weight - 1.0) > 0.001:
            audit.fail(f"Valuation Summary: positive-weight Central methods sum to {total_weight:.3f}, expected 1.000")
        for family, expected in (('Forward Comps', 1.0), ('Terminal', 0.0)):
            actual = sum(float(m['weight']) for m in central if str(m['family']).lower() == family.lower())
            if not math.isclose(actual, expected, abs_tol=1e-8):
                audit.fail(f"Valuation Method Manifest: {family} Central weight must be {expected:.0%}, got {actual:.1%}")
        if any(str(m['family']).lower() not in {'forward comps', 'terminal'} for m in central):
            audit.fail('Valuation Method Manifest: Central methods need a valid Method Family')
    central_comp_method = any(
        any(token in str(method["label"]).lower() for token in ("comp", "peer", "median", "p/s", "p/e", "中位"))
        for method in central
    )
    if exact and central_comp_method and central_peer_count < 3:
        audit.fail(
            f"Comps: central comparable method requires at least 3 Central primary peers; found {central_peer_count}"
        )

    diagnostic_rows = diagnostic_comp_rows(comps)
    for method in central:
        cells = method["value_cells"]
        if not exact:
            cells = [wb["Valuation Summary"].cell(method["row"], 2)]
        for cell in cells:
            formula = cell.value if isinstance(cell.value, str) else ""
            for match in SHEET_CELL_RE.finditer(formula):
                sheet = match.group(1) or match.group(2).strip()
                row = int(match.group(4))
                if sheet == "Comps" and row in diagnostic_rows:
                    audit.fail(
                        f"Valuation Summary!{cell.coordinate}: positive-weight Central method references diagnostic Comps row {row}"
                    )
    if report_text:
        missing = [str(method["label"]) for method in central if str(method["label"]).lower() not in report_text.lower()]
        if missing and exact:
            audit.fail("Report central valuation table/text is missing method(s): " + ", ".join(missing))
        elif missing:
            audit.warn("Legacy report does not reproduce method label(s) verbatim: " + ", ".join(missing))
        else:
            audit.ok("Report includes every positive-weight Central valuation method")
        if exact:
            for method in central:
                label = str(method["label"])
                index = report_text.lower().find(label.lower())
                if index < 0:
                    continue
                window = report_text[index:index + 500]
                pct = float(method["weight"]) * 100
                expected = {f"{pct:.0f}%", f"{pct:.1f}%", f"{pct:.2f}%"}
                if not any(value in window for value in expected):
                    audit.fail(
                        f"Report: method '{label}' is present but its Manifest weight ({pct:.1f}%) is not shown nearby"
                    )

    lockup_title_row = None
    for row in range(1, wb["Valuation Summary"].max_row + 1):
        text = " ".join(norm(wb["Valuation Summary"].cell(row, col).value) for col in range(1, 4)).lower()
        if ("lock-up" in text or "lockup" in text or "锁定期" in text or "解禁" in text) and ("supply" in text or "供给" in text):
            lockup_title_row = row
            break
    if lockup_title_row:
        ws = wb["Valuation Summary"]
        header_row = lockup_title_row + 1
        while header_row <= min(ws.max_row, lockup_title_row + 8):
            row_text = " | ".join(norm(ws.cell(header_row, col).value) for col in range(1, ws.max_column + 1)).lower()
            if "share" in row_text or "股数" in row_text:
                break
            header_row += 1
        headers = {norm(ws.cell(header_row, col).value).lower(): col for col in range(1, ws.max_column + 1)}
        required_groups = {
            "release date/point": ("release", "释放日期"),
            "eligible shares": ("eligible shares", "可出售股数"),
            "float ratio": ("% of", "% float", "流通盘"),
            "cumulative supply": ("cumulative", "累计"),
            "condition": ("condition", "条件", "price"),
        }
        missing_groups = [
            name for name, aliases in required_groups.items()
            if not any(any(alias in header for alias in aliases) for header in headers)
        ]
        has_adv = any("adv" in header or "average volume" in header or "平均成交量" in header for header in headers)
        if missing_groups:
            audit.fail(f"Valuation Summary!{header_row}: lock-up supply map missing {', '.join(missing_groups)}")
        if not has_adv:
            if exact:
                audit.fail(f"Valuation Summary!{header_row}: lock-up supply map missing 20D/60D ADV ratios")
            else:
                audit.warn("Legacy lock-up supply map lacks 20D/60D ADV ratios; new models must include them")
        if not missing_groups and has_adv:
            audit.ok("Lock-up supply map includes release, conditions, float/ADV ratios and cumulative supply")


def workbook_label_rows(wb) -> list[tuple[str, int, str]]:
    rows: list[tuple[str, int, str]] = []
    for ws in wb.worksheets:
        for row in range(1, ws.max_row + 1):
            text = " | ".join(norm(ws.cell(row, col).value) for col in range(1, ws.max_column + 1))
            if text:
                rows.append((ws.title, row, text))
    return rows


def audit_financial_policies(wb, data_wb, audit: Audit) -> None:
    labels = workbook_label_rows(wb)
    low_rows = [(sheet, row, text.lower()) for sheet, row, text in labels]

    capex_present = any("capex" in text or "capital expenditure" in text for _, _, text in low_rows)
    if capex_present:
        missing = []
        for name, aliases in {
            "maintenance": ("maintenance capex", "maintenance capital"),
            "growth": ("growth capex", "growth capital"),
            "acquisition/integration": ("acquisition capex", "integration capex", "acquisition / integration"),
        }.items():
            if not any(any(alias in text for alias in aliases) for _, _, text in low_rows):
                missing.append(name)
        if missing:
            audit.fail("CapEx schedule missing classification(s): " + ", ".join(missing))
        else:
            audit.ok("CapEx is split into maintenance, growth and acquisition/integration")

    buyback_rows = [(sheet, row) for sheet, row, text in low_rows if "repurchase" in text or "buyback" in text]
    if not buyback_rows:
        return
    constraints = {
        "minimum cash": ("minimum cash", "cash floor"),
        "liquidity": ("liquidity", "available liquidity"),
        "leverage": ("leverage", "net debt / ebitda", "debt / ebitda"),
        "authorization": ("authorization", "authorised", "authorized amount"),
    }
    missing_constraints = [
        name
        for name, aliases in constraints.items()
        if not any(any(alias in text for alias in aliases) for _, _, text in low_rows)
    ]
    if missing_constraints:
        audit.fail("Repurchase policy missing constraint(s): " + ", ".join(missing_constraints))
    else:
        audit.ok("Repurchase policy names minimum-cash, liquidity, leverage and authorization constraints")

    floor_rows = [(sheet, row) for sheet, row, text in low_rows if "minimum cash" in text or "cash floor" in text]
    ending_rows = [(sheet, row) for sheet, row, text in low_rows if "ending cash" in text or "cash balance" in text]
    comparisons = 0
    for floor_sheet, floor_row in floor_rows:
        floor_ws = data_wb[floor_sheet]
        for ending_sheet, ending_row in ending_rows:
            if ending_sheet != floor_sheet:
                continue
            end_ws = data_wb[ending_sheet]
            for col in range(1, max(floor_ws.max_column, end_ws.max_column) + 1):
                floor = floor_ws.cell(floor_row, col).value
                ending = end_ws.cell(ending_row, col).value
                if isinstance(floor, (int, float)) and isinstance(ending, (int, float)):
                    comparisons += 1
                    if ending + 1e-9 < floor:
                        audit.fail(
                            f"{ending_sheet}!{end_ws.cell(ending_row, col).coordinate}: ending cash {ending} "
                            f"is below minimum cash {floor}"
                        )
    if comparisons:
        audit.ok(f"Ending cash meets the disclosed floor in {comparisons} cached period(s)")
    else:
        audit.warn("Repurchase cash-floor stress test has no cached numeric periods; recalculate workbook before delivery")


FORWARD_METRICS = {
    "Forward P/E": ("forward p/e", "forward pe"),
    "Forward P/S": ("forward p/s", "forward ps"),
    "Forward EV/EBITDA": ("forward ev/ebitda",),
    "Forward EV/Revenue": ("forward ev/revenue", "forward ev/sales"),
    "Forward EV/FCF": ("forward ev/fcf",),
    "Forward FCF yield": ("forward fcf yield",),
    "Forward P/TBV": ("forward p/tbv",),
    "Forward P/BV": ("forward p/bv", "forward p/b "),
    "Forward P/AFFO": ("forward p/affo",),
    "Forward P/NAV": ("forward p/nav",),
}


def audit_forward_periods(wb, audit: Audit) -> None:
    """Every sector-appropriate forward multiple must use one shared, explicit forecast year."""
    if "Valuation Summary" not in wb.sheetnames:
        return
    ws = wb["Valuation Summary"]
    metric_years: dict[str, set[str]] = {}
    for row in range(1, ws.max_row + 1):
        row_text = " | ".join(norm(ws.cell(row, col).value) for col in range(1, ws.max_column + 1))
        low = row_text.lower() + " "
        for metric, patterns in FORWARD_METRICS.items():
            if any(pattern in low for pattern in patterns):
                metric_years.setdefault(metric, set()).update(re.findall(r"\b(20\d{2})E?\b", row_text, re.I))
    if not metric_years and "Terminal Cases" in wb.sheetnames:
        # The terminal-case audit owns base/observation years for new models.
        return
    if not metric_years:
        audit.fail("Valuation Summary: no forward valuation multiple with an explicit forecast year")
        return
    missing = [metric for metric, years in metric_years.items() if not years]
    ambiguous = [metric for metric, years in metric_years.items() if len(years) > 1]
    if missing:
        audit.fail("Valuation Summary: forward multiple(s) lack an explicit forecast year: " + ", ".join(missing))
        return
    if ambiguous:
        audit.fail("Valuation Summary: each forward multiple must use one unambiguous forecast year: " + ", ".join(ambiguous))
        return
    years = {metric: next(iter(values)) for metric, values in metric_years.items()}
    if len(set(years.values())) > 1:
        detail = ", ".join(f"{metric}={year}" for metric, year in years.items())
        audit.fail(f"Valuation Summary: forward multiples use mixed forecast years ({detail})")
    else:
        audit.ok(f"{len(years)} forward multiple(s) share one explicit forecast year ({next(iter(years.values()))}E)")


PRICE_BAND_COLUMNS = {
    "band": ("band",),
    "low": ("low",),
    "high": ("high",),
    "operating state": ("operating state",),
    "valuation regime": ("valuation regime",),
    "required conditions": ("required condition", "conditions"),
    "key kpis": ("key kpi", "kpi"),
    "driver": ("driver",),
    "distance": ("distance",),
    "robustness": ("robustness",),
    "actionability": ("actionability",),
    "evidence status": ("evidence status",),
    "evidence ref": ("evidence ref",),
}


def audit_price_bands(wb, audit: Audit, data_wb=None) -> None:
    """Price Band Map replaces the single target price as the core valuation output."""
    if "Valuation Summary" not in wb.sheetnames:
        return
    ws = wb["Valuation Summary"]
    start_failures = len(audit.failures)
    title_row = next(
        (row for row in range(1, ws.max_row + 1) if "price band map" in norm(ws.cell(row, 1).value).lower()),
        None,
    )
    if title_row is None:
        audit.fail("Valuation Summary: missing 'Price Band Map' (4–5 Operating State × Valuation Regime bands)")
    else:
        header_row = title_row + 1
        headers = {norm(ws.cell(header_row, col).value).lower(): col for col in range(1, ws.max_column + 1)}
        cols: dict[str, int] = {}
        for key, aliases in PRICE_BAND_COLUMNS.items():
            col = next((c for h, c in headers.items() if h and any(alias in h for alias in aliases)), None)
            if col:
                cols[key] = col
        missing = [key for key in PRICE_BAND_COLUMNS if key not in cols]
        if missing:
            audit.fail(f"Valuation Summary!{header_row}: Price Band Map missing column(s): {', '.join(missing)}")
        else:
            bands = []
            for row in range(header_row + 1, ws.max_row + 1):
                label = norm(ws.cell(row, cols["band"]).value)
                if not label:
                    break
                values_ws = data_wb[ws.title] if data_wb is not None else ws
                bands.append((row, label, values_ws.cell(row, cols["low"]).value, values_ws.cell(row, cols["high"]).value))
                distance = norm(ws.cell(row, cols["distance"]).value).lower()
                if distance not in {"low", "medium", "high"}:
                    audit.fail(f"Valuation Summary!{row}: Distance to Band must be Low/Medium/High, got '{distance}'")
                robustness = norm(ws.cell(row, cols["robustness"]).value).lower()
                if not robustness.startswith(("high", "medium", "low")):
                    audit.fail(f"Valuation Summary!{row}: Robustness must start with High/Medium/Low")
                for key in ("operating state", "valuation regime", "required conditions", "key kpis", "driver", "actionability", "evidence status", "evidence ref"):
                    if not norm(ws.cell(row, cols[key]).value):
                        audit.fail(f"Valuation Summary!{row}: band '{label}' has empty {key}")
            if not 4 <= len(bands) <= 5:
                audit.fail(f"Valuation Summary: Price Band Map needs 4–5 bands; found {len(bands)}")
            numeric = [(r, lab, lo, hi) for r, lab, lo, hi in bands if isinstance(lo, (int, float)) and isinstance(hi, (int, float))]
            formula_bounds = len(numeric) < len(bands)
            if not formula_bounds and bands:
                for (r1, _, lo1, hi1), (r2, _, lo2, hi2) in zip(numeric, numeric[1:]):
                    if not (lo1 < hi1 and lo2 < hi2 and hi2 <= lo1 + 1e-9):
                        audit.fail(f"Valuation Summary!{r1}-{r2}: bands must be ordered high→low without overlap")
                widths = [hi - lo for _, _, lo, hi in numeric[1:-1] if hi > lo]
                if len(widths) >= 3 and max(widths) - min(widths) <= 0.01 * max(widths):
                    audit.fail("Valuation Summary: interior Price Bands are mechanically equal-width; set bounds at regime breaks")
            elif formula_bounds:
                audit.warn("Price Band bounds are formulas without cached values; recalculate to verify order/width")
            if bands and len(audit.failures) == start_failures:
                audit.ok(f"Price Band Map has {len(bands)} fully specified band(s)")

    bridge = False
    for row in range(1, ws.max_row + 1):
        if "3y return bridge" in norm(ws.cell(row, 1).value).lower():
            text = " | ".join(
                norm(ws.cell(r, c).value).lower()
                for r in range(row, min(ws.max_row, row + 8) + 1)
                for c in range(1, min(ws.max_column, 6) + 1)
            )
            parts = ("cagr", "shareholder yield", "multiple")
            missing_parts = [part for part in parts if part not in text]
            if missing_parts:
                audit.fail("3Y Return Bridge missing component(s): " + ", ".join(missing_parts))
            bridge = True
            if not missing_parts:
                audit.ok("3Y Return Bridge shows per-share growth, shareholder yield and multiple change")
            break
    if not bridge:
        audit.fail("Valuation Summary: missing '3Y Return Bridge'")


def _table(ws, title: str, columns: tuple[str, ...], audit: Audit) -> list[dict] | None:
    title_row = next((r for r in range(1, ws.max_row + 1)
                      if norm(ws.cell(r, 1).value).lower() == title.lower()), None)
    if title_row is None:
        audit.fail(f"{ws.title}: missing '{title}'")
        return None
    header = title_row + 1
    mapping = {norm(ws.cell(header, c).value).lower(): c for c in range(1, ws.max_column + 1)}
    missing = [c for c in columns if c.lower() not in mapping]
    if missing:
        audit.fail(f"{ws.title}: {title} missing columns: {', '.join(missing)}")
        return None
    rows = []
    for r in range(header + 1, ws.max_row + 1):
        if not norm(ws.cell(r, mapping[columns[0].lower()]).value):
            break
        record = {c: ws.cell(r, mapping[c.lower()]).value for c in columns}
        record['_row'] = r
        rows.append(record)
    if not rows:
        audit.fail(f"{ws.title}: {title} has no data rows")
    return rows


def audit_terminal_mapping(wb, data_wb, audit: Audit) -> None:
    if "Valuation Summary" not in wb.sheetnames:
        return  # Task 2 remains usable before Task 3 adds valuation tables.
    audit_band_bridge(wb, data_wb, audit)
    if "Terminal Cases" not in wb.sheetnames:
        audit.warn("Terminal reference unavailable: disclose the gap; central comps remain independently auditable")
        return
    columns = ("Case", "Metric", "Base Year", "Current Price", "Horizon", "Required Return", "Exit Multiple",
               "Terminal Total", "Terminal Shares", "Distributions FV", "Supported Price", "Implied Terminal Total", "Basis",
               "Terminal Cash", "Cash Treatment")
    rows = _table(wb['Terminal Cases'], 'Terminal Cases', columns, audit)
    if not rows:
        return
    horizons, years, prices = set(), set(), set()
    title_row = next(r for r in range(1, wb['Terminal Cases'].max_row + 1)
                     if norm(wb['Terminal Cases'].cell(r, 1).value).lower() == 'terminal cases')
    headers = {norm(wb['Terminal Cases'].cell(title_row + 1, c).value): c
               for c in range(1, wb['Terminal Cases'].max_column + 1)}
    for row in rows:
        name = norm(row['Case'])
        if any(not norm(row[c]) for c in columns if c not in {'Required Return', 'Distributions FV', 'Terminal Total', 'Terminal Cash'}):
            audit.fail(f"Terminal Cases: {name} has empty required values")
        values = {}
        unresolved_formula = False
        for field in columns[2:12] + ('Terminal Cash',):
            value = row[field]
            if isinstance(value, str) and value.startswith('='):
                value = data_wb['Terminal Cases'].cell(row['_row'], headers.get(field, 1)).value
                unresolved_formula = unresolved_formula or value is None
            values[field] = value
        if norm(row['Metric']) not in {'P/E', 'P/S', 'P/B', 'P/TBV', 'P/AFFO', 'P/NAV'}:
            audit.fail(f"Terminal Cases: {name} uses an unsupported equity metric")
            continue
        if any(not isinstance(v, (int, float)) or isinstance(v, bool) or not math.isfinite(v) for v in values.values()):
            if unresolved_formula:
                audit.warn(f"Terminal Cases: {name} needs recalculation before numeric mapping can be verified")
            else:
                audit.fail(f"Terminal Cases: {name} has invalid numeric inputs/results")
            continue
        years.add(values['Base Year']); horizons.add(values['Horizon']); prices.add(values['Current Price'])
        if int(values['Base Year']) != values['Base Year'] or not 2000 <= values['Base Year'] <= 2200:
            audit.fail(f"Terminal Cases: {name} has invalid Base Year")
        try:
            case = TerminalCase(norm(row['Metric']), values['Terminal Total'], values['Terminal Shares'],
                                values['Exit Multiple'], values['Horizon'], values['Required Return'], values['Distributions FV'],
                                values['Terminal Cash'], norm(row['Cash Treatment']))
            implied = case.implied_total(values['Current Price'])
        except ValueError as exc:
            audit.fail(f"Terminal Cases: {name}: {exc}")
            continue
        for field, expected in (('Supported Price', case.supported_price), ('Implied Terminal Total', implied)):
            if not math.isclose(values[field], expected, rel_tol=1e-6, abs_tol=1e-6):
                audit.fail(f"Terminal Cases: {name} {field} disagrees with horizon/share/distribution mapping")
    if len(years) > 1 or len(horizons) > 1:
        audit.fail("Terminal Cases: reference cases must share a base year and observation horizon")
    if len(prices) > 1:
        audit.fail("Terminal Cases: inconsistent current-price snapshots")


def audit_band_bridge(wb, data_wb, audit: Audit) -> None:
    bridge_columns = ('Case', 'Comps Low', 'Comps Mid', 'Comps High', 'Terminal Low', 'Terminal Mid',
                      'Terminal High', 'Central Low', 'Central Mid', 'Central High')
    bridges = _table(wb['Valuation Summary'], 'Band Valuation Bridge', bridge_columns, audit)
    table_ws = wb['Valuation Summary']
    title = next((r for r in range(1, table_ws.max_row + 1) if norm(table_ws.cell(r, 1).value).lower() == 'band valuation bridge'), None)
    if title is None:
        return
    headers = {norm(table_ws.cell(title + 1, col).value): col for col in range(1, table_ws.max_column + 1)}
    graph = formula_dependencies(wb)
    terminal_nodes = {(table_ws.title, table_ws.cell(row['_row'], headers[f'Terminal {suffix}']).coordinate)
                      for row in bridges or [] for suffix in ('Low', 'Mid', 'High')}
    for row in bridges or []:
        for suffix in ('Low', 'Mid', 'High'):
            fields = (f'Comps {suffix}', f'Central {suffix}')
            root = (table_ws.title, table_ws.cell(row['_row'], headers[fields[1]]).coordinate)
            pending, seen = [root], set()
            while pending:
                node = pending.pop()
                if node in seen:
                    continue
                seen.add(node)
                if node[0] in {'Terminal Cases', 'Implied Expectations'} or node in terminal_nodes:
                    audit.fail(f"Band Valuation Bridge: {row['Case']} {suffix} depends on a zero-weight terminal reference")
                    break
                pending.extend(graph.get(node, ()))
            values = [data_wb[table_ws.title].cell(row['_row'], headers[field]).value for field in fields]
            if all(isinstance(x, (int, float)) and not isinstance(x, bool) and math.isfinite(x) for x in values):
                a, result = values
                if a < 0 or not math.isclose(result, central_valuation(a), rel_tol=1e-6, abs_tol=1e-6):
                    audit.fail(f"Band Valuation Bridge: {row['Case']} {suffix} must equal100% forward comps")
            elif any(isinstance(row[field], str) and row[field].startswith('=') for field in fields) and any(x is None for x in values):
                audit.warn(f"Band Valuation Bridge: {row['Case']} {suffix} needs recalculation to verify100% comps")
            else:
                audit.fail(f"Band Valuation Bridge: {row['Case']} {suffix} has invalid or missing values")


def audit_condition_evidence(wb, audit: Audit) -> None:
    if 'Valuation Summary' not in wb.sheetnames:
        return
    ws = wb['Valuation Summary']
    conditions = _table(ws, 'Condition Evidence', ('Band', 'Condition', 'Threshold', 'Current Evidence',
                        'Evidence Date', 'Source / Locator', 'Status', 'Decisive', 'Next Signal'), audit)
    positions = _table(ws, 'Decision Position', ('Position', 'Band', 'Confidence', 'Rationale'), audit)
    if conditions is None or positions is None:
        return
    by_band: dict[str, list[dict]] = defaultdict(list)
    for row in conditions:
        label = norm(row['Band']).lower()
        by_band[label].append(row)
        if any(not norm(row[c]) for c in row if c != '_row'):
            audit.fail(f"Condition Evidence!{row['_row']}: incomplete condition evidence")
        if norm(row['Status']).lower() not in {'supported', 'partial', 'unverified', 'contradicted'}:
            audit.fail(f"Condition Evidence!{row['_row']}: invalid evidence Status")
        if norm(row['Decisive']).lower() not in {'yes', 'no'}:
            audit.fail(f"Condition Evidence!{row['_row']}: Decisive must be Yes/No")
        if not re.fullmatch(r'20\d{2}-\d{2}-\d{2}', norm(row['Evidence Date'])):
            audit.fail(f"Condition Evidence!{row['_row']}: Evidence Date must be YYYY-MM-DD")
    positions_by_name = {norm(r['Position']).lower(): r for r in positions}
    for key in ('market-priced band', 'evidence-supported band'):
        row = positions_by_name.get(key)
        if not row or any(not norm(row[c]) for c in ('Band', 'Confidence', 'Rationale')):
            audit.fail(f"Decision Position: missing or incomplete {key}")
        elif norm(row['Confidence']).lower() not in {'high', 'medium', 'low'}:
            audit.fail(f"Decision Position: {key} Confidence must be High/Medium/Low")
    supported = positions_by_name.get('evidence-supported band')
    if supported:
        label = norm(supported['Band']).lower()
        if label not in {'mixed', 'unresolved'}:
            if label not in by_band:
                audit.fail('Decision Position: evidence-supported band lacks Condition Evidence')
            for row in by_band.get(label, []):
                if norm(row['Decisive']).lower() == 'yes' and norm(row['Status']).lower() == 'contradicted':
                    audit.fail('Decision Position: evidence-supported band has a contradicted decisive condition')
                if (norm(row['Decisive']).lower() == 'yes' and norm(row['Status']).lower() == 'unverified'
                        and norm(supported['Confidence']).lower() == 'high'):
                    audit.fail('Decision Position: High confidence conflicts with unverified decisive evidence')
    band_rows = _table(ws, 'Price Band Map', ('Band', 'Evidence Status', 'Evidence Ref'), audit)
    for row in band_rows or []:
        if norm(row['Band']).lower() not in by_band:
            audit.fail(f"Price Band Map: {row['Band']} lacks Condition Evidence")


def audit_scenario_drivers(wb, audit: Audit) -> None:
    if 'Scenarios' not in wb.sheetnames:
        audit.fail('Missing Scenarios: select at most 5 key economic drivers')
        return
    ws = wb['Scenarios']
    selector = [(ws.cell(r, c), ws.cell(r, c + 1)) for r in range(1, ws.max_row + 1)
                for c in range(1, ws.max_column) if norm(ws.cell(r, c).value).lower() == 'case selector']
    if len(selector) != 1 or selector[0][1].value not in {1, 2, 3}:
        audit.fail('Scenarios: exactly one Case Selector with 1=Bear, 2=Base, 3=Bull is required')
    drivers = _table(ws, 'Scenario Drivers', ('Driver ID', 'Driver', 'Reason', 'Active Ref',
                     'Bear Ref', 'Base Ref', 'Bull Ref', 'Output Ref'), audit)
    if not drivers:
        return
    if not 1 <= len(drivers) <= 5:
        audit.fail(f'Scenarios: Scenario Drivers must contain 1–5 key drivers, found {len(drivers)}')
    ids = [norm(row['Driver ID']).lower() for row in drivers]
    if len(set(ids)) != len(ids):
        audit.fail('Scenarios: duplicate Driver ID; register one economic driver only once')

    def resolve(value):
        ref = norm(value).lstrip('=')
        if '!' not in ref:
            raise ValueError('reference must identify a sheet and cell/range')
        sheet, address = ref.rsplit('!', 1)
        sheet = sheet.strip("'").replace("''", "'")
        if sheet not in wb.sheetnames:
            raise ValueError(f'unknown reference sheet {sheet}')
        left, top, right, bottom = range_boundaries(address)
        if (right-left+1)*(bottom-top+1) > 100:
            raise ValueError('use a bounded forecast input range, not a whole column')
        return wb[sheet], [wb[sheet].cell(r,c) for r in range(top,bottom+1) for c in range(left,right+1)]

    def compact(text):
        return norm(text).replace('$', '').replace("'", '').replace(' ', '').upper()

    registered_active = set()
    for row in drivers:
        name = norm(row['Driver'])
        if any(not norm(row[c]) for c in row if c != '_row'):
            audit.fail(f'Scenarios: {name} has incomplete driver registration')
            continue
        try:
            refs = {key: resolve(row[key]) for key in ('Active Ref','Bear Ref','Base Ref','Bull Ref','Output Ref')}
        except (ValueError, TypeError) as exc:
            audit.fail(f'Scenarios: {name} invalid driver reference: {exc}')
            continue
        active_sheet, active_cells = refs['Active Ref']
        for cell in active_cells:
            key = (active_sheet.title, cell.coordinate)
            if key in registered_active:
                audit.fail('Scenarios: one Active input cannot be registered as multiple economic drivers')
            registered_active.add(key)
        cases = [refs[key][1] for key in ('Bear Ref','Base Ref','Bull Ref')]
        if any(cell.value is None for cells in cases for cell in cells):
            audit.fail(f'Scenarios: {name} has missing case inputs')
        if any(len(cells) != len(active_cells) for cells in cases):
            audit.fail(f'Scenarios: {name} Active and case ranges must align')
            continue
        for index, active in enumerate(active_cells):
            formula = compact(active.value)
            if not formula.startswith('=') or not any(token in formula for token in ('CHOOSE(', 'INDEX(', 'IF(', 'OFFSET(', 'XLOOKUP(')):
                audit.fail(f'Scenarios: {name} Active input must select assumptions, not a finished output')
                continue
            if len(selector) == 1:
                control = selector[0][1].coordinate
                if compact(control) not in formula:
                    audit.fail(f'Scenarios: {name} Active input does not reference the Case Selector')
            if 'CHOOSE(' in formula:
                for case in cases:
                    if compact(case[index].coordinate) not in formula:
                        audit.fail(f'Scenarios: {name} Active input omits a registered case input')
        output_sheet, output_cells = refs['Output Ref']
        for index, target in enumerate(output_cells):
            active = active_cells[min(index, len(active_cells)-1)]
            expected = compact(f'{active_sheet.title}!{active.coordinate}')
            formula = compact(target.value)
            if not formula.startswith('=') or expected not in formula:
                audit.fail(f'Scenarios: {name} Output Ref must consume its Active input')
    if len(selector) == 1:
        control = compact(selector[0][1].coordinate)
        for sheet in wb:
            for cells in sheet:
                for cell in cells:
                    formula = compact(cell.value)
                    if not formula.startswith('=') or '"' in formula:
                        continue  # Text-only case labels are display, not input drivers.
                    reference = control if sheet.title == 'Scenarios' else f'SCENARIOS!{control}'
                    selects = any(t in formula for t in ('CHOOSE(', 'INDEX(', 'IF(', 'OFFSET(', 'XLOOKUP('))
                    if selects and re.search(re.escape(reference) + r'(?!\d)', formula) and (sheet.title,cell.coordinate) not in registered_active:
                        audit.fail(f'{sheet.title}!{cell.coordinate}: unregistered scenario-selecting input; non-key assumptions must share the base path')
    if not audit.failures:
        audit.ok(f'Scenarios: {len(drivers)} registered key driver(s), one selector and linked build inputs')


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--excel", required=True, type=Path)
    parser.add_argument("--report", type=Path)
    parser.add_argument("--prev", type=Path)
    args = parser.parse_args()
    audit = Audit()
    if not args.excel.exists():
        audit.fail(f"Excel file not found: {args.excel}")
        return audit.print()
    try:
        wb = openpyxl.load_workbook(args.excel, data_only=False)
        data_wb = openpyxl.load_workbook(args.excel, data_only=True)
    except Exception as exc:
        audit.fail(f"Cannot open Excel workbook: {exc}")
        return audit.print()
    report_text = None
    if args.report:
        if not args.report.exists():
            audit.fail(f"Report file not found: {args.report}")
        else:
            try:
                report_text = extract_docx_text(args.report)
            except Exception as exc:
                audit.fail(f"Cannot open report DOCX: {exc}")
    if args.prev:
        if not args.prev.exists():
            audit.fail(f"Previous report not found: {args.prev}")
        else:
            audit.warn("--prev supplied: depth_audit.py remains authoritative for chapter regression; this audit checks current model/report methods")

    audit_governance(wb, audit)
    audit_hardcodes_fonts_formats(wb, audit)
    audit_scenario_drivers(wb, audit)
    audit_errors_cycles_balances(wb, data_wb, audit)
    audit_valuation(wb, audit, report_text)
    audit_price_bands(wb, audit, data_wb)
    audit_terminal_mapping(wb, data_wb, audit)
    audit_condition_evidence(wb, audit)
    audit_financial_policies(wb, data_wb, audit)
    audit_forward_periods(wb, audit)
    return audit.print()


if __name__ == "__main__":
    sys.exit(main())
