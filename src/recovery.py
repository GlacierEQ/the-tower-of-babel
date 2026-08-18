"""Source-aware language transformation with explicit provenance."""
from dataclasses import dataclass

@dataclass(frozen=True)
class Translation:
    source: str
    output: str
    ruleset: str
    source_digest: str

    def receipt(self) -> dict[str, str]:
        return {'source': self.source, 'ruleset': self.ruleset, 'source_digest': self.source_digest}
