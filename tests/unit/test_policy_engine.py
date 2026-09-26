from vibeguard.policies.engine import (
    Action,
    PolicyConfig,
    PolicyEngine,
    PolicyRequest,
)


def engine() -> PolicyEngine:
    return PolicyEngine(
        PolicyConfig(
            allowed_repositories=frozenset(
                {"MAI-AMAN/vibeguard-demo-python"}
            )
        )
    )


def test_unapproved_write_is_rejected():
    result = engine().evaluate(
        PolicyRequest(
            repository="MAI-AMAN/vibeguard-demo-python",
            action=Action.COMMIT_FILES,
        )
    )

    assert not result.allowed
    assert "approval" in result.reason


def test_unapproved_merge_is_rejected():
    result = engine().evaluate(
        PolicyRequest(
            repository="MAI-AMAN/vibeguard-demo-python",
            action=Action.MERGE_PR,
        )
    )

    assert not result.allowed


def test_allowlisted_approved_write_is_allowed():
    result = engine().evaluate(
        PolicyRequest(
            repository="MAI-AMAN/vibeguard-demo-python",
            action=Action.COMMIT_FILES,
            base_sha="abc123",
            approved_base_sha="abc123",
            changed_files=("src/demo/metrics.py", "tests/test_metrics.py"),
            diff_lines=20,
            approval_valid=True,
        )
    )

    assert result.allowed


def test_wrong_base_sha_is_rejected():
    result = engine().evaluate(
        PolicyRequest(
            repository="MAI-AMAN/vibeguard-demo-python",
            action=Action.COMMIT_FILES,
            base_sha="new-sha",
            approved_base_sha="old-sha",
            approval_valid=True,
        )
    )

    assert not result.allowed
    assert "SHA" in result.reason


def test_too_many_files_are_rejected():
    files = tuple(f"src/file{i}.py" for i in range(6))

    result = engine().evaluate(
        PolicyRequest(
            repository="MAI-AMAN/vibeguard-demo-python",
            action=Action.COMMIT_FILES,
            changed_files=files,
            approval_valid=True,
        )
    )

    assert not result.allowed


def test_large_diff_is_rejected():
    result = engine().evaluate(
        PolicyRequest(
            repository="MAI-AMAN/vibeguard-demo-python",
            action=Action.COMMIT_FILES,
            diff_lines=251,
            approval_valid=True,
        )
    )

    assert not result.allowed


def test_forbidden_workflow_file_is_rejected():
    result = engine().evaluate(
        PolicyRequest(
            repository="MAI-AMAN/vibeguard-demo-python",
            action=Action.COMMIT_FILES,
            changed_files=(".github/workflows/ci.yml",),
            approval_valid=True,
        )
    )

    assert not result.allowed


def test_non_allowlisted_repository_is_rejected():
    result = engine().evaluate(
        PolicyRequest(
            repository="someone/other-repo",
            action=Action.COMMIT_FILES,
            approval_valid=True,
        )
    )

    assert not result.allowed
    assert "allowlisted" in result.reason
