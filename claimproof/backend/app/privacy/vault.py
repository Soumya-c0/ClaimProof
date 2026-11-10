import uuid
from typing import Dict

class TokenVault:
    def __init__(self):
        # In-memory vault for the hackathon MVP. 
        # For production, this maps to an encrypted PostgreSQL table.
        self.token_to_raw: Dict[str, str] = {}
        self.raw_to_token: Dict[str, str] = {}
        self.counters: Dict[str, int] = {}

    def get_or_create_token(self, entity_type: str, raw_text: str) -> str:
        if raw_text in self.raw_to_token:
            return self.raw_to_token[raw_text]
        
        count = self.counters.get(entity_type, 0) + 1
        self.counters[entity_type] = count
        
        token = f"[{entity_type}_{count}]"
        
        self.token_to_raw[token] = raw_text
        self.raw_to_token[raw_text] = token
        
        return token

    def restore(self, text: str) -> str:
        restored_text = text
        for token, raw in self.token_to_raw.items():
            restored_text = restored_text.replace(token, raw)
        return restored_text

# Singleton instance for the app
vault = TokenVault()