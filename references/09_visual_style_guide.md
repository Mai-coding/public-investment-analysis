# 09 - 视觉风格规范 v2（McKinsey）

**修订要点 (v1 → v2)**：
- 增加图表数据逻辑一致性规则（多 source 慎用）
- 双 Y 轴默认禁用规则
- 字体 fallback chain 必须能渲染 ASCII
- 雷达图 / scatter / 热力图防遮挡的具体代码模板
- 字体生成后必须 sanity check
- 全部脚本统一读取 `assets/color_palette.json`，并按亮度自动选择标签字色

---

## 一、图表数据逻辑一致性 ⚠️ v1 高发问题 ⚠️

### 1.1 一张图的所有数据必须 internally consistent

**反面案例**：把"光模块 TAM (LightCounting 口径 A) + 硅光渗透率 (LightCounting 口径 B) + 硅光芯片市场 (BP 自下而上)"放进一张双 Y 轴图。三条线讲不出统一的故事，观众发现"硅光市场快速增长 + 渗透率却趋平 + TAM 缓慢增长"——逻辑断裂。

**强制规则**：
1. **每张图必须能用同一组驱动因子讲清楚一个故事**。如果出现两个变量明显不一致（如"市场快速增长" vs "渗透率趋平"），必须先回答：增长源自哪里？
2. **多 source 数据组合时强制用驱动因子分解**：
   ```
   硅光芯片市场 +44% CAGR = 光模块出货量 +32% × 硅光渗透率 +20pp × ASP 升级 +20%
   ```
   把三层驱动**拆成独立子图**（`plt.subplots(1, 2)` 或 `(2, 1)`），每个子图讲一个完整故事。
3. **图表必须能独立站住**：标题（讲什么）+ 关键标注（数字多少）+ 副标题（so what），三件套齐全。

### 1.2 双 Y 轴默认禁用（除非有强因果关系）

**何时可以用双 Y 轴**：两个轴的指标有明确因果关系——
- 价格 vs 销量
- 利率 vs 通胀
- 客户数 vs ARPU

**何时不能用双 Y 轴**：
- TAM + 渗透率 + 第三个指标（混在一起）
- 不同 source 的"独立增长曲线"
- 单纯为了在一张图里塞更多数据

**默认行为**：所有原本想画双 Y 轴的场景，**先尝试改为双子图**：
```python
fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(15, 6))
# 子图 A：故事 1（量价拆解的"量"）
# 子图 B：故事 2（量价拆解的"价"）
```

---

## 一·五、matplotlib 用途边界 ⚠️ 强制（Redwire 教训）⚠️

v2 曾用 matplotlib 画 5 张产品 / 场景 "schematic 示意图"（业务全景、ROSA 展开、IBDM 对接、卫星轨道、任务流程），用户回复 "我不喜欢 schematic 的质量，删掉"——matplotlib 画的飞机 / 卫星像幼儿园简笔画。

**强制规则**：
- ✅ matplotlib 用于数据图表：bar / line / pie / scatter / heatmap / radar / 堆叠柱 / 量价拆解；竞争位置 scatter 可按 `04_chart_inventory.md` 使用明确标识的定性等级，不冒充实测数值。
- ❌ **不要用 matplotlib 画产品示意图、卫星 / 飞机 / 设备卡通图、物理结构图**。
- ✅ 产品/资产图片 → 优先使用真实官方图片并遵守 `17_product_images.md`；找不到可靠素材时才使用明确标注的 AI 示意图或表格。
- ✅ 概念流程图 → 用 **Mermaid**、矢量框箭头或文字 + 表格；箭头明确资金/信息/责任等关系，不画卡通产品。非 Matplotlib 输出用对应渲染器的边界/重叠检查，加实际插入尺寸人审，manifest 记录 `overlap_method`；不得伪称跑过 Matplotlib gate。
- ✅ 含 CJK 的 matplotlib 图，先按 `13_cjk_charts.md` 配置楷体/Times New Roman 及 fallback，避免方框。

---


## 二、字体与语言意图（实现唯一真源）

- 图表语言跟随报告语言；行业通用缩写可保留英文。
- 中文主标题/副标题 27/19pt；英文主标题/副标题 27/19pt。图内标签、图例、刻度和注释 17pt；来源 14pt。
- 中文默认楷体，英文/数字默认 Times New Roman（随包 LXGW WenKai / Source Serif 4 仅作回退）；**具体注册、fallback、`$` 转义和首图 sanity check 仅按 `13_cjk_charts.md` 执行**。本文件不维护第二套字体代码。

