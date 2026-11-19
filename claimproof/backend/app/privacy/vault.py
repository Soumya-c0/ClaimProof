import json
from pathlib import Path
from typing import Dict

VAULT_PATH = Path("local_token_vault.json")


class LocalTokenVault:
    """Stores PII token mappings locally. Never transmitted to external LLMs."""

    def __init__(self, path: Path = VAULT_PATH):
        self.path = path
        self._store: Dict[str, Dict[str, str]] = self._load()

    def _load(self) -> Dict[str, Dict[str, str]]:
        if self.path.exists():
            return json.loads(self.path.read_text(encoding="utf-8"))
        return {}

    def _save(self) -> None:
        self.path.write_text(json.dumps(self._store, indent=2), encoding="utf-8")

    def save_map(self, doc_id: str, token_map: Dict[str, str]) -> None:
        self._store[doc_id] = token_map
        self._save()

    def get_map(self, doc_id: str) -> Dict[str, str]:
        return self._store.get(doc_id, {})

    def detokenize(self, doc_id: str, text: str) -> str:
        """Restores raw identifiers locally after the model call."""
        token_map = self.get_map(doc_id)
        for token, original in token_map.items():
            text = text.replace(token, original)
        return text


vault = LocalTokenVault()