#!/usr/bin/env python3
from __future__ import annotations

import tempfile
from pathlib import Path

import depth_audit


def main() -> int:
    with tempfile.TemporaryDirectory() as td:
        path = Path(td) / "research.md"
        path.write_text(
            "<!-- DEPTH_EXCLUDE_START: RESEARCH_BACKSTAGE -->\n"
            "## 渠道覆盖矩阵\n" + ("后台日志" * 1000) + "\n"
            "## 研究对象覆盖矩阵\n" + ("对象记录" * 1000) + "\n"
            "<!-- DEPTH_EXCLUDE_END: RESEARCH_BACKSTAGE -->\n"
            "## 2. 行业纵向叙事\n"
            "正文分析 2026 年收入增长 20%。\n",
            encoding="utf-8",
        )
        chapters, _, _ = depth_audit.split_sections(depth_audit.parse_md(path))
        assert "渠道覆盖矩阵" in chapters[0]["text"]
        assert chapters[2]["chars"] < 100, chapters[2]["chars"]
        assert "后台日志" not in chapters[2]["text"]
    print("DEPTH EXCLUSION TEST: PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
