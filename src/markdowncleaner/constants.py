import re

SKIP_TYPES = {"code_inline", "code_block", "fence"}  # never touch code
SENT_DELIM = "\uFFF9"

# compile once
SHORT_DUP_RE = re.compile(
            rf"\b([A-Za-z]{{1,3}})(?:\s*{SENT_DELIM}\s*|\s+)+\1\b",  # ← sentinel counts as space
            flags=re.I)

_DUP_RE = re.compile(
    rf"""
    \b([A-Za-z]{{1,3}})            # short word (capture = \1)
    (?:\s*|{SENT_DELIM})+          # any mix of spaces or sentinel(s)
    \1                             # the SAME short word again …
    (?=\W|{SENT_DELIM})?           # … if it is a stand-alone token
    """,
    re.IGNORECASE | re.VERBOSE,
)

