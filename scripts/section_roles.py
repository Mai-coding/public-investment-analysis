"""Resolve introductory chapter roles from titles, independently of numbering."""
import re

ROLE_PATTERNS = {
    "technical": re.compile(r"(?:技术|业务).*(?:入门|基础|科普)|(?:technical|technology|business).*(?:intro|primer|fundamentals)", re.I),
    "history": re.compile(r"(?:行业|公司).*(?:历史|纵向|演进)|(?:industry|company).*(?:history|evolution|longitudinal)", re.I),
}


def resolve_intro_roles(headings):
    roles, errors = {}, []
    for role, pattern in ROLE_PATTERNS.items():
        found = [number for number, title in headings.items() if pattern.search(title)]
        if len(found) != 1:
            errors.append(f"Expected one {role} introduction chapter; found {len(found)}")
        else:
            roles[role] = found[0]
    if len(roles) == 2 and roles["technical"] == roles["history"]:
        errors.append("Technical introduction and history must be distinct chapters")
    return roles, errors
