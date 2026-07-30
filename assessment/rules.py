"""Controlled runtime rule catalogue for the Validation Engine."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Iterable, Mapping

from assessment.models import (
    AssessmentDefinitionError,
    AssessmentTarget,
    RuleDefinition,
    RuleSource,
    RuleStatus,
)


class RuleCatalogError(AssessmentDefinitionError):
    """Invalid rule catalogue or unresolved requested rule."""


class RuleCatalog:
    """Immutable set of validated rule definitions loaded from JSON files."""

    def __init__(self, rules: Iterable[RuleDefinition]) -> None:
        ordered_rules = tuple(rules)
        by_id: dict[str, RuleDefinition] = {}

        for rule in ordered_rules:
            if rule.rule_id in by_id:
                raise RuleCatalogError(
                    "DUPLICATE_RULE_ID",
                    f"Duplicate rule ID found: {rule.rule_id}",
                )
            by_id[rule.rule_id] = rule

        if not ordered_rules:
            raise RuleCatalogError(
                "RULE_CATALOG_EMPTY",
                "Rule catalogue must contain at least one rule definition.",
            )

        self._rules = ordered_rules
        self._by_id = by_id

    @property
    def rules(self) -> tuple[RuleDefinition, ...]:
        return self._rules

    @property
    def rule_ids(self) -> frozenset[str]:
        return frozenset(self._by_id)

    def resolve(
        self,
        requested_rule_ids: Iterable[str],
        *,
        allowed_statuses: frozenset[RuleStatus],
    ) -> tuple[RuleDefinition, ...]:
        """Resolve requested IDs in request order and enforce lifecycle status."""

        resolved: list[RuleDefinition] = []

        for rule_id in requested_rule_ids:
            rule = self._by_id.get(rule_id)
            if rule is None:
                raise RuleCatalogError(
                    "UNKNOWN_RULE",
                    f"Requested rule is not present in the catalogue: {rule_id}",
                )

            if rule.status not in allowed_statuses:
                allowed = ", ".join(sorted(status.value for status in allowed_statuses))
                raise RuleCatalogError(
                    "RULE_STATUS_NOT_ALLOWED",
                    (
                        f"Rule {rule_id} has status {rule.status.value}, which is not "
                        f"allowed by this assessment request. Allowed: {allowed}."
                    ),
                )

            resolved.append(rule)

        return tuple(resolved)

    @classmethod
    def from_files(cls, *paths: str | Path) -> RuleCatalog:
        """Load, validate, and combine deterministic JSON rule files."""

        if not paths:
            raise RuleCatalogError(
                "RULE_CATALOG_NOT_CONFIGURED",
                "At least one rule catalogue file must be configured.",
            )

        rules: list[RuleDefinition] = []
        seen: dict[str, Path] = {}

        for raw_path in sorted((Path(path) for path in paths), key=lambda p: str(p)):
            try:
                with raw_path.open("r", encoding="utf-8") as rule_file:
                    payload = json.load(rule_file)
            except FileNotFoundError as exc:
                raise RuleCatalogError(
                    "RULE_CATALOG_FILE_NOT_FOUND",
                    f"Rule catalogue file does not exist: {raw_path}",
                ) from exc
            except json.JSONDecodeError as exc:
                raise RuleCatalogError(
                    "RULE_CATALOG_PARSE_ERROR",
                    f"Invalid JSON in rule catalogue {raw_path}: {exc}",
                ) from exc

            root = _require_mapping(payload, "rule catalogue root", raw_path)
            raw_rules = root.get("rules")
            if not isinstance(raw_rules, list):
                raise RuleCatalogError(
                    "MALFORMED_RULE_CATALOG",
                    f"Rule catalogue {raw_path} must contain a 'rules' list.",
                )

            for index, raw_rule in enumerate(raw_rules):
                rule = _parse_rule(raw_rule, path=raw_path, index=index)
                first_path = seen.get(rule.rule_id)
                if first_path is not None:
                    raise RuleCatalogError(
                        "DUPLICATE_RULE_ID",
                        (
                            f"Duplicate rule ID {rule.rule_id!r} found in "
                            f"{first_path} and {raw_path}."
                        ),
                    )
                seen[rule.rule_id] = raw_path
                rules.append(rule)

        return cls(rules)


def _parse_rule(
    raw_rule: Any,
    *,
    path: Path,
    index: int,
) -> RuleDefinition:
    location = f"{path} rule index {index}"
    try:
        data = _require_mapping(raw_rule, "rule", path)
        source_data = _require_mapping(data["source"], "rule source", path)

        return RuleDefinition(
            rule_id=_require_string(data["id"], "id", location),
            version=_require_string(data["version"], "version", location),
            status=RuleStatus(_require_string(data["status"], "status", location)),
            title=_require_string(data["title"], "title", location),
            evaluator_instruction=_require_string(
                data["evaluator_instruction"],
                "evaluator_instruction",
                location,
            ),
            applies_to_targets=frozenset(
                AssessmentTarget(target)
                for target in _require_string_list(
                    data["applies_to_targets"],
                    "applies_to_targets",
                    location,
                )
            ),
            required_evidence=frozenset(
                _require_string_list(
                    data["required_evidence"],
                    "required_evidence",
                    location,
                    allow_empty=True,
                )
            ),
            source=RuleSource(
                source_type=_require_string(
                    source_data["type"],
                    "source.type",
                    location,
                ),
                reference=_require_string(
                    source_data["reference"],
                    "source.reference",
                    location,
                ),
            ),
            forbidden_behaviours=tuple(
                _require_string_list(
                    data.get("forbidden_behaviours", []),
                    "forbidden_behaviours",
                    location,
                    allow_empty=True,
                )
            ),
            permitted_conclusions=tuple(
                _require_string_list(
                    data.get("permitted_conclusions", []),
                    "permitted_conclusions",
                    location,
                    allow_empty=True,
                )
            ),
        )
    except (KeyError, TypeError, ValueError) as exc:
        raise RuleCatalogError(
            "MALFORMED_RULE",
            f"Malformed rule at {location}: {exc}",
        ) from exc


def _require_mapping(value: Any, label: str, path: Path) -> Mapping[str, Any]:
    if not isinstance(value, dict):
        raise RuleCatalogError(
            "MALFORMED_RULE_CATALOG",
            f"{label.capitalize()} in {path} must be a JSON object.",
        )
    return value


def _require_string(value: Any, field_name: str, location: str) -> str:
    if not isinstance(value, str) or not value.strip():
        raise ValueError(f"{field_name} must be a non-empty string at {location}")
    return value.strip()


def _require_string_list(
    value: Any,
    field_name: str,
    location: str,
    *,
    allow_empty: bool = False,
) -> list[str]:
    if not isinstance(value, list):
        raise TypeError(f"{field_name} must be a list at {location}")
    if not allow_empty and not value:
        raise ValueError(f"{field_name} must not be empty at {location}")

    result = []
    for item in value:
        result.append(_require_string(item, field_name, location))
    return result
