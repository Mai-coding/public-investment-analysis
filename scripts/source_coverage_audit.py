#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Task 1 渠道与研究对象覆盖闸门。仅使用 Python 标准库。"""

import argparse
import json
import os
import re
import sys


for _stream in (sys.stdout, sys.stderr):
    try:
        _stream.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass


TERMINAL = {"hit", "no_hit", "not_applicable", "blocked"}
ENTITY_TYPES = {"target", "competitor", "upstream", "downstream"}

def default_registry():
    return os.path.abspath(
        os.path.join(os.path.dirname(__file__), "..", "references", "source_registry.json")
    )


def cells(line):
    return [c.strip() for c in line.strip().strip("|").split("|")]


def parse_tables(text, channel_ids):
    channels = {}
    entities = []
    for raw in text.splitlines():
        if raw.count("|") < 2:
            continue
        row = cells(raw)
        if not row or set("".join(row).replace(":", "").replace("-", "")) == set():
            continue
        if row[0] in channel_ids and len(row) >= 6:
            channels[row[0]] = {
                "status": row[1].lower(),
                "searched_at": row[2],
                "query_scope": row[3],
                "evidence": row[4],
                "note": row[5],
            }
        if row[0].lower() in ENTITY_TYPES and len(row) >= 7 and row[1].strip():
            try:
                entities.append(
                    {
                        "type": row[0].lower(),
                        "name": row[1],
                        "annual": int(row[2]),
                        "quarterly": int(row[3]),
                        "transcripts": int(row[4]),
                        "market": row[5],
                        "evidence": row[6],
                    }
                )
            except ValueError:
                pass
    return channels, entities


def has_evidence(value):
    return bool(
        re.search(
            r"https?://|www\.|BV[0-9A-Za-z]{8,}|@[0-9]{1,2}:[0-9]{2}|\b20[0-9]{2}[./-][0-9]{1,2}[./-][0-9]{1,2}\b|\.(?:pdf|htm|html|md|txt)\b",
            value,
            re.I,
        )
    )


def audit(registry, channels, entities):
    fails = []
    warns = []
    for item in registry["channels"]:
        cid = item["id"]
        row = channels.get(cid)
        if not row:
            fails.append(f"渠道缺失：{cid} ({item['name']})")
            continue
        status = row["status"]
        if status not in TERMINAL:
            fails.append(f"渠道未结束：{cid} status={status or '空'}")
            continue
        if item["mode"] in {"always", "always_scan"} and status == "not_applicable":
            fails.append(f"强制渠道不可标 not_applicable：{cid}")
        if status in {"hit", "no_hit"}:
            if not row["searched_at"]:
                fails.append(f"渠道缺扫描日期：{cid}")
            if not row["query_scope"]:
                fails.append(f"渠道缺搜索词/扫描范围：{cid}")
        if status == "hit" and not has_evidence(row["evidence"]):
            fails.append(f"命中渠道缺可定位证据：{cid}")
        if status == "blocked" and not row["note"]:
            fails.append(f"阻塞渠道缺原因/兜底说明：{cid}")
        if status == "not_applicable" and not row["note"]:
            fails.append(f"不适用渠道缺原因：{cid}")

    grouped = {k: [e for e in entities if e["type"] == k] for k in ENTITY_TYPES}
    expected_counts = {"target": (1, 1), "competitor": (4, 5), "upstream": (1, 2), "downstream": (1, 2)}
    minimums = {
        "target": (3, 2, 5),
        "competitor": (1, 2, 2),
        "upstream": (1, 1, 1),
        "downstream": (1, 1, 1),
    }
    for kind, (lo, hi) in expected_counts.items():
        count = len(grouped[kind])
        if not lo <= count <= hi:
            fails.append(f"研究对象数量错误：{kind}={count}，要求 {lo}-{hi}")
        need_a, need_q, need_t = minimums[kind]
        for entity in grouped[kind]:
            if entity["annual"] < need_a or entity["quarterly"] < need_q or entity["transcripts"] < need_t:
                fails.append(
                    f"资料范围不足：{kind}/{entity['name']} "
                    f"年报{entity['annual']} 季报{entity['quarterly']} transcript{entity['transcripts']}；"
                    f"最低 {need_a}/{need_q}/{need_t}"
                )
            if not entity["evidence"]:
                fails.append(f"研究对象缺文件/链接证据：{kind}/{entity['name']}")

    markets = {e["market"].upper() for e in entities}
    market_channels = {
        "US": "filing.sec",
        "CN": "filing.cninfo",
        "HK": "filing.hkex",
        "EU": "filing.esma",
    }
    for market, cid in market_channels.items():
        if market in markets and channels.get(cid, {}).get("status") in {None, "not_applicable", "pending"}:
            fails.append(f"存在 {market} 公司，但监管渠道未实际搜索：{cid}")

    return fails, warns


