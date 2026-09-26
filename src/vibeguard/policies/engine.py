class PolicyEngine:
    def __init__(self, config: PolicyConfig) -> None:
        self.config = config

    def evaluate(self, request: PolicyRequest) -> PolicyDecision:
        if request.repository not in self.config.allowed_repositories:
            return PolicyDecision(False, "repository is not allowlisted")

        if request.action in {
            Action.CREATE_BRANCH,
            Action.COMMIT_FILES,
            Action.OPEN_DRAFT_PR,
        } and not request.approval_valid:
            return PolicyDecision(False, "valid fix approval is required")

        if request.action is Action.MERGE_PR and not request.approval_valid:
            return PolicyDecision(False, "valid ship approval is required")

        if (
            request.approved_base_sha is not None
            and request.base_sha != request.approved_base_sha
        ):
            return PolicyDecision(False, "base SHA does not match approved SHA")

        if len(request.changed_files) > self.config.max_changed_files:
            return PolicyDecision(False, "too many changed files")

        if request.diff_lines > self.config.max_diff_lines:
            return PolicyDecision(False, "diff exceeds configured limit")

        for path in request.changed_files:
            if self._is_forbidden_path(path):
                return PolicyDecision(
                    False,
                    f"forbidden path: {path}",
                )

        return PolicyDecision(True, "policy checks passed")

    @staticmethod
    def _is_forbidden_path(path: str) -> bool:
        normalized = path.lstrip("./")

        if normalized.startswith(".github/workflows/"):
            return True

        for pattern in FORBIDDEN_PATHS:
            if fnmatch(normalized, pattern):
                return True

        return False
