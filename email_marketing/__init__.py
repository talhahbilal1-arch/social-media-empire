"""Email marketing module for Social Media Empire."""

from .email_sender import EmailSender, get_email_sender
from .email_automation import (
    ConvertKitAutomation,
    EmailAutomationManager,
    FORM_CONFIGS,
    generate_form_html
)

from .sequences.welcome_sequences import (
    EMAIL_SEQUENCES,
    get_sequence,
    get_email,
    preview_sequence
)

__all__ = [
    "EmailSender",
    "get_email_sender",
    "ConvertKitAutomation",
    "EmailAutomationManager",
    "FORM_CONFIGS",
    "generate_form_html",
    "EMAIL_SEQUENCES",
    "get_sequence",
    "get_email",
    "preview_sequence"
]
