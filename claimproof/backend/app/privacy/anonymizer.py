import os
from typing import Dict, Tuple
from presidio_analyzer import AnalyzerEngine
from presidio_analyzer.nlp_engine import NlpEngineProvider

ENTITY_PREFIX = {
    "PERSON": "PERSON",
    "PHONE_NUMBER": "PHONE",
    "DATE_TIME": "DATE",
    "LOCATION": "ADDRESS",
    "IN_PAN": "ID",
    "US_SSN": "ID",
    "CREDIT_CARD": "ID",
}

def _build_analyzer() -> AnalyzerEngine:
    """Default: Presidio's standard (large) spaCy model.
    Set CLAIMPROOF_SPACY_MODEL=en_core_web_sm to use a small model on low-memory hosts."""
    model = os.getenv("CLAIMPROOF_SPACY_MODEL")
    if not model:
        return AnalyzerEngine()
    import spacy
    try:
        spacy.load(model)
    except OSError:
        from spacy.cli import download
        download(model)
    provider = NlpEngineProvider(
        nlp_configuration={"nlp_engine_name": "spacy", "models": [{"lang_code": "en", "model_name": model}]}
    )
    return AnalyzerEngine(nlp_engine=provider.create_engine(), supported_languages=["en"])


analyzer = _build_analyzer()


def _drop_overlaps(results):
    """Keep the longest span when detections overlap (e.g. a phone number also read as a date)."""
    kept = []
    for r in sorted(results, key=lambda r: (-(r.end - r.start), -r.score)):
        if all(r.end <= k.start or r.start >= k.end for k in kept):
            kept.append(r)
    return kept


def anonymize_text(text: str, doc_type: str = "claim") -> Tuple[str, Dict[str, str], Dict[str, str]]:
    """
    Detects PII with Microsoft Presidio and replaces it with indexed tokens.
    Only the tokenized text is passed downstream to any LLM.
    """
    entities = list(ENTITY_PREFIX.keys())
    if doc_type == "policy":
        # Policy wording has no personal data; keep "30 days" and place names intact for rule extraction.
        entities = [e for e in entities if e not in ("DATE_TIME", "LOCATION")]
    results = analyzer.analyze(text=text, entities=entities, language="en")
    results = _drop_overlaps(results)

    
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