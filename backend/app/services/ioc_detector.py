import ipaddress
import re


HASH_PATTERNS = {
    32: "md5",
    40: "sha1",
    64: "sha256",
}

_HEX_RE = re.compile(r"^[0-9a-fA-F]+$")

_DOMAIN_RE = re.compile(
    r"^(?!-)[A-Za-z0-9-]{1,63}(?<!-)(\.[A-Za-z0-9-]{1,63}(?<!-))+$"
)


def detect_ioc_type(indicator: str) -> str:
    indicator = indicator.strip()

    # 1. Hash (most specific - check first)
    if len(indicator) in HASH_PATTERNS and _HEX_RE.match(indicator):
        return "hash"

    # 2. URL
    if indicator.lower().startswith(("http://", "https://")):
        return "url"

    # 3. IP address
    try:
        ipaddress.ip_address(indicator)
        return "ip"
    except ValueError:
        pass

    # 4. Domain (validated, not a blind fallback)
    if _DOMAIN_RE.match(indicator):
        return "domain"

    raise ValueError(f"Unrecognized indicator format: {indicator!r}")
