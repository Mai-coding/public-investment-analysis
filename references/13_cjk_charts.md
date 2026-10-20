# 13 - matplotlib 图表字体：中文楷体 + 英文 Times New Roman

> **图表字体与报告正文一致**：中文用 **楷体**（Windows `KaiTi`/`SimKai`，macOS `Kaiti SC`/`STKaiti`），英文/数字用 **Times New Roman**。二者均为系统字体，**不随包分发**。随包的 OFL 字体 LXGW WenKai（楷体风格）与 Source Serif 4（Times 风格衬线）仅作 fallback。matplotlib 默认 DejaVu Sans 不支持 CJK（中文渲染成方框），必须**在画第一张图之前**就配好。DOCX 正文字体规则见 `task5-report-assembly.md`。

---

## 一、配置（fallback chain，一次性）

matplotlib 3.6+ 支持按 `font.family` 列表**逐字符回退**：把 Times New Roman 放第一位（拉丁字母/数字优先命中），中文字符再回退到楷体。这样**同一个字符串里中英混排**也能各用各的字体。

```python
from matplotlib import font_manager as fm
import matplotlib.pyplot as plt
from pathlib import Path

# 系统字体优先；只注册当前运行时确实存在的文件。随包 OFL 字体仅兜底。
skill_root = Path('<skill>')
candidates = (
    Path('C:/Windows/Fonts/times.ttf'), Path('C:/Windows/Fonts/simkai.ttf'),
    Path('/System/Library/Fonts/Supplemental/Times New Roman.ttf'),
    Path('/Library/Fonts/Times New Roman.ttf'),
    skill_root / 'assets/fonts/SourceSerif4-Regular.ttf',
    skill_root / 'assets/fonts/LXGWWenKai-Regular.ttf',
)
for path in candidates:
    if path.is_file():
        fm.fontManager.addfont(path)

plt.rcParams['font.family'] = [
    'Times New Roman', 'KaiTi', 'Kaiti SC', 'STKaiti',
    'Source Serif 4', 'LXGW WenKai', 'Noto Serif CJK SC', 'DejaVu Sans'
]
plt.rcParams['axes.unicode_minus'] = False                  # 负号正常（并避免 U+2212）
```

> 注册后用 `fm.fontManager.ttflist` 确认实际 family 名（macOS 已安装的 Kaiti SC/STKaiti 通常已被 matplotlib 自动发现）。系统中没有 Times New Roman 或楷体时（如云端 Linux 沙盒），自动退到随包 Source Serif 4 / LXGW WenKai；**发生回退必须在确认卡说明**。不得提交 SimKai、Times New Roman 等专有字体二进制，也不得从不明来源下载字体。

---

## 二、两个必避的坑（实测踩过）

1. **`$` 触发 mathtext，把中文渲染成数学字体**：标题/标签里出现**两个及以上 `$`**（如 "NT$/股 … NT$495"）会被 matplotlib 当成 `$...$` 数学公式，中间的中文用数学罗马体（无 CJK）→ 方框/'rm' 警告。**所有文本里的 `$` 必须转义为 `\$`**（f-string 里写 `\\$` 或 `\$`）。
2. **负号 U+2212**：正文里别手敲 "−"(U+2212)，用 ASCII "-"；并设 `axes.unicode_minus=False`。

---

## 三、强制 sanity check（画完第 1 张图立即做，用当前运行时的图片查看能力肉眼看）

- [ ] 中文是 **楷体**（或已披露的 LXGW WenKai 回退）、无方框（如"营收与增长""市场吸引力"）。
- [ ] 英文/数字是 **Times New Roman**（或已披露的 Source Serif 4 回退）、无方框（如 "Forward P/E" "2026E" "1,004"）。
- [ ] 中英混排串正常（如 "ASE 2026E EPS NT$14.4"）。
- [ ] 无 `Font 'rm' does not have a glyph` 警告（有 → 查 `$` 未转义）。
- [ ] **黑/深底色图：文字全部白色/浅色，无黑底黑字**（matplotlib 文字默认黑色，深底图必须显式改色）。

发现方框或字体不对**立即修、重画全部**，不要先把 13 张图都生成再回头返工。

> **深/黑底图配色（强制，见 `09_visual_style_guide.md` 的配色对比规则）**：若 `fig.patch`/`ax.set_facecolor` 设黑/深色，必须显式把文字与轴线转白：
> ```python
> ax.set_facecolor('#061F32'); fig.patch.set_facecolor('#061F32')
> ax.tick_params(colors='white')                      # 刻度
> ax.set_title(t, color='white'); ax.set_xlabel(x, color='white'); ax.set_ylabel(y, color='white')
> for sp in ax.spines.values(): sp.set_color('white')  # 边框
> # 数据标注/图例/来源文字也逐个传 color='white'
> ```

---

## 四、缓存复用

字体注册是进程级的，同一会话内多次画图只需配一次。新会话重跑配置即可（沙盒可能重置）。
