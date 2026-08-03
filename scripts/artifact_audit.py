#!/usr/bin/env python3
"""Audit IC model provenance, formatting and valuation consistency."""

from __future__ import annotations

import argparse
import re
import sys
from collections import defaultdict
from pathlib import Path
from typing import Iterable

import openpyxl
from openpyxl.utils import get_column_letter, range_boundaries
from openpyxl.worksheet.worksheet import Worksheet


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
    if "yoy" in low or "year-over-year" in low or ("growth" in low and "revenue" not in low):
        return "yoy"
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
    for index in revenue_starts:
        sequence = [kind for _, kind in ordered[index : index + 4]]
        if sequence != ["revenue", "yoy", "quantity", "price"]:
            row = ordered[index][0]
            audit.fail(
                f"Revenue Model!{get_column_letter(metric_col)}{row}: revenue stream order must be "
                "Revenue -> YoY growth -> Quantity -> Price / yield"
            )
    if revenue_starts and all(
        [kind for _, kind in ordered[index : index + 4]] == ["revenue", "yoy", "quantity", "price"]
        for index in revenue_starts
    ):
        audit.ok(f"Revenue Model contains {len(revenue_starts)} correctly ordered revenue-stream block(s)")


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
            "value_cells": [ws.cell(row, col) for col in (low_col, mid_col, high_col, source_formula_col if exact else None) if col],
        })
    return methods, exact


def audit_valuation(wb, audit: Audit, report_text: str | None) -> None:
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


def audit_forward_periods(wb, audit: Audit) -> None:
    if "Valuation Summary" not in wb.sheetnames:
        return
    ws = wb["Valuation Summary"]
    metric_years: dict[str, set[str]] = {"p/e": set(), "p/s": set()}
    for row in range(1, ws.max_row + 1):
        row_text = " | ".join(norm(ws.cell(row, col).value) for col in range(1, ws.max_column + 1))
        low = row_text.lower()
        for metric, patterns in {
            "p/e": ("forward p/e", "forward pe"),
            "p/s": ("forward p/s", "forward ps"),
        }.items():
            if any(pattern in low for pattern in patterns):
                metric_years[metric].update(re.findall(r"\b(20\d{2})E?\b", row_text, re.I))
    if not metric_years["p/e"] or not metric_years["p/s"]:
        audit.fail("Valuation Summary: Forward P/E and Forward P/S must each show an explicit forecast year")
        return
    if len(metric_years["p/e"]) != 1 or len(metric_years["p/s"]) != 1:
        audit.fail("Valuation Summary: each forward multiple must use one unambiguous forecast year")
        return
    pe_year = next(iter(metric_years["p/e"]))
    ps_year = next(iter(metric_years["p/s"]))
    if pe_year != ps_year:
        audit.fail(f"Valuation Summary: Forward P/E uses {pe_year} but Forward P/S uses {ps_year}")
    else:
        audit.ok(f"Forward P/E and Forward P/S use the same explicit forecast year ({pe_year}E)")


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
    audit_errors_cycles_balances(wb, data_wb, audit)
    audit_valuation(wb, audit, report_text)
    audit_financial_policies(wb, data_wb, audit)
    audit_forward_periods(wb, audit)
    return audit.print()


if __name__ == "__main__":
    sys.exit(main())
