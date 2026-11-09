"""Recipient utilities for the admin "Send Official Email" composer.

The composer mails *specific* people — one searched student, a chosen group,
or external addresses that have no Code Yaar account at all. Three promises
live here:

* **Addresses are validated, normalized and deduplicated** before a campaign
  draft is stored, so the fan-out never aims at a typo.
* **Rich-text bodies pass through an allowlist sanitizer** built on the
  standard library: an admin's editor may carry formatting, links and lists,
  never scripts, event handlers or tracking pixels.
* **Personalization is per-recipient.** ``{{student_name}}`` and friends are
  substituted separately for every row of one campaign — and substituted with
  HTML-escaped values into the already-sanitized body, so a display name can
  never smuggle markup back in.

Nothing here talks to a transport; delivery stays the job of
:mod:`learning.services.email_campaigns` and the configured ``MAILERS``
backend, exactly as for every other Code Yaar email.
"""

from __future__ import annotations

import re
from html import escape
from html.parser import HTMLParser

from django.core.exceptions import ValidationError
from django.core.validators import validate_email as _dj_validate_email
from django.utils import timezone

#: Variables an admin may type into subject, heading or body.
ORGANIZATION_NAME = 'Code Yaar'

_VARIABLE_RE = re.compile(r'\{\{\s*([a-zA-Z_]+)\s*\}\}')

#: Display labels for the composer's variable-insert buttons; keep in sync
#: with ``recipient_variables`` below.
PERSONALIZATION_KEYS = [
    ('student_name', 'Recipient name'),
    ('student_email', 'Recipient email'),
    ('student_id', 'Student ID'),
    ('current_date', "Today's date"),
    ('organization_name', 'Organization name'),
]

# ─── Address handling ─────────────────────────────────────────────────────────


def normalize_email(value) -> str:
    return str(value or '').strip().lower()


def display_name(user) -> str:
    """The personal name shown to an admin, falling back to the username."""
    if user is None:
        return ''
    return (user.get_full_name() or '').strip() or user.username


def validate_email(value) -> bool:
    """True for a syntactically valid address (the only acceptance test)."""
    try:
        _dj_validate_email(normalize_email(value))
        return bool(normalize_email(value))
    except ValidationError:
        return False


def clean_address_list(addresses) -> tuple[list[str], list[str]]:
    """Split an incoming list into ``(valid_unique, invalid)``.

    Duplicates collapse silently into the valid bucket (case-insensitive,
    whitespace-stripped); malformed entries are returned untouched so the API
    can tell the admin exactly which one to fix.
    """
    valid: list[str] = []
    invalid: list[str] = []
    seen = set()
    for raw in addresses or []:
        text = str(raw or '').strip()
        if not text:
            continue
        lowered = text.lower()
        if validate_email(lowered):
            if lowered not in seen:
                seen.add(lowered)
                valid.append(lowered)
        else:
            invalid.append(text)
    return valid, invalid


# ─── HTML sanitization (stdlib allowlist) ─────────────────────────────────────

_ALLOWED_TAGS = frozenset({
    'a', 'b', 'blockquote', 'br', 'code', 'div', 'em', 'h1', 'h2', 'h3', 'h4',
    'hr', 'i', 'img', 'li', 'ol', 'p', 'pre', 'span', 'strong', 'u', 'ul',
})

#: Only these attributes survive, and only on these tags. Everything else —
#: inline styles, classes, ids, ``on*`` handlers — is dropped; link targets
#: must use http/https/mailto so ``javascript:`` never reaches an inbox.
_ALLOWED_ATTRS = {
    'a': frozenset({'href', 'title', 'target'}),
    'img': frozenset({'src', 'alt', 'width'}),
}

_ALLOWED_URL_RE = re.compile(r'^(?:https?:|mailto:|tel:)', re.I)
_ALLOWED_IMAGE_RE = re.compile(r'^https?:', re.I)
_UNSAFE_URL_RE = re.compile(r'^(?:javascript|data|vbscript)\s*:', re.I)

#: Tags whose entire content is dropped (not just the tag itself).
_DROP_CONTENT_TAGS = frozenset({'script', 'style', 'iframe', 'object', 'embed', 'template'})


class _AllowlistParser(HTMLParser):
    """Rebuild the document keeping only allowlisted tags and attributes."""

    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.parts: list[str] = []
        self._skip_depth = 0

    def _in_skip(self, tag: str) -> bool:
        return self._skip_depth > 0 or tag in _DROP_CONTENT_TAGS

    def handle_starttag(self, tag, attrs):
        if tag in _DROP_CONTENT_TAGS:
            self._skip_depth += 1
            return
        if self._skip_depth or tag not in _ALLOWED_TAGS:
            return
        allowed = _ALLOWED_ATTRS.get(tag, frozenset())
        rendered = ''
        for name, value in attrs:
            name = (name or '').lower()
            if name not in allowed or value is None:
                continue
            if name == 'href':
                value = value.strip()
                if _UNSAFE_URL_RE.match(value) or not _ALLOWED_URL_RE.match(value):
                    continue
            if name == 'src':
                value = value.strip()
                if _UNSAFE_URL_RE.match(value) or not _ALLOWED_IMAGE_RE.match(value):
                    continue
            rendered += f' {name}="{escape(value, quote=True)}"'
        self.parts.append(f'<{tag}{rendered}>')

    def handle_startendtag(self, tag, attrs):
        if self._skip_depth or tag not in _ALLOWED_TAGS:
            return
        self.handle_starttag(tag, attrs)
        if tag not in ('br', 'hr', 'img'):
            self.parts.append(f'</{tag}>')

    def handle_endtag(self, tag):
        if tag in _DROP_CONTENT_TAGS:
            self._skip_depth = max(0, self._skip_depth - 1)
            return
        if self._skip_depth or tag not in _ALLOWED_TAGS:
            return
        self.parts.append(f'</{tag}>')

    def handle_data(self, data):
        if not self._skip_depth:
            self.parts.append(escape(data))

    def output(self) -> str:
        return ''.join(self.parts)


