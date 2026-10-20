# Examples

This directory separates **copyable usage contracts** from **verified execution evidence**.

## Quick-memo input contract

The following is a copyable trigger, not a precomputed investment conclusion:

```text
用 public-investment-analysis 分析 MongoDB（MDB），先做中文 quick memo。
基于最新公开文件，给出 Price Band Decision Map、3 年预期回报、priced-in vs. variant view、
三项 killer risks 和六个月行动图；缺失数据不要猜。
```

A conforming quick memo should contain:

1. snapshot date, current Price Band, 4–5 bands with actionability, and the expected 3-year return;
2. what the current price appears to discount versus the variant view;
3. the operating-state × valuation-regime bridge behind each band;
4. three falsifiable risks with tripwires;
5. a six-month action map;
6. traceable sources for factual claims and numbers;
7. explicit disclosure of missing or stale inputs.

This prompt names a public company only to demonstrate the input shape. It does not bundle a recommendation, price band, or stale market snapshot.

## Verified repository evidence

[`repository-check-2026-10-20.txt`](repository-check-2026-10-20.txt) records a real run of the deterministic repository check suite.

## Current showcase: Intel

[`intel/`](intel/README.md) exposes exactly five selected original pages (1, 3, 23, 40, 41) from the 58-page Intel report. The full report and model are not distributed. The case includes source hashes, recorded validation limits and a builder that works only from those five images.

## Historical showcase: MongoDB

[`mongodb/`](mongodb/README.md) contains five selected pages from a real 44-page MongoDB IC report, the reproducible showcase manifest, and the command used to rebuild the public GIF and result cards. The case passed model, content, depth, all-page visual QA, and independent review before it was admitted here.
