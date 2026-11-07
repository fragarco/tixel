"""
In-memory undo/redo history for Tixel.

Stores project snapshots on an undo stack and rewinds/replays them
one logical edit at a time.

This program is free software; you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation in its version 3.

This program is distributed in the hope that it will be useful
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program; if not, write to the Free Software
Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA  02111-1307 USA
"""

from typing import Any
from constants import UNDO_LIMIT

Snapshot = dict[str, Any]

class History:
    """
    Bounded undo/redo stack pair (runtime-only; never persisted).
    """

    def __init__(self, limit: int = UNDO_LIMIT) -> None:
        self.limit: int = max(1, limit)
        self._undo: list[Snapshot] = []
        self._redo: list[Snapshot] = []

    @property
    def can_undo(self) -> bool:
        return bool(self._undo)

    @property
    def can_redo(self) -> bool:
        return bool(self._redo)

    def reset(self) -> None:
        """
        Forget all history (New/Open project).
        """
        self._undo.clear()
        self._redo.clear()

    def record(self, snapshot: Snapshot) -> None:
        """
        Call with the state BEFORE a logical edit is applied.
        """
        self._undo.append(snapshot)
        if len(self._undo) > self.limit:
            self._undo.pop(0)
        self._redo.clear()

    def undo(self, current: Snapshot) -> Snapshot | None:
        """
        Give back the state before the last edit; `current` goes to redo.
        """
        if not self._undo:
            return None
        self._redo.append(current)
        return self._undo.pop()

    def redo(self, current: Snapshot) -> Snapshot | None:
        """
        Re-apply the last undone edit; `current` goes back to undo.
        """
        if not self._redo:
            return None
        self._undo.append(current)
        return self._redo.pop()
