import os
import shutil
from pathlib import Path
from typing import List, Dict, Any, Callable, Optional, Tuple
from core.transaction import TransactionManager


class OrganizerEngine:
    """
    Executes file organization operations safely with collision resolution,
    progress tracking, and transaction journaling.
    """

    def __init__(self, base_dir: str):
        self.base_dir = Path(base_dir).resolve()
        self.tx_manager = TransactionManager(str(self.base_dir))

    @staticmethod
    def get_unique_filename(target_path: str) -> str:
        """Generate non-colliding file path with incremental suffix: name_1.ext"""
        if not os.path.exists(target_path):
            return target_path

        p = Path(target_path)
        parent = p.parent
        stem = p.stem
        suffix = p.suffix

        counter = 1
        while True:
            candidate = parent / f"{stem}_{counter}{suffix}"
            if not candidate.exists():
                return str(candidate)
            counter += 1

    def execute_batch(
        self,
        items: List[Dict[str, Any]],
        collision_policy: str = "ask",
        collision_callback: Optional[Callable[[str, str], Tuple[str, bool]]] = None,
        progress_callback: Optional[Callable[[int, int, str], None]] = None
    ) -> Dict[str, Any]:
        """
        Execute moving files according to items list.
        
        collision_policy:
          - "ask": invoke collision_callback if target exists
          - "auto_rename": automatically generate unique name
          - "skip": skip conflicting files
          - "replace": overwrite target file
        
        Returns summary report.
        """
        total = len(items)
        moved_count = 0
        skipped_count = 0
        error_count = 0
        moves_record: List[Dict[str, str]] = []
        errors: List[str] = []

        cached_apply_all_action: Optional[str] = None

        for idx, item in enumerate(items):
            src = item["src_path"]
            dst = item["target_path"]
            target_dir = item["target_dir"]

            if progress_callback:
                progress_callback(idx + 1, total, item["name"])

            if not os.path.exists(src):
                error_count += 1
                errors.append(f"Source file disappeared: {src}")
                item["status"] = "MISSING"
                continue

            # Ensure destination folder exists
            os.makedirs(target_dir, exist_ok=True)

            final_dst = dst
            action_to_take = collision_policy

            # Check collision
            if os.path.exists(dst) and os.path.abspath(src) != os.path.abspath(dst):
                if cached_apply_all_action:
                    action_to_take = cached_apply_all_action
                elif collision_policy == "ask" and collision_callback:
                    chosen_action, apply_all = collision_callback(src, dst)
                    action_to_take = chosen_action
                    if apply_all:
                        cached_apply_all_action = chosen_action
                elif collision_policy == "ask":
                    action_to_take = "auto_rename"

                if action_to_take == "skip":
                    skipped_count += 1
                    item["status"] = "SKIPPED"
                    continue
                elif action_to_take == "replace":
                    final_dst = dst
                else:  # Default / auto_rename
                    final_dst = self.get_unique_filename(dst)

            # Check if source and final destination are identical
            if os.path.abspath(src) == os.path.abspath(final_dst):
                skipped_count += 1
                item["status"] = "ALREADY_ORGANIZED"
                continue

            try:
                shutil.move(src, final_dst)
                moved_count += 1
                item["status"] = "MOVED"
                item["final_dst"] = final_dst
                moves_record.append({"src": src, "dst": final_dst})
            except Exception as e:
                error_count += 1
                item["status"] = "ERROR"
                errors.append(f"Failed to move {item['name']}: {str(e)}")

        batch_id = None
        if moves_record:
            batch_id = self.tx_manager.record_batch(
                moves_record,
                description=f"Organized {moved_count} files into daily folders"
            )

        return {
            "batch_id": batch_id,
            "total": total,
            "moved": moved_count,
            "skipped": skipped_count,
            "errors_count": error_count,
            "errors": errors
        }