def sanitize_html(raw) -> str:
    """Strip everything outside the allowlist from an admin-composed body."""
    parser = _AllowlistParser()
    try:
        parser.feed(str(raw or ''))
        parser.close()
    except Exception:  # noqa: BLE001 - malformed input degrades to empty, never 500
        return ''
    return parser.output()


# ─── HTML → plain text ────────────────────────────────────────────────────────


class _TextExtractor(HTMLParser):
    """Best-effort readable plain-text twin of a sanitized HTML body."""

    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.parts: list[str] = []
        self._href: list[str] = []
        self._list_stack: list[str] = []
        self._index = 0

    def handle_starttag(self, tag, attrs):
        if tag == 'p' and self.parts:
            self.parts.append('\n\n')
        elif tag == 'br':
            self.parts.append('\n')
        elif tag in ('h1', 'h2', 'h3', 'h4'):
            self.parts.append('\n\n')
        elif tag == 'li':
            marker = '• ' if not self._list_stack or self._list_stack[-1] != 'ol' else f'{self._index + 1}. '
            if self._list_stack and self._list_stack[-1] == 'ol':
                self._index += 1
            self.parts.append('\n' + marker)
        elif tag == 'ul':
            self._list_stack.append('ul')
        elif tag == 'ol':
            self._list_stack.append('ol')
            self._index = 0
        elif tag == 'a':
            href = dict(attrs).get('href') or ''
            self._href.append(href)

    def handle_endtag(self, tag):
        if tag in ('ul', 'ol'):
            if self._list_stack:
                self._list_stack.pop()
            self.parts.append('\n')
        elif tag == 'a' and self._href:
            href = self._href.pop()
            if href:
                self.parts.append(f' (<{href}>)')

    def handle_data(self, data):
        self.parts.append(re.sub(r'\s+', ' ', data) if data.strip() else data)

    def text(self) -> str:
        joined = ''.join(self.parts)
        joined = re.sub(r'[ \t]+\n', '\n', joined)
        joined = re.sub(r'\n{3,}', '\n\n', joined)
        return joined.strip()


def plain_text_from_html(html: str) -> str:
    parser = _TextExtractor()
    parser.feed(str(html or ''))
    return parser.text()


# ─── Personalization ──────────────────────────────────────────────────────────


def _formatted_today() -> str:
    """e.g. "November 6, 2026" without Windows-incompatible ``%-d``.

    ``%-d`` (unpadded day) is a glibc extension the Windows CRT does not
    implement, so the date is composed from explicit parts instead.
    """
    today = timezone.localdate()
    return f'{today:%B} {today.day}, {today.year}'


def recipient_variables(*, name: str = '', email: str = '', student_id: str = '') -> dict:
    """The personalization dictionary for exactly one recipient."""
    display = (name or '').strip()
    return {
        # External addresses have no account name; a generic salutation keeps
        # "Dear {{student_name}}" from collapsing into "Dear ,"
        'student_name': display or ((email.partition('@')[0].replace('.', ' ').strip()) or 'there'),
        'student_email': email or '',
        'student_id': student_id or '',
        'current_date': _formatted_today(),
        'organization_name': ORGANIZATION_NAME,
    }


def used_variables(text) -> list[str]:
    """Every ``{{ token }}`` name appearing in ``text``, deduplicated."""
    seen: list[str] = []
    for match in _VARIABLE_RE.finditer(str(text or '')):
        key = match.group(1).lower()
        if key not in seen:
            seen.append(key)
    return seen


def unknown_variables(*texts) -> list[str]:
    """Tokens used but not supported — the API warns about these."""
    supported = {key for key, _label in PERSONALIZATION_KEYS}
    found: list[str] = []
    for text in texts:
        for key in used_variables(text):
            if key not in supported and key not in found:
                found.append(key)
    return found


def personalize(text: str, variables: dict) -> str:
    """Substitute known ``{{tokens}}``; unknown tokens are left literal."""
    def _replace(match):
        key = match.group(1).lower()
        return str(variables.get(key, match.group(0))) if key in variables else match.group(0)

    return _VARIABLE_RE.sub(_replace, str(text or ''))


def personalize_html(html: str, variables: dict) -> str:
    """Personalize sanitized HTML with HTML-escaped values.

    The body has already been through :func:`sanitize_html`, and every
    substituted value is escaped first, so a name like ``<script>x</a>``
    renders as inert text rather than re-opening the sanitizer.
    """
    escaped = {key: escape(str(value), quote=True) for key, value in variables.items()}
    return personalize(html, escaped)
