#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
depth_audit.py — public-investment-analysis 深度闸门（硬测量，非软自检）

这是 skill 的"防骨架/防灌水"测量闸门。它替代过去散落在 03/10/11 三处的章节
完整性 grep 脚本与 §A 深度自检——那些是 checklist 勾选项，会被一趟跑直接打 ✅。
本脚本必须被【真正运行】，并把输出贴给用户；FAIL 即阻断：

  • 闸门 1（Task 1 末）：研究文档未 PASS  →  不得进入 Task 2/3/4/5
  • 闸门 2（Task 5 交付前）：DOCX 未 PASS  →  不得交付，回炉补足再重跑

三层检查（对应"字数下限 + 结构 + 抽样人工审"）：
  1) 字数下限：每章/附录硬下限（FLOORS）——粗筛防骨架（ASE v1 骨架会重挂）。
  2) 结构：子节完整性 + 关键章必含表 + 量化密度（定性词挂数字）+ §7 竞品块、
     附录块、§9 逐人画像、问句标题=0 + §16『重点研究问题』直答块在场。（CEMRI 因果/反方 marker 检查已移除——
     用户要求全文不套 CEMRI；深度实质靠字数下限+必含表+量化密度+抽样人工审兜底。）
  3) 抽样人工审：脚本点名 3-4 个关键章，打印深度核查清单（自然散文不贴标签；
     机器只能查"在场"，质量好坏靠人工抽样判断）。

用法：
  python depth_audit.py --stage research --in <Research_Document.md> [--dir <研究文件夹>]
  python depth_audit.py --stage final    --in <IC_Report.docx> [--prev <上一版.docx>]

