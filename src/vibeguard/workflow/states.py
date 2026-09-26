from enum import StrEnum


class State(StrEnum):
    RECEIVED = "received"
    GATHERING_CONTEXT = "gathering_context"
    ANALYZED = "analyzed"
    REPRODUCING = "reproducing"
    REPRODUCED = "reproduced"
    PROPOSED = "proposed"
    AWAITING_APPROVAL = "awaiting_approval"
    EXECUTING = "executing"
    VERIFYING = "verifying"
    AWAITING_SHIP_APPROVAL = "awaiting_ship_approval"
    SHIPPING = "shipping"
    COMPLETED = "completed"

    NEEDS_MORE_INFORMATION = "needs_more_information"
    DENIED = "denied"
    FAILED = "failed"


TERMINAL_STATES = {
    State.COMPLETED,
    State.NEEDS_MORE_INFORMATION,
    State.DENIED,
    State.FAILED,
}


TRANSITIONS: dict[State, set[State]] = {
    State.RECEIVED: {
        State.GATHERING_CONTEXT,
        State.NEEDS_MORE_INFORMATION,
        State.FAILED,
    },
    State.GATHERING_CONTEXT: {
        State.ANALYZED,
        State.NEEDS_MORE_INFORMATION,
        State.FAILED,
    },
    State.ANALYZED: {
        State.REPRODUCING,
        State.NEEDS_MORE_INFORMATION,
        State.FAILED,
    },
    State.REPRODUCING: {
        State.REPRODUCED,
        State.NEEDS_MORE_INFORMATION,
        State.FAILED,
    },
    State.REPRODUCED: {
        State.PROPOSED,
        State.NEEDS_MORE_INFORMATION,
        State.FAILED,
    },
    State.PROPOSED: {
        State.AWAITING_APPROVAL,
        State.NEEDS_MORE_INFORMATION,
        State.FAILED,
    },
    State.AWAITING_APPROVAL: {
        State.EXECUTING,
        State.DENIED,
        State.FAILED,
    },
    State.EXECUTING: {
        State.VERIFYING,
        State.FAILED,
    },
    State.VERIFYING: {
        State.AWAITING_SHIP_APPROVAL,
        State.FAILED,
    },
    State.AWAITING_SHIP_APPROVAL: {
        State.SHIPPING,
        State.DENIED,
        State.FAILED,
    },
    State.SHIPPING: {
        State.COMPLETED,
        State.FAILED,
    },
    State.COMPLETED: set(),
    State.NEEDS_MORE_INFORMATION: set(),
    State.DENIED: set(),
    State.FAILED: set(),
}


def can_transition(current: State, target: State) -> bool:
    """Return whether a state transition is explicitly allowed."""
    return target in TRANSITIONS[current]


def transition(current: State, target: State) -> State:
    """Perform a validated state transition."""
    if not can_transition(current, target):
        raise ValueError(
            f"Illegal VibeGuard transition: {current.value} -> {target.value}"
        )

    return target
