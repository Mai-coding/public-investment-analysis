#!/usr/bin/env python3
"""Rebuild the public MongoDB showcase from audited report-page images."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont, ImageOps


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_SOURCE = ROOT / "examples" / "mongodb" / "source-pages"
DEFAULT_OUTPUT = ROOT / "assets" / "showcase"
MANIFEST = ROOT / "examples" / "mongodb" / "showcase_manifest.json"
FONT = ROOT / "assets" / "fonts" / "LXGWWenKai-Regular.ttf"
SERIF = ROOT / "assets" / "fonts" / "SourceSerif4-Regular.ttf"

GREEN = "#00684A"
DARK = "#102A24"
MID = "#52655F"
PALE = "#F2F6F4"
BLUE = "#2F7EE6"
ORANGE = "#E97722"


SLIDES = [
    {
        "file": "cover.png",
        "page": 1,
        "zh": "投资结论",
        "en": "Investment conclusion",
        "detail": "评级、目标价与安全边际先行",
        "crop": (0.00, 0.00, 1.00, 1.00),
    },
    {
        "file": "competition.png",
        "page": 17,
        "zh": "竞争结构",
        "en": "Competitive structure",
        "detail": "先解释评分，再展示单一矩阵",
        "crop": (0.00, 0.02, 1.00, 0.98),
    },
    {
        "file": "valuation-sensitivity.png",
        "page": 30,
        "zh": "情景与敏感性",
        "en": "Scenarios & sensitivity",
        "detail": "增长、EPS 与倍数不混成一个故事",
        "crop": (0.00, 0.01, 1.00, 0.98),
    },
    {
        "file": "scenario-weights.png",
        "page": 31,
        "zh": "概率权重",
        "en": "Probability weights",
        "detail": "五情景、事件链与权重敏感性对账",
        "crop": (0.00, 0.01, 1.00, 0.98),
    },
    {
        "file": "valuation-summary.png",
        "page": 32,
        "zh": "估值交叉验证",
        "en": "Valuation cross-check",
        "detail": "DCF、P/S 与 P/E 共享预测年度",
        "crop": (0.00, 0.00, 1.00, 0.72),
    },
]


def font(path: Path, size: int) -> ImageFont.FreeTypeFont:
    return ImageFont.truetype(str(path), size=size)


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def crop_fraction(image: Image.Image, box: tuple[float, float, float, float]) -> Image.Image:
    width, height = image.size
    return image.crop((int(width * box[0]), int(height * box[1]), int(width * box[2]), int(height * box[3])))


def wrap_pixels(draw: ImageDraw.ImageDraw, text: str, text_font: ImageFont.FreeTypeFont,
                max_width: int) -> str:
    lines: list[str] = []
    current = ""
    for character in text:
        candidate = current + character
        if current and draw.textlength(candidate, font=text_font) > max_width:
            lines.append(current)
            current = character
        else:
            current = candidate
    if current:
        lines.append(current)
    return "\n".join(lines)


def paste_card(canvas: Image.Image, image: Image.Image, box: tuple[int, int, int, int]) -> None:
    left, top, right, bottom = box
    shadow = Image.new("RGBA", (right - left + 18, bottom - top + 18), (0, 0, 0, 0))
    ImageDraw.Draw(shadow).rounded_rectangle((8, 8, shadow.width - 1, shadow.height - 1), 8, fill=(21, 49, 41, 45))
    canvas.paste(shadow, (left - 1, top - 1), shadow)
    fitted = ImageOps.contain(image.convert("RGB"), (right - left, bottom - top), Image.Resampling.LANCZOS)
    card = Image.new("RGB", (right - left, bottom - top), "white")
    card.paste(fitted, ((card.width - fitted.width) // 2, (card.height - fitted.height) // 2))
    canvas.paste(card, (left, top))


def build_gif(source: Path, output: Path) -> Path:
    frames: list[Image.Image] = []
    title_font = font(FONT, 46)
    label_font = font(FONT, 27)
    body_font = font(FONT, 22)
    small_font = font(FONT, 17)
    for index, slide in enumerate(SLIDES, start=1):
        canvas = Image.new("RGB", (1200, 675), PALE)
        draw = ImageDraw.Draw(canvas)
        draw.rectangle((0, 0, 340, 675), fill=GREEN)
        draw.text((44, 42), f"{index:02d} / 05", font=small_font, fill="#A9D9C8")
        draw.text((44, 94), slide["zh"], font=title_font, fill="white")
        draw.text((44, 154), slide["en"], font=label_font, fill="#D5EEE5")
        draw.rounded_rectangle((44, 226, 296, 358), 14, fill="#0A7658")
        detail = wrap_pixels(draw, slide["detail"], body_font, 205)
        draw.multiline_text((65, 250), detail, font=body_font, fill="white", spacing=10)
        draw.text((44, 525), "真实 MongoDB 回放", font=body_font, fill="white")
        draw.text((44, 560), "Real audited report run", font=small_font, fill="#D5EEE5")
        draw.text((44, 602), "44 pages · 0 blocking failures", font=small_font, fill="#A9D9C8")
        page = crop_fraction(Image.open(source / slide["file"]).convert("RGB"), slide["crop"])
        paste_card(canvas, page, (385, 34, 1158, 625))
        for dot in range(len(SLIDES)):
            color = ORANGE if dot == index - 1 else "#B8C7C2"
            draw.ellipse((735 + dot * 28, 642, 747 + dot * 28, 654), fill=color)
        frames.append(canvas)
    gif_path = output / "mongodb-workflow.gif"
    frames[0].save(
        gif_path,
        save_all=True,
        append_images=frames[1:],
        duration=1500,
        loop=0,
        optimize=True,
        disposal=2,
    )
    return gif_path


def build_overview(source: Path, output: Path) -> Path:
    canvas = Image.new("RGB", (1500, 940), PALE)
    draw = ImageDraw.Draw(canvas)
    draw.text((64, 42), "A report is not done until the evidence agrees.", font=font(SERIF, 46), fill=DARK)
    draw.text((66, 106), "MongoDB full-report showcase · 2026-07-26 snapshot", font=font(FONT, 25), fill=MID)
    cards = [
        ("cover.png", "01 结论先行", (55, 170, 465, 750)),
        ("competition.png", "02 竞争证据", (545, 170, 955, 750)),
        ("valuation-sensitivity.png", "03 估值对账", (1035, 170, 1445, 750)),
    ]
    for filename, label, box in cards:
        paste_card(canvas, Image.open(source / filename).convert("RGB"), box)
        draw.text((box[0], 772), label, font=font(FONT, 25), fill=GREEN)
    metrics = [
        ("23 / 23", "content gates"),
        ("14 / 14", "model hard gates"),
        ("44", "pages visually checked"),
        ("38,419", "body characters"),
    ]
    for idx, (value, label) in enumerate(metrics):
        x = 62 + idx * 355
        draw.rounded_rectangle((x, 832, x + 315, 914), 12, fill="white", outline="#C9D8D2", width=2)
        draw.text((x + 20, 845), value, font=font(SERIF, 30), fill=GREEN)
        draw.text((x + 122, 856), label, font=font(SERIF, 19), fill=MID)
    path = output / "mongodb-showcase.png"
    canvas.save(path, optimize=True)
    return path


def build_result_card(output: Path) -> Path:
    canvas = Image.new("RGB", (1200, 675), GREEN)
    draw = ImageDraw.Draw(canvas)
    draw.text((65, 48), "PUBLIC INVESTMENT ANALYSIS", font=font(SERIF, 24), fill="#A9D9C8")
    draw.text((65, 94), "MongoDB full-report run", font=font(SERIF, 52), fill="white")
    draw.text((67, 162), "Independent validation: PASS", font=font(FONT, 28), fill="#D5EEE5")
    metrics = [
        ("23 / 23", "内容门槛 / content gates", BLUE),
        ("0", "阻塞失败 / blocking failures", ORANGE),
        ("44", "逐页视觉检查 / pages checked", "#23B26D"),
        ("10 / 10", "仓库检查 / repository checks", "#9B72E8"),
    ]
    for idx, (value, label, color) in enumerate(metrics):
        x = 65 + (idx % 2) * 555
        y = 235 + (idx // 2) * 150
        draw.rounded_rectangle((x, y, x + 510, y + 118), 16, fill="white")
        draw.rectangle((x, y, x + 12, y + 118), fill=color)
        draw.text((x + 34, y + 18), value, font=font(SERIF, 39), fill=DARK)
        draw.text((x + 190, y + 42), label, font=font(FONT, 20), fill=MID)
    draw.text((67, 565), "2026-07-26 market snapshot · research artifact, not investment advice", font=font(SERIF, 21), fill="#D5EEE5")
    draw.text((67, 608), "Sources → model → valuation → charts → IC report", font=font(SERIF, 22), fill="white")
    path = output / "mongodb-result-card.png"
    canvas.save(path, optimize=True)
    return path


def write_manifest(source: Path, outputs: list[Path]) -> None:
    payload = {
        "case": "MongoDB (NASDAQ: MDB)",
        "market_snapshot": "2026-07-26",
        "report_pages": 44,
        "body_characters": 38419,
        "source_report": {
            "filename": "MongoDB_IC_Report_v1_QA.pdf",
            "sha256": "1ec63eee5072169a4e382037a25832ef995b2bf1e69b1ae42d88a02d20026a5c",
            "distributed": False,
        },
        "source_page_map": {slide["file"]: slide["page"] for slide in SLIDES},
        "validation": {
            "report_content_audit": "23 PASS / 0 WARN / 0 FAIL",
            "artifact_audit": "14 PASS / 2 WARN / 0 FAIL",
            "depth_audit": "PASS",
            "repository_checks": "10 PASS / 0 FAIL",
            "independent_review": "PASS",
        },
        "known_non_blocking_limitation": "Repurchase cash-floor formulas require an Excel recalculation before a live investment delivery.",
        "source_pages": {slide["file"]: sha256(source / slide["file"]) for slide in SLIDES},
        "generated_assets": {path.name: sha256(path) for path in outputs},
        "rebuild": "python scripts/build_showcase.py",
    }
    MANIFEST.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--source-dir", type=Path, default=DEFAULT_SOURCE)
    parser.add_argument("--output-dir", type=Path, default=DEFAULT_OUTPUT)
    args = parser.parse_args()
    args.output_dir.mkdir(parents=True, exist_ok=True)
    missing = [slide["file"] for slide in SLIDES if not (args.source_dir / slide["file"]).is_file()]
    if missing:
        raise SystemExit(f"Missing source page(s): {', '.join(missing)}")
    outputs = [
        build_gif(args.source_dir, args.output_dir),
        build_overview(args.source_dir, args.output_dir),
        build_result_card(args.output_dir),
    ]
    write_manifest(args.source_dir, outputs)
    for path in outputs:
        print(path.relative_to(ROOT))
    print(MANIFEST.relative_to(ROOT))


if __name__ == "__main__":
    main()
