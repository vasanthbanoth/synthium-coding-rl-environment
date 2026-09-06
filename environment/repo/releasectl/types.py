from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


@dataclass
class Decision:
    ship: bool
    reasons: list[str] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        return {"ship": self.ship, "reasons": list(self.reasons)}
