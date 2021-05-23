from typing import Dict

from dataclasses import dataclass, field


@dataclass
class TemplateResult:
    pattern: str
    variables: Dict = field(default_factory=dict)

    @property
    def resolved(self):
        if not self.variables:
            return self.pattern
        return self.pattern.format(**self.variables)
