import re

def count_pii_entities(text: str) -> int:
    """
    Counts potential PII entities (phone numbers, emails, dates of birth, national IDs) in text using regex matching.
    """
    if not text:
        return 0
    
    count = 0
    # Phone numbers
    count += len(re.findall(r'\b(?:\+?\d{1,3}[-.\s]?)?\(?\d{3}\)?[-.\s]?\d{3}[-.\s]?\d{4}\b', text))
    # Emails
    count += len(re.findall(r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b', text))
    # Dates / DOBs
    count += len(re.findall(r'\b(?:\d{1,2}[/-]\d{1,2}[/-]\d{2,4}|\d{4}[/-]\d{1,2}[/-]\d{1,2})\b', text))
    # SSN / Government IDs
    count += len(re.findall(r'\b\d{3}-\d{2}-\d{4}\b', text))
    
    return count
