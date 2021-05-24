from typing import Dict, Optional

from dataclasses import dataclass


@dataclass
class TemplateResult:
    pattern: Optional[str] = None
    variables: Optional[Dict] = None

    @property
    def resolved(self):
        if not self.variables:
            return self.pattern
        return self.pattern.format(**self.variables)
