"""Git branch name validators."""
import re
from typing import List
from dataclasses import dataclass


@dataclass
class ValidationResult:
    """Result of branch name validation."""
    is_valid: bool
    branch: str
    errors: List[str]
    warnings: List[str] = None

    def __post_init__(self):
        if self.warnings is None:
            self.warnings = []


def validate_branch_name(branch: str) -> ValidationResult:
    """
    Validate Git branch name against project conventions.

    Args:
        branch: Branch name to validate

    Returns:
        ValidationResult with is_valid, branch, and errors
    """
    errors = []

    # Pattern: NNN-feature-name or fix-description or master/main
    if branch in ['master', 'main', 'develop']:
        return ValidationResult(is_valid=True, branch=branch, errors=[], warnings=[])

    # Feature branch: NNN-feature-name
    feature_pattern = r'^\d{3}-[a-z0-9-]+$'
    # Fix branch: fix-description
    fix_pattern = r'^fix-[a-z0-9-]+$'

    if not (re.match(feature_pattern, branch) or re.match(fix_pattern, branch)):
        errors.append(
            f"Branch name '{branch}' doesn't match conventions: "
            "NNN-feature-name or fix-description"
        )

    return ValidationResult(
        is_valid=len(errors) == 0,
        branch=branch,
        errors=errors,
        warnings=[]
    )


def format_validation_errors(validation: ValidationResult) -> str:
    """
    Format validation errors for display.

    Args:
        validation: Validation result from validate_branch_name

    Returns:
        Formatted error message string
    """
    if validation.is_valid:
        return ""

    if not validation.errors:
        return ""

    return "\n".join(f"❌ {err}" for err in validation.errors)