退出码：PASS=0，FAIL=1。
依赖：仅标准库（zipfile + xml.etree + re）。无需 python-docx。
"""

import argparse
import os
import random
import re
import sys
import zipfile
import xml.etree.ElementTree as ET
from section_roles import resolve_intro_roles
from docx_structure import Structure, chapter_number

# Windows 控制台默认 GBK，强制 UTF-8 以输出 ✅/❌/中文
for _s in (sys.stdout, sys.stderr):
    try:
        _s.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass

W_NS = "http://schemas.openxmlformats.org/wordprocessingml/2006/main"

# ── 每章字数下限（中文字符，floor 非 target；低于即回炉）──────────────────
# Round 2 校准（用户要求 §2-9 研究文档 target ~20k）：§2-9 floor 合计约 19.5k（§8/§9 加深），
# 写作 target 20k（留 ~10% 余量不误杀好稿）。新标准高于 Cloudflare §2-9（17.5k）——
# 这是用户主动抬高的 bar，CF 在叙事/市场章会略低于线，属预期、非 gate 回归。
# research-stage 在 .md 上计数（含 markdown 标记）；final-stage 在 .docx 上计数（标记已剥离），
# 同一内容 docx 比 md 少 ~3-5%，故 final §2-9 floor = research ×0.95（否则忠实装配的 docx 会假性 FAIL）。
RESEARCH_FLOORS = {2: 2400, 3: 3000, 4: 2200, 5: 2400, 6: 1700, 7: 3200, 8: 2200, 9: 2400}
FINAL_FLOORS = {
    1: 700, 2: 2280, 3: 2850, 4: 2090, 5: 2280, 6: 1615, 7: 3040, 8: 2090,
    9: 2280, 10: 1000, 11: 1000, 12: 800, 13: 650, 14: 500, 15: 600, 16: 950,
}
APPENDIX_FLOOR = 500   # 目标 800-1,200；硬下限 500（连 gold-standard 也仅~600）

# 必含 ≥1 张表的章。§6 用漏斗图；§7.1 由纯文字解读 + 竞争矩阵图承担，
# 不再强制表格，避免正文矩阵与 chart 4 重复。图表在场由 report_content_audit.py 检查。
TABLE_REQUIRED_FINAL = {3, 5, 8, 9, 11, 12}
TABLE_REQUIRED_RESEARCH = {3, 5, 8, 9}

# 必含子节（canonical 清单 = 03_section_structure；本脚本是完整性的唯一权威）
REQUIRED_SUBS = {
    4: ["4.1", "4.2", "4.3", "4.4", "4.5"],
    5: ["5.1", "5.2", "5.3"], 6: ["6.1", "6.2", "6.3"],
    7: ["7.1", "7.2", "7.4"], 8: ["8.1", "8.5", "8.6", "8.7"],
    9: ["9.1", "9.2", "9.3"],
    11: ["11.1", "11.3"], 12: ["12.1", "12.5"], 13: ["13.1"],
    15: ["15.1"], 16: ["16.1", "16.3", "16.4"],
}

CHAPTER_TITLES = {
    1: "投资概要", 2: "核心技术入门", 3: "行业纵向叙事", 4: "产品分析",
    5: "技术分析", 6: "市场分析", 7: "竞争横向叙事", 8: "商业模式",
    9: "团队", 10: "财务分析", 11: "估值与可比", 12: "Price Band 与情景",
    13: "Killer Risk", 14: "Why Now/This/Us", 15: "投资判断", 16: "尽调与跟踪",
}

# 量化密度（数字 token，用于"定性词挂数字"软检）；CEMRI 因果/反方 marker 已废弃
RE_NUMTOKEN = re.compile(r"\d[\d\.,]*%?")
RE_LABEL = re.compile(r"Fact|Inference|Assumption|事实|推断|管理层口径|来源")
RE_Q_TITLE = re.compile(r"^(Q\d[：:]|.*[？?]\s*$)")


def nlen(s):
    """非空白字符数。"""
    return len(re.sub(r"\s", "", s))


# ── DOCX 解析（按 body 文档顺序遍历 w:p / w:tbl）─────────────────────────
def parse_docx(path):
    items = []
    for block in Structure(path).blocks:
        if block.navigation:
            continue
        el = block.element
        txt = "".join(t.text or "" for t in el.iter(f"{{{W_NS}}}t"))
        kind = "tbl" if el.tag.endswith("}tbl") else "heading" if block.heading_level is not None else "body"
        items.append((kind, txt))
    return items


def parse_md(path):
    """Research Markdown -> items; backstage blocks are preserved as meta but excluded from depth counts."""
    items = []
    excluded = False
    with open(path, encoding="utf-8") as f:
        lines = f.read().splitlines()
    for ln in lines:
        s = ln.strip()
        if "DEPTH_EXCLUDE_START" in s:
            excluded = True
            continue
        if "DEPTH_EXCLUDE_END" in s:
            excluded = False
            continue
        if not s:
            continue
        if excluded:
            items.append(("meta", re.sub(r"^#{1,6}\s*", "", s)))
            continue
        body = s.replace("|", "").replace(":", "").replace(" ", "")
        if s.count("|") >= 2 and body and set(body) <= {"-"}:
            items.append(("tbl", ""))
            continue
        items.append(("p", re.sub(r"^#{1,6}\s*", "", s)))
    return items


# ── 章节切分 ───────────────────────────────────────────────────────────
RE_CH_PARA = re.compile(r"^§\s*(\d{1,2})\b")                 # "§7 ..."
RE_CH_DOT = re.compile(r"^(\d{1,2})\.\s+\S")                  # "7. ..."（需句点）
RE_SOURCE_APPX = re.compile(r"^(?:附录|Appendix)\s*(?:[｜|:：—\-]\s*)?(?:Sources?\b|来源索引|参考来源|Source Index\b|Methods?\b|定义与方法|方法与定义|方法说明)", re.I)
RE_APPX = re.compile(r"^(?:附录|Appendix)\s*([A-E])\b", re.I)
RE_SUB = re.compile(r"\b(\d{1,2})\.(\d{1,2})\b")


def split_sections(items):
    """
    返回:
      chapters[n] = {"chars":int, "tables":int, "text":str, "qtitles":int}
      appendices[A] = {"chars":int, "tables":int}
      subs = set("2.1", ...)
    """
    chapters = {}
    appendices = {}
    subs = set()
    cur = None          # ("ch", n) | ("ap", letter) | None
    cur_ch = 0          # 单调递增守卫

    def bucket():
        if cur and cur[0] == "ch":
            return chapters.setdefault(cur[1], {"chars": 0, "tables": 0, "text": "", "qtitles": 0})
        if cur and cur[0] == "ap":
            return appendices.setdefault(cur[1], {"chars": 0, "tables": 0, "text": ""})
        return None

    for kind, txt in items:
        s = txt.strip()
        if kind == "meta":
            meta = chapters.setdefault(0, {"chars": 0, "tables": 0, "text": "", "qtitles": 0})
            meta["text"] += "\n" + s
            continue
        if kind in {"p", "heading", "body"} and s:
            for m in RE_SUB.finditer(s):
                subs.add(f"{int(m.group(1))}.{int(m.group(2))}")
            is_head = False
            # 静态目录(TOC)条目形如 "2. 行业纵向叙事… 5" / "附录 C… 43"，末尾带页码——
            # 会污染章节切分，必须排除（正文标题绝不以孤立页码结尾）。
            toc_like = bool(re.search(r"\s\d{1,3}\s*$", s))
            if kind != "body" and len(s) < 100 and (kind == "heading" or not toc_like):
                n = chapter_number(s)
                if n is not None:
                    if 1 <= n <= 16 and n > cur_ch:   # 单调递增，防误判
                        cur = ("ch", n); cur_ch = n; is_head = True
                        chapters.setdefault(n, {"chars": 0, "tables": 0, "text": "", "qtitles": 0})["title"] = s
                if not is_head and RE_SOURCE_APPX.match(s):
                    # Unlettered source/methods appendix is deliberately excluded from body and comp-appendix floors.
                    cur = None; is_head = True
                if not is_head:
                    a = RE_APPX.match(s)
                    if a:
                        cur = ("ap", a.group(1).upper()); is_head = True
                        appendices.setdefault(a.group(1).upper(), {"chars": 0, "tables": 0, "text": ""})
            b = bucket()
            if b is not None:
                if is_head and RE_Q_TITLE.match(s) and "qtitles" in b:
                    b["qtitles"] += 1
                b["chars"] += nlen(s)
                b["text"] += "\n" + s
        elif kind == "tbl":
            b = bucket()
            if b is not None:
                b["tables"] += 1
                b["chars"] += nlen(txt)
                b["text"] = b.get("text", "") + "\n" + txt
    return chapters, appendices, subs


# ── 检查 ───────────────────────────────────────────────────────────────
def audit(chapters, appendices, subs, stage, research_dir=None, prev_total=None):
    fails, warns, lines = [], [], []
    floors = dict(RESEARCH_FLOORS if stage == "research" else FINAL_FLOORS)
    table_req = set(TABLE_REQUIRED_RESEARCH if stage == "research" else TABLE_REQUIRED_FINAL)
    roles, role_errors = resolve_intro_roles({n: c.get("title", "") for n, c in chapters.items() if n})
    fails.extend(role_errors)
    required_subs = dict(REQUIRED_SUBS)
    for role, minimum in (("technical", 2400 if stage == "research" else 2280),
                          ("history", 3000 if stage == "research" else 2850)):
        if role in roles:
            n = roles[role]
            floors[n] = minimum
            required_subs[n] = [f"{n}.{x}" for x in ([0] if role == "technical" else [1, 2, 3])]
    if "history" in roles:
        table_req.discard(2); table_req.discard(3); table_req.add(roles["history"])

    lines.append(f"{'章节':<26}{'字数':>7}{'下限':>7}{'表':>4}  判定")
    lines.append("-" * 60)
    total = 0
    for n in sorted(floors):
        c = chapters.get(n, {"chars": 0, "tables": 0, "text": "", "qtitles": 0})
        total += c["chars"]
        flags = []
        ok = True
        if c["chars"] < floors[n]:
            ok = False; flags.append(f"字数{c['chars']}<{floors[n]}")
        if n in table_req and c["tables"] < 1:
            ok = False; flags.append("缺表")
        if c.get("qtitles", 0) > 0:
            ok = False; flags.append(f"问句标题×{c['qtitles']}")
        # 子节完整性（软警告——好报告会合并/重编号子节，不硬失败；但字数下限会兜住真漏写）
        if n in required_subs:
            miss = [x for x in required_subs[n] if x not in subs]
            if miss:
                warns.append(f"§{n} 缺子节 {','.join(miss)}（确认是合并重编号还是真漏写）")
        # 量化密度软检（"定性词挂数字"是保留的深度实质；CEMRI 因果/反方标记检查已移除）
        # Introductory chapters are judged for readability;
        # numeric density is not a proxy for explanatory depth there.
        if c["chars"] >= 300 and n not in {2, 3}:
            ntok = len(RE_NUMTOKEN.findall(c["text"]))
            if ntok < c["chars"] / 150:   # 约每 150 字应有 ≥1 个数字，否则疑似空泛
                warns.append(f"§{n} 量化密度偏低（{ntok} 个数字 / {c['chars']} 字，定性词后应挂数字）")
        tag = "✅" if ok else "❌ " + " | ".join(flags)
        title = chapters.get(n, {}).get("title") or f"§{n} {CHAPTER_TITLES.get(n,'')}"
        lines.append(f"{title:<26}{c['chars']:>7}{floors[n]:>7}{c['tables']:>4}  {tag}")
        if not ok:
            fails.append(f"§{n} " + " | ".join(flags))

    # §7 竞品块深度（结构信号：威胁/瓶颈标记数）
    if 7 in chapters:
        t7 = chapters[7]["text"]
        sig = len(re.findall(r"威胁|瓶颈|赌注|生态位", t7))
        if sig < 4:
            warns.append(f"§7 竞品 narrative 信号弱（威胁/瓶颈/赌注/生态位 仅 {sig} 处，疑似每家未到 5 段）")

    # 可比公司附录（仅 final）：固定 4-5 篇，标签从 A 连续开始。
    if stage == "final":
        lines.append("-" * 60)
        present = [a for a in ["A", "B", "C", "D", "E"] if a in appendices]
        expected = ["A", "B", "C", "D"] if len(present) == 4 else ["A", "B", "C", "D", "E"]
        if len(present) not in {4, 5} or present != expected:
            fails.append(f"可比公司附录须为连续 A-D 或 A-E；当前 {','.join(present) or '无'}")
        for a in expected:
            c = appendices.get(a)
            if c is None:
                fails.append(f"附录 {a} 缺失"); lines.append(f"附录 {a:<22}{'缺失':>7}"); continue
            ok = c["chars"] >= APPENDIX_FLOOR
            tag = "✅" if ok else f"❌ 字数{c['chars']}<{APPENDIX_FLOOR}"
            lines.append(f"附录 {a:<22}{c['chars']:>7}{APPENDIX_FLOOR:>7}{c['tables']:>4}  {tag}")
            if not ok:
                fails.append(f"附录 {a} 字数{c['chars']}<{APPENDIX_FLOOR}")

    # §16 重点研究问题直答块（仅 final）：用户 Step 0 的「重点研究问题」必须在 §16 逐条直答并置最前；
    # 若用户未提任何重点问题，也必须在 §16 显式写一句"无重点研究问题，按标准全覆盖"。
    # 两种写法都含"重点研究问题"五字 → 只需查该 marker 是否在 §16 在场（脚本读不到用户原问题，
    # 逐条直答的"质量"靠抽样人工审；这里只防"静默漏掉"）。
    if stage == "final":
        t16 = chapters.get(16, {}).get("text", "")
        if "重点研究问题" not in t16:
            fails.append("§16 缺『重点研究问题』直答块（有则逐条直答并置最前；"
                         "若用户未提，显式写一句『无重点研究问题，按标准全覆盖』）")
        else:
            lines.append("§16 『重点研究问题』块 ✅ 在场（逐条直答质量请在抽样审中人工核）")

        # §16.4 未来 6 个月决策路线图：四块须齐全（买入/催化/减持/清仓 四关键词在场）
        rm_missing = [kw for kw in ("买入", "催化", "减持", "清仓") if kw not in t16]
        if rm_missing:
            fails.append("§16 缺 16.4 未来 6 个月决策路线图（买入/催化剂/减持/清仓 四块，各 3–4 条，"
                         f"含具体触发值；缺关键词：{'/'.join(rm_missing)}）")
        else:
            lines.append("§16 16.4 决策路线图 ✅ 四块在场（买入/催化/减持/清仓；触发值质量请在抽样审中人工核）")

    # 研究阶段：Task 1 硬产出物。coverage/meta 在 chapters[0]，存在但不计入字数。
    if stage == "research":
        alltext = "\n".join(c["text"] for c in chapters.values())
        history = chapters.get(roles.get("history"), {}).get("text", "")
        technical = chapters.get(roles.get("technical"), {}).get("text", "")
        t9 = chapters.get(9, {}).get("text", "")
        guidance_re = r"guidance\s*(?:演变|历史|兑现)|指引(?:演变|兑现|可信度)"
        if re.search(guidance_re, technical, re.I):
            fails.append("guidance 演变不得放技术入门，统一移至 §9")
        if not re.search(guidance_re, t9, re.I):
            fails.append("§9 缺最近五次 guidance 演变与可信度分析")
        if re.search(r"(?:行业)?术语(?:速览|表)|Glossary", history, re.I):
            fails.append("历史章含重复术语表；唯一 Glossary 应放技术入门末尾")
        if not re.search(r"术语表|Glossary", technical, re.I):
            fails.append("技术入门缺全报告唯一术语表")
        if "渠道覆盖矩阵" not in alltext:
            fails.append("缺 渠道覆盖矩阵（先运行 source_coverage_audit.py）")
        if "研究对象覆盖矩阵" not in alltext:
            fails.append("缺 研究对象覆盖矩阵（target/comps/upstream/downstream）")
        d = research_dir or os.path.dirname(os.path.abspath(args_in_path))
        cf = os.path.join(d, "entity_filings")
        if not (os.path.isdir(cf) and any(
                os.path.isdir(os.path.join(cf, x)) and os.listdir(os.path.join(cf, x))
                for x in os.listdir(cf))):
            fails.append(f"缺 entity_filings/<ENTITY_TYPE>/<TICKER>/ 原始材料（查 {cf}）")

    # 版本防回退（final + 提供上一版）
    if stage == "final" and prev_total is not None:
        lines.append("-" * 60)
        lines.append(f"总字数 本版 {total} vs 上一版 {prev_total}")
        if total < prev_total:
            fails.append(f"总字数回退 {total}<{prev_total}（疑似扩A砍B，逐章查 Δ）")

    lines.append("-" * 60)
    lines.append(f"正文总字数 {total}（参考：ASE骨架≈11.8k / Cloudflare深度≈28.4k）")
    return fails, warns, lines, total


def sampling_review(chapters):
    present = [n for n in chapters if chapters[n]["chars"] >= 200]
    picks = [n for n in (5, 7, 12) if n in present]
    rest = [n for n in present if n not in picks]
    if rest:
        picks.append(random.choice(rest))
    out = ["", "── 抽样人工审（机器不替代，请逐条人工核）─────────────",
           "对下列每章核深度实质（自然散文，不要 CEMRI 标签/五件套）：",
           "  □ 先区分介绍与分析：技术/历史介绍定义清楚、顺序自然、非专业读者能跟上，不强制每段数字/反方/交易结论",
           "  □ 投资判断有硬数字（带单位/年份；完整来源留后台，最终用数字角标）",
           "  □ 讲清了'为什么'（因果），不是'陈述+形容词'",
           "  □ 关键处点出了风险/反面/边界",
           "  □ 分析章节答了 2-3 个最尖的争议点；介绍章节讲清核心概念或历史转折（自然成段，不贴标签）",
           "  □ 市场/份额一律美元化 + 标的份额轨迹",
           "  □ §8 有收入结构图且解释 mix；§9 有 5–7 位逐人画像和 guidance 可信度",
           "  □ §16『重点研究问题』逐条直答了用户 Step 0 的问题（非仅写个标题；答不了的标'数据缺口+如何验证'）",
           "抽中章节： " + "  ".join(f"§{n} {CHAPTER_TITLES.get(n,'')}" for n in picks)]
    return out


args_in_path = None


def main():
    global args_in_path
    ap = argparse.ArgumentParser()
    ap.add_argument("--stage", required=True, choices=["research", "final"])
    ap.add_argument("--in", dest="inp", required=True)
    ap.add_argument("--dir", default=None, help="研究文件夹（找 entity_filings），默认 --in 所在目录")
    ap.add_argument("--prev", default=None, help="上一版 DOCX（防字数回退）")
    a = ap.parse_args()
    args_in_path = a.inp

    if a.stage == "final":
        items = parse_docx(a.inp)
    else:
        items = parse_md(a.inp)
    chapters, appendices, subs = split_sections(items)

    prev_total = None
    if a.prev:
        pc, _, _ = split_sections(parse_docx(a.prev))
        prev_total = sum(v["chars"] for v in pc.values())

    fails, warns, lines, total = audit(chapters, appendices, subs, a.stage, a.dir, prev_total)

    print("\n".join(lines))
    if warns:
        print("\n── 软警告（不阻断，但应消除）──")
        for w in warns:
            print("  ⚠ " + w)
    print("\n".join(sampling_review(chapters)))

    print("\n" + "=" * 60)
    if fails:
        print(f"❌ FAIL（{len(fails)} 项硬门槛未过）— 不得交付/不得进下一 task，回炉补足后重跑：")
        for f in fails:
            print("   • " + f)
        print("=" * 60)
        sys.exit(1)
    else:
        print("✅ PASS — 硬门槛全过。仍须完成上面的『抽样人工审』再交付/进下一 task。")
        print("=" * 60)
        sys.exit(0)


if __name__ == "__main__":
    main()
