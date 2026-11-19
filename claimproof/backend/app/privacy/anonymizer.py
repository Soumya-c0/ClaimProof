from typing import Dict, Tuple
from presidio_analyzer import AnalyzerEngine

ENTITY_PREFIX = {
    "PERSON": "PERSON",
    "PHONE_NUMBER": "PHONE",
    "DATE_TIME": "DATE",
    "LOCATION": "ADDRESS",
    "IN_PAN": "ID",
    "US_SSN": "ID",
    "CREDIT_CARD": "ID",
}

analyzer = AnalyzerEngine()


def anonymize_text(text: str) -> Tuple[str, Dict[str, str], Dict[str, str]]:
    """
    Detects PII with Microsoft Presidio and replaces it with indexed tokens.
    Only the tokenized text is passed downstream to any LLM.
    """
    results = analyzer.analyze(
        text=text,
        entities=list(ENTITY_PREFIX.keys()),
        language="en",
    )

    
    results = sorted(results, key=lambda r: r.start, reverse=True)

    counts: Dict[str, int] = {}
    token_map: Dict[str, str] = {}
    tokenized_text = text

    for res in results:
        prefix = ENTITY_PREFIX.get(res.entity_type, "PII")
        counts[prefix] = counts.get(prefix, 0) + 1
        token = f"{prefix}_{counts[prefix]}"
        original_val = text[res.start:res.end]

        token_map[token] = original_val
        tokenized_text = tokenized_text[:res.start] + token + tokenized_text[res.end:]

    privacy_check = {
        "names": "tokenised",
        "phone_numbers": "tokenised",
        "addresses": "tokenised",
        "id_numbers": "tokenised",
    }

    return tokenized_text, token_map, privacy_check