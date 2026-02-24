"""Email marketing module for Social Media Empire."""


def __getattr__(name):
    """Lazy imports to avoid requiring all dependencies at import time."""
    if name in ("EmailSender", "get_email_sender"):
        from .email_sender import EmailSender, get_email_sender
        return {"EmailSender": EmailSender, "get_email_sender": get_email_sender}[name]
    if name in ("ConvertKitAutomation", "EmailAutomationManager", "FORM_CONFIGS", "generate_form_html"):
        from .email_automation import (
            ConvertKitAutomation, EmailAutomationManager, FORM_CONFIGS, generate_form_html
        )
        return {
            "ConvertKitAutomation": ConvertKitAutomation,
            "EmailAutomationManager": EmailAutomationManager,
            "FORM_CONFIGS": FORM_CONFIGS,
            "generate_form_html": generate_form_html,
        }[name]
    if name in ("EMAIL_SEQUENCES", "get_sequence", "get_email", "preview_sequence"):
        from .sequences.welcome_sequences import (
            EMAIL_SEQUENCES, get_sequence, get_email, preview_sequence
        )
        return {
            "EMAIL_SEQUENCES": EMAIL_SEQUENCES,
            "get_sequence": get_sequence,
            "get_email": get_email,
            "preview_sequence": preview_sequence,
        }[name]
    raise AttributeError(f"module 'email_marketing' has no attribute {name}")


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
