"""Versioned report and configuration contracts."""

from enum import StrEnum

from pydantic import BaseModel, ConfigDict, Field


class Status(StrEnum):
    PASS = "PASS"
    INFO = "INFO"
    WARNING = "WARNING"
    FAIL = "FAIL"
    SKIPPED = "SKIPPED"


class Category(StrEnum):
    RUNTIME = "runtime"
    DEPENDENCIES = "dependencies"
    CONFIGURATION = "configuration"
    SECURITY = "security"
    TESTING = "testing"
    CI = "ci"
    DEPLOYMENT = "deployment"
    INTEGRATION = "integration"
    OBSERVABILITY = "observability"
    REPOSITORY = "repository"


class Check(BaseModel):
    id: str
    name: str
    category: Category
    status: Status
    severity: str
    description: str
    evidence: list[str] = Field(default_factory=list)
    recommendation: str
    score_impact: int = Field(default=0, ge=0)


class Stack(BaseModel):
    languages: list[str] = Field(default_factory=list)
    frameworks: list[str] = Field(default_factory=list)
    package_managers: list[str] = Field(default_factory=list)
    runtimes: dict[str, str] = Field(default_factory=dict)
    docker: list[str] = Field(default_factory=list)
    ci: list[str] = Field(default_factory=list)
    deployment: list[str] = Field(default_factory=list)


class Report(BaseModel):
    schema_version: str = "1.0"
    tool_version: str = "0.1.0"
    project: str
    stack: Stack
    checks: list[Check]
    score: int = Field(ge=0, le=100)
    scoring_model: str = "v1: max(0, 100 - sum(score_impact)); see docs/SCORING.md"
    limitations: list[str] = Field(
        default_factory=lambda: [
            "Static heuristics only; presence does not prove correct or working configuration.",
            "No network calls, dependency installation, project execution, or Git history scan.",
            "No security guarantee. Exclusions and read limits can hide risks.",
        ]
    )


class Config(BaseModel):
    model_config = ConfigDict(extra="forbid", strict=True)
    schema_version: int = Field(default=1, ge=1, le=1)
    exclude: list[str] = Field(default_factory=lambda: ["tests/fixtures", "examples"])
    max_file_bytes: int = Field(default=262144, ge=1024, le=2097152)
    max_files: int = Field(default=10000, ge=1, le=100000)
    max_total_bytes: int = Field(default=16777216, ge=1024, le=134217728)
    required_env: list[str] = Field(default_factory=list)
    min_score: int = Field(default=70, ge=0, le=100)