def print_template(registry):
    print("<!-- DEPTH_EXCLUDE_START: RESEARCH_BACKSTAGE -->")
    print("## 渠道覆盖矩阵")
    print("| channel_id | status | searched_at | query_scope | evidence | note |")
    print("|---|---|---|---|---|---|")
    for item in registry["channels"]:
        print(f"| {item['id']} | pending | | | | {item['name']} · {item['mode']} |")
    print("\n## 研究对象覆盖矩阵")
    print("| entity_type | entity | annual_reports | quarterly_reports | transcripts | market | evidence |")
    print("|---|---|---:|---:|---:|---|---|")
    print("| target | | 0 | 0 | 0 | | |")
    for _ in range(5):
        print("| competitor | | 0 | 0 | 0 | | |")
    for _ in range(2):
        print("| upstream | | 0 | 0 | 0 | | |")
    for _ in range(2):
        print("| downstream | | 0 | 0 | 0 | | |")
    print("\n## 数据搜集附录（后台，不计入 §2–9 字数）")
    print("<!-- 将渠道日志、文件清单和覆盖说明追加在此行之后、END marker 之前 -->")
    print("<!-- DEPTH_EXCLUDE_END: RESEARCH_BACKSTAGE -->")


def self_test(registry):
    channels = {}
    for item in registry["channels"]:
        active = item["mode"] == "always"
        channels[item["id"]] = {
            "status": "hit" if active else "not_applicable",
            "searched_at": "2026-07-22" if active else "",
            "query_scope": "test query" if active else "",
            "evidence": "https://example.com/evidence" if active else "",
            "note": "self-test" if not active else "",
        }
    entities = [
        {"type": "target", "name": "T", "annual": 3, "quarterly": 2, "transcripts": 5, "market": "US", "evidence": "t"},
        *[
            {"type": "competitor", "name": f"C{i}", "annual": 1, "quarterly": 2, "transcripts": 2, "market": "US", "evidence": "c"}
            for i in range(4)
        ],
        {"type": "upstream", "name": "U", "annual": 1, "quarterly": 1, "transcripts": 1, "market": "US", "evidence": "u"},
        {"type": "downstream", "name": "D", "annual": 1, "quarterly": 1, "transcripts": 1, "market": "US", "evidence": "d"},
    ]
    channels["filing.sec"] = {
        "status": "hit", "searched_at": "2026-07-22", "query_scope": "CIK",
        "evidence": "https://sec.gov/", "note": ""
    }
    fails, _ = audit(registry, channels, entities)
    if fails:
        print("SELF TEST FAIL: valid fixture rejected")
        for failure in fails:
            print(f"  {failure}")
        return 1
    channels.pop("priority.a16z")
    fails, _ = audit(registry, channels, entities)
    if not any("priority.a16z" in failure for failure in fails):
        print("SELF TEST FAIL: missing channel was not detected")
        return 1
    print("SELF TEST PASS")
    return 0


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--in", dest="input_path", help="Task 1 研究文档 Markdown")
    parser.add_argument("--registry", default=default_registry())
    parser.add_argument("--template", action="store_true", help="打印两张强制台账模板")
    parser.add_argument("--self-test", action="store_true")
    args = parser.parse_args()

    with open(args.registry, encoding="utf-8") as f:
        registry = json.load(f)
    if args.template:
        print_template(registry)
        return 0
    if args.self_test:
        return self_test(registry)
    if not args.input_path:
        parser.error("除 --template 外必须提供 --in")
    with open(args.input_path, encoding="utf-8") as f:
        text = f.read()
    channel_ids = {item["id"] for item in registry["channels"]}
    channels, entities = parse_tables(text, channel_ids)
    fails, warns = audit(registry, channels, entities)
    print(f"渠道覆盖：{len(channels)}/{len(channel_ids)}；研究对象：{len(entities)}")
    for warning in warns:
        print(f"WARN  {warning}")
    if fails:
        for failure in fails:
            print(f"FAIL  {failure}")
        print(f"SOURCE COVERAGE AUDIT: FAIL ({len(fails)})")
        return 1
    print("SOURCE COVERAGE AUDIT: PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
