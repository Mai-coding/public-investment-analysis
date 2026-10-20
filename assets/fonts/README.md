# Bundled open font assets

The repository bundles two redistributable fonts so charts render consistently
without depending on a specific operating system:

- `LXGWWenKai-Regular.ttf` — Chinese; LXGW WenKai, SIL OFL 1.1.
  Source: <https://github.com/lxgw/LxgwWenKai>
- `SourceSerif4-Regular.ttf` — Latin letters and numbers; Source Serif 4,
  SIL OFL 1.1. Source: <https://github.com/adobe-fonts/source-serif>

The corresponding upstream license texts are stored beside the font binaries:

- `OFL-LXGW-WenKai.txt`
- `OFL-Source-Serif-4.md`

Do not commit `SimKai.ttf`, `times.ttf`, or other proprietary system fonts.
The house style is KaiTi (Chinese) + Times New Roman (Latin/numbers), loaded
from the operating system. These bundled open fonts are the fallback when the
system fonts are unavailable (e.g. cloud Linux sandboxes); disclose any fallback
in the completion card.
