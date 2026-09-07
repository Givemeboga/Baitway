"""Analyse des pieces jointes : empreintes et extensions a risque.

Les pieces jointes ne sont jamais executees ni ecrites sur disque ; seul leur
contenu binaire est hache en memoire.
"""

import hashlib

DANGEROUS_EXTENSIONS = {
    "exe", "scr", "pif", "bat", "cmd", "com", "js", "jse", "vbs", "vbe", "wsf",
    "wsh", "hta", "jar", "msi", "ps1", "lnk", "reg", "dll", "cpl", "scf", "inf",
}
MACRO_EXTENSIONS = {"docm", "xlsm", "pptm", "dotm", "xltm", "xlam"}
ARCHIVE_EXTENSIONS = {"zip", "rar", "7z", "gz", "tar", "iso", "img", "cab"}
# Extensions souvent utilisees comme leurre dans une double extension.
DECOY_EXTENSIONS = {"pdf", "doc", "docx", "xls", "xlsx", "jpg", "jpeg", "png", "txt"}


def extension_of(filename):
    return filename.rsplit(".", 1)[-1].lower() if "." in filename else ""


def analyse_attachment(attachment):
    """Analyse une piece jointe et renvoie son entree de contrat + ses signaux."""
    filename = attachment["filename"]
    payload = attachment.get("payload") or b""
    extension = extension_of(filename)

    flags = []
    signals = []

    if extension in DANGEROUS_EXTENSIONS:
        flags.append("dangerous_extension")
        signals.append(("attachment_dangerous", f"Executable extension ({filename})"))

    parts = filename.lower().split(".")
    if len(parts) > 2 and parts[-2] in DECOY_EXTENSIONS:
        flags.append("double_extension")
        signals.append(("attachment_double_extension", f"Double extension ({filename})"))

    if extension in MACRO_EXTENSIONS:
        flags.append("macro_enabled")
        signals.append(("attachment_macro", f"Macro-enabled document ({filename})"))

    if extension in ARCHIVE_EXTENSIONS:
        flags.append("archive")
        signals.append(("attachment_archive", f"Archive that may hide a payload ({filename})"))

    if extension in DANGEROUS_EXTENSIONS or "double_extension" in flags:
        reputation = "malicious"
    elif flags:
        reputation = "suspicious"
    else:
        reputation = "unknown"

    return {
        "filename": filename,
        "md5": hashlib.md5(payload).hexdigest(),
        "sha256": hashlib.sha256(payload).hexdigest(),
        "size": attachment.get("size", len(payload)),
        "reputation": reputation,
        "flags": flags,
    }, signals


def analyse_attachments(parsed):
    entries = []
    signals = []
    for attachment in parsed["attachments"]:
        entry, attachment_signals = analyse_attachment(attachment)
        entries.append(entry)
        signals.extend(attachment_signals)
    return entries, signals
