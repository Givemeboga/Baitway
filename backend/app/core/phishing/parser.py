"""Parseur .eml : transforme un e-mail brut en structure exploitable.

S'appuie sur la bibliotheque standard `email`. Aucune piece jointe n'est
jamais executee ni ecrite sur disque : seul son contenu binaire est lu en
memoire pour calculer les empreintes.
"""

from email import message_from_string, policy
from email.utils import parseaddr


def _decode(payload, charset):
    """Decode un payload binaire sans jamais lever d'exception."""
    for encoding in (charset, "utf-8", "latin-1"):
        if not encoding:
            continue
        try:
            return payload.decode(encoding, errors="replace")
        except (LookupError, AttributeError):
            continue
    return ""


def parse_email(raw_email):
    """Parse un e-mail brut et renvoie ses composants.

    Renvoie un dict : subject, from_addr, from_display, reply_to, received,
    auth_results, body_text, body_html, attachments.
    """
    try:
        msg = message_from_string(raw_email, policy=policy.default)
    except Exception:
        # E-mail mal forme : on retombe sur le parseur permissif historique.
        msg = message_from_string(raw_email)

    from_display, from_addr = parseaddr(str(msg.get("From", "")))
    _, reply_to = parseaddr(str(msg.get("Reply-To", "")))

    body_text = []
    body_html = []
    attachments = []

    for part in msg.walk():
        if part.get_content_maintype() == "multipart":
            continue

        filename = part.get_filename()
        disposition = part.get_content_disposition()

        if disposition == "attachment" or filename:
            try:
                payload = part.get_payload(decode=True) or b""
            except Exception:
                payload = b""
            attachments.append(
                {
                    "filename": filename or "sans_nom",
                    "content_type": part.get_content_type(),
                    "size": len(payload),
                    "payload": payload,
                }
            )
            continue

        try:
            payload = part.get_payload(decode=True)
        except Exception:
            payload = None
        if payload is None:
            continue

        text = _decode(payload, part.get_content_charset())
        if part.get_content_type() == "text/html":
            body_html.append(text)
        else:
            body_text.append(text)

    return {
        "subject": str(msg.get("Subject", "")).strip(),
        "from_addr": from_addr.lower(),
        "from_display": from_display,
        "reply_to": reply_to.lower(),
        "received": [str(h) for h in msg.get_all("Received", [])],
        "auth_results": [str(h) for h in msg.get_all("Authentication-Results", [])],
        "received_spf": [str(h) for h in msg.get_all("Received-SPF", [])],
        "body_text": "\n".join(body_text),
        "body_html": "\n".join(body_html),
        "attachments": attachments,
    }
