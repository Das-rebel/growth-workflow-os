"""Base signal model and collector interface."""

from datetime import datetime
from typing import Optional
from pydantic import BaseModel, Field, ConfigDict
from abc import ABC, abstractmethod


class Signal(BaseModel):
    """A single market or operational signal.

    Signals are the atomic unit of intelligence in this system.
    They flow through the pipeline: collect → interpret → infer → memorize.
    """

    text: str = Field(..., description="The raw signal content")
    source: str = Field(..., description="Where this signal came from")
    category: str = Field(default="manual_observation", description="Signal category")
    url: Optional[str] = Field(None, description="Original URL if applicable")
    collected_at: datetime = Field(default_factory=datetime.utcnow)
    metadata: dict = Field(default_factory=dict, description="Additional context")

    # Populated after interpretation
    interpretation: Optional[str] = None
    strategic_weight: Optional[float] = None
    tags: list[str] = Field(default_factory=list)
    id: Optional[int] = Field(None, description="Database ID, set after storage")

    model_config = ConfigDict(
        arbitrary_types_allowed=True,
        json_schema_extra={
            "example": {
                "text": "Stripe launches AI-powered revenue recovery agent",
                "source": "techcrunch",
                "category": "product_launch",
                "url": "https://techcrunch.com/...",
                "tags": ["fintech", "ai_agents", "revenue_ops"],
            }
        },
    )


class SignalCollector(ABC):
    """Base class for signal collectors."""

    @abstractmethod
    def collect(self, **kwargs) -> list[Signal]:
        """Collect signals from this source.

        Returns:
            List of Signal objects
        """
        pass

    @abstractmethod
    def source_name(self) -> str:
        """Return the name of this collector's source."""
        pass
