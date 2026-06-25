from __future__ import annotations

from collections import deque
from dataclasses import dataclass, field
from typing import Protocol


class GameAction(Protocol):
    name: str

    def execute(self, combat: "CombatSystem") -> None:
        ...


@dataclass
class ActionQueue:
    """戦闘中の効果解決順を管理する同期Action Queue。"""

    max_actions_per_resolution: int = 1000
    _queue: deque[GameAction] = field(default_factory=deque, init=False)
    is_resolving: bool = False

    def add(self, action: GameAction) -> None:
        self._queue.append(action)

    def add_front(self, action: GameAction) -> None:
        self._queue.appendleft(action)

    def extend(self, actions: list[GameAction]) -> None:
        self._queue.extend(actions)

    def clear(self) -> None:
        self._queue.clear()

    def has_pending(self) -> bool:
        return bool(self._queue)

    def resolve_all(self, combat: "CombatSystem") -> None:
        if self.is_resolving:
            return

        self.is_resolving = True
        resolved_count = 0
        try:
            while self._queue:
                if combat.state.pending_selection is not None:
                    break

                resolved_count += 1
                if resolved_count > self.max_actions_per_resolution:
                    combat.log("ActionQueue safety stop")
                    self.clear()
                    break

                action = self._queue.popleft()
                action.execute(combat)

                if combat.state.outcome == "defeat":
                    self.clear()
                    break
        finally:
            self.is_resolving = False
