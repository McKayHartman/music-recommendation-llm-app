from dataclasses import dataclass, field
from typing import Any, Dict


@dataclass
class Document:
    id: str
    description: str
    metadata: Dict[str, Any] = field(default_factory=dict)

    def get_id(self) -> str:
        return str(self.id)

    def get_description(self) -> str:
        return self.description

    def get_metadata(self) -> Dict[str, Any]:
        return self.metadata

    def set_id(self, id: str) -> None:
        self.id = str(id)

    def set_description(self, description: str) -> None:
        self.description = description

    def set_metadata(self, metadata: Dict[str, Any]) -> None:
        self.metadata = metadata
