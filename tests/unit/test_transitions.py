import pytest

from vibeguard.workflow.states import (
    State,
    can_transition,
    transition,
)


def test_happy_path_transitions_are_allowed():
    path = [
        State.RECEIVED,
        State.GATHERING_CONTEXT,
        State.ANALYZED,
        State.REPRODUCING,
        State.REPRODUCED,
        State.PROPOSED,
        State.AWAITING_APPROVAL,
        State.EXECUTING,
        State.VERIFYING,
        State.AWAITING_SHIP_APPROVAL,
        State.SHIPPING,
        State.COMPLETED,
    ]

    for current, target in zip(path, path[1:]):
        assert can_transition(current, target)
        assert transition(current, target) == target


def test_write_cannot_happen_before_first_approval():
    assert not can_transition(
        State.PROPOSED,
        State.EXECUTING,
    )


def test_merge_cannot_happen_before_second_approval():
    assert not can_transition(
        State.VERIFYING,
        State.SHIPPING,
    )


def test_invalid_transition_raises():
    with pytest.raises(ValueError):
        transition(State.RECEIVED, State.SHIPPING)


def test_terminal_states_cannot_transition():
    for state in (
        State.COMPLETED,
        State.DENIED,
        State.FAILED,
        State.NEEDS_MORE_INFORMATION,
    ):
        assert not any(
            can_transition(state, target)
            for target in State
        )