## 三、雷达图防遮挡 ⚠️ v1 问题 ⚠️

### 3.1 极坐标图的标题处理

**反面案例**：在 `polar` 轴上用 `ax.set_title()` 同时配长中文轴标签——title 与标签重叠。

**强制规则**：
```python
from scripts.report_presentation import format_number
fig = plt.figure(figsize=(12, 10))  # 至少 12×10
ax = fig.add_subplot(111, projection='polar')

# 标题用 figure-level 而非 axes-level
fig.suptitle("五维投资判断", fontsize=27, fontweight='bold', y=0.97, fontproperties=kaiti)
fig.text(0.5, 0.92, f"加权总分 {format_number(weighted)} / 10", ha='center', fontsize=19, fontproperties=kaiti)

# 标签使用 \n 换行避免单行过长
ax.set_xticklabels([f"{c}\n({w}%)" for c, w in zip(categories_en, weights)], fontsize=17, fontproperties=times)

# Score 数字用 circle bbox 包裹避免与扇形边界重叠
for ang, score in zip(angles, scores):
    ax.text(ang, score + 0.55, str(score), ha='center', fontsize=17, fontweight='bold', fontproperties=times,
            bbox=dict(boxstyle='circle,pad=0.25', facecolor='white', edgecolor='navy'))

plt.tight_layout(rect=[0, 0, 1, 0.92])  # 给 suptitle 留空间
```

---

## 四、Scatter 标签防遮挡

### 4.1 leader line + bbox 模板（必背）

对密集 scatter，3 个以上点在 1 单位距离内**必须**用 leader line + bbox：

```python
ax.annotate(name, xy=(x, y),
            xytext=(ox, oy), textcoords='offset points',
            fontsize=17, color=NAVY, fontweight='bold', fontproperties=times,
            ha='left' if ox > 0 else 'right',
            bbox=dict(boxstyle='round,pad=0.35', facecolor='white',
                      edgecolor=point_color, linewidth=1.5, alpha=0.95),
            arrowprops=dict(arrowstyle='-', color=DARK_GREY,
                            lw=0.8, alpha=0.6))
```

---


## 四·五、所有文字的通用防遮挡闸门

Scatter/radar 之外也必须检查标题、时间线节点、柱顶标签、图例和注释。每个脚本维护一个 Text artist 列表，在最终 PNG 尺寸调用：

```python
from scripts.chart_text_overlap import assert_no_text_overlap
assert_no_text_overlap(fig, qa_text_artists, pad_px=4)
```

失败后必须改布局：换 3–4 条上下车道、缩短/折行、使用 leader line、扩大画布或拆成主图+放大图。**不得仅缩小字号硬塞**。时间线在 24 个月内出现 4 个以上节点时默认使用多车道；仍冲突则拆图。

检测必须在 `tight_layout`/`constrained_layout` 完成后、`savefig` 前执行，并以 DOCX 实际插入比例复查。结果写入 `charts_manifest.json` 的 `overlap_check=PASS`。

## 五、统一色板（McKinsey）

```python
import json
from pathlib import Path

PALETTE = json.loads(Path('assets/color_palette.json').read_text(encoding='utf-8'))
LIGHT_BLUE = PALETTE['primary']['LIGHT_BLUE']  # #A8DCFA，核心数据系列 1
BLUE       = PALETTE['primary']['BLUE']        # #2F80ED，核心数据系列 2
SLATE      = PALETTE['primary']['SLATE']       # #5B6573，核心数据系列 3
NAVY       = PALETTE['primary']['NAVY']        # #061F32，仅标题/坐标/正文
ORANGE     = PALETTE['semantic']['ORANGE_WARN']
RED        = PALETTE['semantic']['RED_CRITICAL']
GREEN      = PALETTE['semantic']['GREEN_POSITIVE']
```

数据系列默认只用浅蓝、中蓝、灰蓝；NAVY 只承担文字与坐标。红/橙/绿仅表达风险或方向。禁止脚本私自定义紫色、黑色或旧亮青蓝 `#08A6F6`，禁止把黑色作为默认数据系列。

## 六、配色对比强制规则

