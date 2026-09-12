from __future__ import annotations

from datetime import datetime, timezone
from typing import Any, Dict, List, Optional

from pydantic import BaseModel, Field


def utcnow() -> str:
    return datetime.now(timezone.utc).isoformat()


class Item(BaseModel):
    row_id: str
    fields: Dict[str, Any] = Field(default_factory=dict)


class Normalized(BaseModel):
    fields: Dict[str, Any] = Field(default_factory=dict)
    quarantined: bool = False
    issues: List[str] = Field(default_factory=list)


class ContextPackage(BaseModel):
    history: List[Dict[str, Any]] = Field(default_factory=list)
    metadata: Dict[str, Any] = Field(default_factory=dict)
    token_budget: Optional[int] = None
    truncation_log: List[str] = Field(default_factory=list)


class Evidence(BaseModel):
    doc_id: str
    score: float
    same_user: bool = True
    source: str = ""
    snippet: str = ""
    timestamp: Optional[str] = None


class FeatureSet(BaseModel):
    signals: Dict[str, Any] = Field(default_factory=dict)


class Perception(BaseModel):
    provider: str = "none"
    structured: Dict[str, Any] = Field(default_factory=dict)
    raw: Dict[str, Any] = Field(default_factory=dict)


class Decision(BaseModel):
    label: str
    reason: str = ""
    rule_fired: str = ""
    is_fallback: bool = False


class Confidence(BaseModel):
    score: float = 0.0
    band: str = "none"
    basis: str = ""


class ValidationResult(BaseModel):
    ok: bool = True
    errors: List[str] = Field(default_factory=list)
    checks: Dict[str, Any] = Field(default_factory=dict)


class OutputRow(BaseModel):
    row_id: str
    columns: Dict[str, Any] = Field(default_factory=dict)


class TraceEvent(BaseModel):
    stage: str
    plugin: str
    version: str
    time_ms: float
    detail: Dict[str, Any] = Field(default_factory=dict)


class ExecutionContext(BaseModel):
    item: Optional[Item] = None
    normalized: Optional[Normalized] = Field(default_factory=Normalized)
    context: ContextPackage = Field(default_factory=ContextPackage)
    evidence: List[Evidence] = Field(default_factory=list)
    features: FeatureSet = Field(default_factory=FeatureSet)
    perception: Perception = Field(default_factory=Perception)
    decision: Optional[Decision] = None
    confidence: Confidence = Field(default_factory=Confidence)
    validation: ValidationResult = Field(default_factory=ValidationResult)
    trace: List[TraceEvent] = Field(default_factory=list)
    output_row: Optional[OutputRow] = None
    aborted: bool = False
    abort_reason: str = ""

    def add_trace(self, stage: str, plugin: str, version: str, time_ms: float, detail: Dict[str, Any]) -> None:
        self.trace.append(
            TraceEvent(stage=stage, plugin=plugin, version=version, time_ms=time_ms, detail=detail)
        )