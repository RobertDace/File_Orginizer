import os
import json
import shutil
import datetime
from pathlib import Path
from typing import List, Dict, Any, Optional

JOURNAL_FILENAME = ".file_organizer_journal.json"


class TransactionManager:
    """
    Manages transaction batches and history to allow 100% reliable 1-click Undo.
    The journal is stored in the target base directory.
    """

    def __init__(self, base_dir: str):
        self.base_dir = Path(base_dir).resolve()
        self.journal_path = self.base_dir / JOURNAL_FILENAME

    def _load_history(self) -> List[Dict[str, Any]]:
        """Load history list from disk if present."""
        if not self.journal_path.exists():
            return []
        try:
            with open(self.journal_path, "r", encoding="utf-8") as f:
                data = json.load(f)
                return data if isinstance(data, list) else []
        except Exception:
            return []

    def _save_history(self, history: List[Dict[str, Any]]) -> None:
        """Atomically save history to journal file."""
        tmp_path = self.journal_path.with_suffix(".tmp")
        try:
            with open(tmp_path, "w", encoding="utf-8") as f:
                json.dump(history, f, indent=2, ensure_ascii=False)
            if self.journal_path.exists():
                self.journal_path.unlink()
            tmp_path.rename(self.journal_path)
        except Exception as e:
            if tmp_path.exists():
                try:
                    tmp_path.unlink()
                except Exception:
                    pass
            raise e

    def record_batch(self, moves: List[Dict[str, str]], description: str = "") -> str:
        """
        Record a successful batch of file movements.
        Each move dict: {"src": original_path, "dst": new_path}
        Returns the batch ID.
        """
        history = self._load_history()
        batch_id = datetime.datetime.now().strftime("BATCH_%Y%m%d_%H%M%S")
        batch_entry = {
            "batch_id": batch_id,
            "timestamp": datetime.datetime.now().isoformat(),
            "count": len(moves),
            "description": description,
            "moves": moves
        }
        history.append(batch_entry)
        self._save_history(history)
        return batch_id

    def get_last_batch(self) -> Optional[Dict[str, Any]]:
        """Return the most recent batch entry, or None if no history exists."""
        history = self._load_history()
        if not history:
            return None
        return history[-1]

    def can_undo(self) -> bool:
        """Check if there is at least one recorded batch that can be undone."""
        return len(self._load_history()) > 0

    def rollback_last_batch(self) -> Dict[str, Any]:
        """
        Revert the most recent batch:
        Moves files back from dst to src, restores directories, and cleans up empty created folders.
        Returns report: {"reverted": int, "failed": int, "errors": list}
        """
        history = self._load_history()
        if not history:
            return {"reverted": 0, "failed": 0, "errors": ["No transaction history available to undo."]}

        last_batch = history.pop()
        moves = last_batch.get("moves", [])
        
        reverted = 0
        failed = 0
        errors = []
        affected_dirs = set()

        # Execute reverse moves
        for move in reversed(moves):
            src_orig = move.get("src")
            dst_curr = move.get("dst")

            if not src_orig or not dst_curr:
                continue

            if not os.path.exists(dst_curr):
                failed += 1
                errors.append(f"File not found at target: {dst_curr}")
                continue

            # Ensure original directory exists
            orig_dir = os.path.dirname(src_orig)
            os.makedirs(orig_dir, exist_ok=True)

            try:
                # If destination already has a file with the original name, handle safely
                final_restore_path = src_orig
                if os.path.exists(final_restore_path) and os.path.abspath(final_restore_path) != os.path.abspath(dst_curr):
                    stem = Path(src_orig).stem
                    suffix = Path(src_orig).suffix
                    counter = 1
                    while os.path.exists(final_restore_path):
                        final_restore_path = os.path.join(orig_dir, f"{stem}_restored_{counter}{suffix}")
                        counter += 1

                shutil.move(dst_curr, final_restore_path)
                reverted += 1
                affected_dirs.add(os.path.dirname(dst_curr))
            except Exception as e:
                failed += 1
                errors.append(f"Error reverting {dst_curr} -> {src_orig}: {str(e)}")

        # Clean up empty parent directories if any were left behind
        for folder in affected_dirs:
            try:
                if os.path.exists(folder) and not os.listdir(folder):
                    os.rmdir(folder)
            except Exception:
                pass

        # Update remaining history on disk
        self._save_history(history)

        return {
            "batch_id": last_batch.get("batch_id"),
            "reverted": reverted,
            "failed": failed,
            "errors": errors
        }
