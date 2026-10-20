"""Reader-facing formatting. Inputs are base units; model values stay untouched."""
from decimal import Decimal, ROUND_HALF_UP
import re


def _decimal(value):
    result = Decimal(str(value))
    if not result.is_finite():
        raise ValueError('Non-finite report value')
    return result


def format_number(value):
    if value is None:
        return '—'
    value = _decimal(value)
    if value == 0:
        return '0'
    quantum = Decimal('1') if abs(value) >= 10 else Decimal('0.1')
    rounded = value.quantize(quantum, rounding=ROUND_HALF_UP)
    if rounded == 0:
        return '<0.1' if value > 0 else '>-0.1'
    if abs(rounded) >= 10:
        rounded = rounded.quantize(Decimal('1'), rounding=ROUND_HALF_UP)
    return f'{rounded:,f}'.rstrip('0').rstrip('.') if '.' in f'{rounded:f}' else f'{rounded:,f}'


def format_amount(value, currency='美元', unit=None):
    """unit=None selects 万/亿 automatically; set unit for an entire table column.

    currency can also be 人/台/股. Scaling never converts a currency.
    """
    if value is None:
        return '—'
    factors = {'': Decimal(1), '万': Decimal(10000), '亿': Decimal(100000000)}
    if unit is not None and unit not in factors:
        raise ValueError('unit must be empty, 万, 亿 or None')
    value = _decimal(value)
    automatic = unit is None
    if automatic:
        unit = '亿' if abs(value) >= factors['亿'] else '万' if abs(value) >= factors['万'] else ''
        # Promote again if rounding would cross the next unit boundary.
        for larger in ('万', '亿'):
            if factors[larger] > factors[unit]:
                scaled = value / factors[unit]
                quantum = Decimal(1) if abs(scaled) >= 10 else Decimal('0.1')
                if abs(scaled.quantize(quantum, rounding=ROUND_HALF_UP)) >= factors[larger] / factors[unit]:
                    unit = larger
    return f'{format_number(value / factors[unit])} {unit}{currency}'.strip()


def format_percent(value, fraction=False):
    """Default input is percentage points: 24.36 -> 24%; fraction=True: .2436 -> 24%."""
    return '—' if value is None else format_number(_decimal(value) * (100 if fraction else 1)) + '%'


METHODS_RE = re.compile(r'^(?:Appendix|附录)\s*(?:[｜|:：—\-]\s*)?(?:Methods?\b|定义与方法|方法与定义|方法说明)', re.I)
APPENDIX_RE = re.compile(r'^(?:Appendix\b|附录)', re.I)
DECIMAL_RE = re.compile(r'(?<![A-Za-z0-9_.])[-+−]?(?:\d{1,3}(?:,\d{3})+|\d+)\.\d+(?![A-Za-z0-9_.])')
FORBIDDEN_UNIT_RE = re.compile(r'百万|十亿|\b(?:million|billion|trillion)\b|(?<=\d)\s*(?:bn|mn|[mMbB])(?=\b|[/美元元港])', re.I)


def style_issues(text):
    """Lint financial display strings, not source entries or exact Methods records."""
    issues = []
    if '口径' in text:
        issues.append('methodology wording belongs in Methods Appendix')
    if FORBIDDEN_UNIT_RE.search(text):
        issues.append('large values must use 万/亿')
    # Do not mistake subsection IDs, dates, tickers or semantic versions for decimals.
    cleaned = re.sub(r'^\s*(?:§\s*)?\d+(?:\.\d+)+(?=\s)', '', text)
    cleaned = re.sub(r'\b\d{4}\.\d{1,2}\.\d{1,2}\b|\b\d{4}\.\d{1,2}\b|\bv\d+(?:\.\d+)+\b', '', cleaned, flags=re.I)
    for match in DECIMAL_RE.finditer(cleaned):
        token = match.group().replace(',', '').replace('−', '-')
        # Exclude raw identifiers like 1.6T / 300124.SZ via the token boundaries above.
        value = Decimal(token)
        decimals = len(token.split('.')[1])
        if decimals > 1 or abs(value) >= 10:
            issues.append(f'excess decimal precision: {match.group()}')
    return issues
