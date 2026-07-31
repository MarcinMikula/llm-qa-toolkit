"""Transport-neutral ports for examinee and evaluator roles."""

from __future__ import annotations

from typing import Protocol

from assessment.models import (
    BoundedEvaluatorRequest,
    CandidateResponse,
    ExamineeRequest,
    ProposedEvaluatorResult,
)


class ExamineePort(Protocol):
    """Returns a normalised response from a system under evaluation."""

    def respond(self, request: ExamineeRequest) -> CandidateResponse:
        """Submit a stimulus and return a normalised candidate response."""


class EvaluatorPort(Protocol):
    """Returns proposed findings for deterministic downstream validation."""

    def evaluate(
        self,
        request: BoundedEvaluatorRequest,
    ) -> ProposedEvaluatorResult:
        """Evaluate only within the supplied bounded evaluator request."""