| 底色 | 字色 | 评估 |
|------|------|------|
| LIGHT_GREY (#E8E8E8) | NAVY | ✅ 高对比 |
| LIGHT_GREY | 白色 | ❌ 看不见 |
| NAVY | 白色 | ✅ 高对比 |
| NAVY | 黑色 | ❌ 看不见 |
| 黑色 / 深色 (facecolor) | 白色 | ✅ 高对比 |
| 黑色 / 深色 (facecolor) | 黑色 | ❌ 看不见 |
| BLUE | 白色 | ✅ 高对比 |
| LIGHT_BLUE | NAVY | ✅ 高对比 |
| SLATE | 白色 | ✅ 高对比 |
| ORANGE | NAVY 加粗 | ✅ 可读 |
| ORANGE | 白色 | ⚠️ 边缘可读，慎用 |

🔴 **整图黑/深底色 → 文字一律白色（强制）**：若一张图/图片采用黑色或深色底色（`fig.patch`/`ax.set_facecolor`），则**所有文字**（主标题/副标题/轴标签/刻度/数据标注/图例/来源）必须为白色或浅色，**禁止黑底黑字 / 深底深字**。matplotlib 默认文字为黑色，深底图必须显式改色（见 `13_cjk_charts.md` §三的代码：`ax.tick_params(colors='white')`、title/label `color='white'`、`spines.set_color('white')`）。

每次生成图都检查这条。

所有柱段、堆叠段和热力图标签按填充色相对亮度自动选字色，不凭颜色名称硬编码：

```python
def label_color(hex_color):
    h = hex_color.lstrip('#')
    r, g, b = (int(h[i:i+2], 16) / 255 for i in (0, 2, 4))
    linear = [c / 12.92 if c <= 0.04045 else ((c + 0.055) / 1.055) ** 2.4 for c in (r, g, b)]
    luminance = 0.2126 * linear[0] + 0.7152 * linear[1] + 0.0722 * linear[2]
    return NAVY if luminance > 0.42 else '#FFFFFF'
```

堆叠柱每个分部标绝对值；构成是图意时再加百分比；总值统一标在柱顶。

---

## 七、字号规范

以下固定基准已按用户要求统一增加 1 pt；这是新基准，不在每次重跑时继续加 1。所有本技能生成的图表、图解与图内表格都适用，含标题、副标题、轴、刻度、图例、数值、注释及脚注。保留图像实际插入尺寸，扩大留白、换行或拆图解决碰撞；不通过缩小字体或缩放整图抵消增大。官方照片、logo 或不可编辑的来源图不重绘品牌文字；使用清晰原图并在实际插入尺寸检查可读性。

```python
TITLE_SIZE    = 27  # 中文主标题，楷体
SUBTITLE_SIZE = 19  # 中文副标题，楷体
AXIS_LABEL    = 17  # 轴标题，字体按报告语言
TICK_SIZE     = 17  # 刻度，中文用楷体；英文/数字用 Times New Roman
BODY_SIZE     = 17  # 数据标注，字体按内容语言
ANNOT_SIZE    = 17  # 图内注释，字体按报告语言
LEGEND_SIZE   = 17  # 图例，字体按报告语言
NOTE_SIZE     = 14  # 方法/口径注释；完整来源不写入 PNG
```

### 7.1 比例轴与视觉编码

- 比例、容量因子、利润率和其他百分比图默认使用 0% 起点；不得用截断纵轴夸大 1-2 个百分点的变化。
- 只有分析确实需要观察局部变化时才使用局部刻度，并在图内明确写 `Focused scale; actual change: X.X pp`，同时给出真实变化幅度；柱状图不得使用局部截断轴。
- 每一种覆盖层、阴影区、参考线、色带和形状都必须在图例或注释中给出明确语义。无法用一句话解释的视觉编码直接删除。
- 深色柱体/单元格用白字，浅色背景用 NAVY/深色字。窄柱标签使用与柱体同色的 bbox，并根据亮度选择白字或深字，确保首位数字不被边界裁掉。

## 八、DOCX 字号

```python
TITLE_PT      = 28   # 封面
COVER_TABLE_PT = 12  # 封面判断卡片/摘要表格；表内所有文字固定 12 pt
H1_PT         = 20   # 章节大标题
H2_PT         = 16   # 二级标题
H3_PT         = 13   # 三级标题
BODY_PT       = 11   # 正文
TABLE_PT      = 9.5  # 表格内
NOTE_PT       = 9    # 数字角标/方法注释；完整来源在 Appendix
```

所有报告表格的底色、表头与对齐规则由 `21_report_editorial_style.md` 统一管理。封面仍是 `TABLE_PT` 的例外：每个非空 run 显式设为 12 pt；图内字体增加不改变 DOCX 正文与封面字号。

---

## 九、数字单位与精度

唯一遵循 `21_report_editorial_style.md`：先换万/亿，再按显示数值取精度；绝对值 ≥10 无小数，<10 最多一位。英文报告保留英文单位。模型值不提前舍入。实现可用 `scripts/report_presentation.py`。注意 0.7 billion = 7 亿，1.5 billion = 15 亿，不能直接把 B 换成“亿”。

## 十、图中文字与方法说明

中文图表优先使用“美元/股”“亿美元”等文字，避免 `$...$` 触发 matplotlib math mode；必须出现 `$` 时按 `13_cjk_charts.md` 转义。图内保留指标名称、年份、单位和关键限制，详细统计边界、换算与推导进入 Methods Appendix；完整来源按 `20_citation_and_source_appendix.md`。

## 十一、热力图配色与可读性

数值敏感性热力图先选择所表达的关系，再选色标：数据跨越现价时，可用以现价为中心的红黄绿（低于/接近/高于现价）；全部位于同侧且数值集中时，用浅至深的顺序色阶突出表内差异，另行标明所有格与现价的关系。不得让窄区间淹没在宽色域中，也不得用绿色把“表内较高”伪装成“高于现价”。色彩读取统一palette，标出色条范围、单位和Base位置；截取表内范围须说明深浅仅作表内比较。主估值敏感性改变可比倍数及近期每股经营指标；终局倍数×远期盈利仅作单独零权重参考图，不画成影响主价格带的加权敏感性。

每个格子必须有数值标注（白字或黑字，根据底色亮度决定）：
```python
from scripts.report_presentation import format_number
for i in range(len(ni_axis)):
    for j in range(len(pe_axis)):
        v = price_matrix[i, j]
        ax.text(j, i, format_number(v), ha='center', va='center',
                color=label_color(cell_hex_color), fontsize=17, fontweight='bold', fontproperties=times)
```

---

## 十二、图表生成流程的 sanity check

每次生成图后必须 review：

- [ ] 一张图的所有数据是否能用同一组驱动因子讲通？
- [ ] 双 Y 轴是否真的有强因果关系？没有的话改双子图
- [ ] 中文字体是否正常渲染（数字 + 字母 + 中文混合）？
- [ ] 雷达图标题是否用 fig-level 避免遮挡？
- [ ] Scatter 标签是否用 leader line + bbox？
- [ ] 配色对比是否足够（浅底深字 / 深底白字）？**整图黑/深底色时文字是否全部为白色/浅色（无黑底黑字）？**
- [ ] 数据标签是否被柱挡住？
- [ ] 比例轴是否从 0% 起；局部刻度是否标 `Focused scale` 和真实百分点变化？
- [ ] 每个覆盖层、阴影区、参考线和形状是否有明确语义；无语义编码是否已删除？
- [ ] 图表语言是否跟随报告语言；中文文字用楷体，英文与数字用 Times New Roman（回退须已披露）；标签/图例/刻度/注释 17pt、来源 14pt？
- [ ] 副标题是否含 `$` 触发 math mode？
- [ ] 每张图是否有数据源标注？

---

## 十三、三个高频图元易错点（时间线 / 饼图 / 源注释）⚠️ 实测踩过

> 图表人审见 [Charts and images](10_final_checklist.md#c-charts-and-images--inspect-every-file)；本文件负责绘图规范。

1. **时间线必须标年份**：节点光靠 x 位置不够——①给一条年份刻度轴（每 2 年一格）；②每个节点标签前缀年份（"2019 首次商用"而非"首次商用"）。
2. **饼图 / 堆叠柱图：图上同时标"绝对值 + 百分比"**，不能只放图例。环形图用 `labeldistance≈1.1` 把"名称\nXX 单位 (YY%)"放到扇区外。
3. **最终 PNG 不印完整来源名或 URL**。全量来源写入 `charts_manifest.json`，DOCX 图注用数字上标并由 Sources Appendix 解析。图内只保留准确指标名称、单位和决策相关限制；详细方法与统计边界进入 Methods Appendix，不贴 `Inference` 标签。

---
