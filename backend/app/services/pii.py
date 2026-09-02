# Mock PII Guardian for Hackathon Demo
def count_pii_entities(text: str) -> int:
    """
    Very basic PII counter for demo purposes.
    """
    # Simply simulate PII detection for the demo
    return 7 if "Arun" in text or "Kumar" in text else 0
