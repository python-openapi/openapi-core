from dataclasses import dataclass
from typing import Dict
from typing import Optional


@dataclass
class TemplateResult:
    pattern: str
    variables: Optional[Dict[str, str]] = None

    @property
    def resolved(self) -> str:
        if not self.variables:
            return self.pattern
        return self.pattern.format(**self.variables)
