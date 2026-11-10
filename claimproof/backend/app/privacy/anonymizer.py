from presidio_analyzer import AnalyzerEngine
from presidio_anonymizer import AnonymizerEngine
from app.privacy.vault import vault

# Initialize Presidio engines
analyzer = AnalyzerEngine()
anonymizer = AnonymizerEngine()

def protect_text(text: str) -> str:
    """Detects PII and replaces it with tokens from the local vault."""
    if not text:
        return ""

    # Detect entities (Names, Phones, Emails, Locations, etc.)
    results = analyzer.analyze(text=text, entities=[], language='en')
    
    # Sort results in reverse order to avoid index shifting during replacement
    results = sorted(results, key=lambda x: x.start, reverse=True)
    
    protected_text = text
    for result in results:
        raw_entity = text[result.start:result.end]
        token = vault.get_or_create_token(result.entity_type, raw_entity)
        
        # Replace the raw text with the token
        protected_text = protected_text[:result.start] + token + protected_text[result.end:]
        
    return protected_text