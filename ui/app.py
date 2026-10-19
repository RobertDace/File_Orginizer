import os
import sys
import threading
import subprocess
from pathlib import Path
from typing import List, Dict, Any, Optional

import customtkinter as ctk
from tkinter import filedialog, messagebox

from core.scanner import scan_directory, format_file_size
from core.organizer import OrganizerEngine
from core.transaction import TransactionManager
from ui.theme import (
    CORNER_RADIUS,
    COLOR_BG,
    COLOR_SURFACE_1,
    COLOR_SURFACE_2,
    COLOR_SURFACE_HOVER,
    COLOR_BORDER,
    COLOR_BORDER_FOCUS,
    COLOR_NEON_LIME,
    COLOR_HAZARD_ORANGE,
    COLOR_TEXT_PRIMARY,
    COLOR_TEXT_MUTED,
    COLOR_TEXT_DIM,
    COLOR_DANGER,
    COLOR_SUCCESS,
    FONT_MACRO_HEADER,
    FONT_SECTION_HEADER,
    FONT_TELEMETRY,
    FONT_TELEMETRY_BOLD,
    FONT_TELEMETRY_SMALL,
    FONT_BUTTON_PRIMARY,
    FONT_BADGE,
    BADGE_SYS_IDLE,
    BADGE_SYS_SCANNING,
    BADGE_SYS_READY,
    BADGE_SYS_EXECUTING,
    BADGE_SYS_DONE
)
from ui.components import TacticalBadge, BrutalistButton, ConflictDialog


class FileOrganizerApp(ctk.CTk):
    """
    Main Desktop Application for File Organizer.
    Industrial Brutalist & Streetwear Tactical Telemetry Edition.
    """

    def __init__(self):
        super().__init__()

        # Appearance configuration
        ctk.set_appearance_mode("dark")
        ctk.set_default_color_theme("dark-blue")

        self.title(">>> FILE//ORGANIZER™ [TACTICAL TELEMETRY]")
        self.geometry("1060x760")
        self.minsize(980, 680)
        self.configure(fg_color=COLOR_BG)

        # Set tactical icon if present
        icon_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "assets", "icon.ico")
        if os.path.exists(icon_path):
            try:
                self.iconbitmap(icon_path)
            except Exception:
                pass

        # Internal state
        self.current_folder: str = ""
        self.scanned_items: List[Dict[str, Any]] = []
        self.filtered_items: List[Dict[str, Any]] = []
        self.is_processing: bool = False
        self.organizer_engine: Optional[OrganizerEngine] = None
        self.tx_manager: Optional[TransactionManager] = None

        # Build UI
        self._build_header()
        self._build_folder_selector()
        self._build_controls_matrix()
        self._build_preview_matrix()
        self._build_bottom_action_bar()

        # Update initial undo state
        self._update_undo_button_state()

    # =========================================================================
    # UI BUILDERS
    # =========================================================================

    def _build_header(self):
        """Top brand bar with industrial monospace badges and hazard stripe."""
        header_frame = ctk.CTkFrame(
            self,
            fg_color=COLOR_SURFACE_1,
            corner_radius=CORNER_RADIUS,
            border_width=1,
            border_color=COLOR_BORDER,
            height=70
        )
        header_frame.pack(fill="x", padx=16, pady=(16, 8))
        header_frame.pack_propagate(False)

        # Left brand title
        left_box = ctk.CTkFrame(header_frame, fg_color="transparent")
        left_box.pack(side="left", fill="y", padx=16, pady=8)

        ctk.CTkLabel(
            left_box,
            text=">>> FILE//ORGANIZER™",
            font=FONT_MACRO_HEADER,
            text_color=COLOR_TEXT_PRIMARY
        ).pack(anchor="w")

        ctk.CTkLabel(
            left_box,
            text="TACTICAL TELEMETRY // DAILY BATCH ROTATION ENGINE",
            font=FONT_TELEMETRY_SMALL,
            text_color=COLOR_HAZARD_ORANGE
        ).pack(anchor="w")

        # Right telemetry status badges
        right_box = ctk.CTkFrame(header_frame, fg_color="transparent")
        right_box.pack(side="right", padx=16, pady=12)

        self.badge_status = TacticalBadge(
            right_box,
            text=BADGE_SYS_IDLE,
            bg_color=COLOR_SURFACE_2,
            border_color=COLOR_BORDER,
            text_color=COLOR_TEXT_MUTED
        )
        self.badge_status.pack(side="left", padx=4)

        TacticalBadge(
            right_box,
            text="[REV: 1.0.4]",
            bg_color=COLOR_SURFACE_2,
            border_color=COLOR_BORDER,
            text_color=COLOR_NEON_LIME
        ).pack(side="left", padx=4)

        TacticalBadge(
            right_box,
            text="[OS: WIN_X64]",
            bg_color=COLOR_SURFACE_2,
            border_color=COLOR_BORDER,
            text_color=COLOR_TEXT_MUTED
        ).pack(side="left", padx=4)

    def _build_folder_selector(self):
        """Directory input box, browse button, and quick Explorer actions."""
        selector_frame = ctk.CTkFrame(
            self,
            fg_color=COLOR_SURFACE_1,
            corner_radius=CORNER_RADIUS,
            border_width=1,
            border_color=COLOR_BORDER
        )
        selector_frame.pack(fill="x", padx=16, pady=4)

        # Label line
        top_line = ctk.CTkFrame(selector_frame, fg_color="transparent")
        top_line.pack(fill="x", padx=14, pady=(10, 4))

        ctk.CTkLabel(
            top_line,
            text="// TARGET DIRECTORY LOCATION",
            font=FONT_TELEMETRY_BOLD,
            text_color=COLOR_NEON_LIME
        ).pack(side="left")

        ctk.CTkLabel(
            top_line,
            text="Select or drop folder to index files",
            font=FONT_TELEMETRY_SMALL,
            text_color=COLOR_TEXT_MUTED
        ).pack(side="left", padx=8)

        # Input row
        input_row = ctk.CTkFrame(selector_frame, fg_color="transparent")
        input_row.pack(fill="x", padx=14, pady=(0, 12))

        self.entry_folder = ctk.CTkEntry(
            input_row,
            corner_radius=CORNER_RADIUS,
            border_width=1,
            border_color=COLOR_BORDER,
            fg_color=COLOR_BG,
            text_color=COLOR_TEXT_PRIMARY,
            font=FONT_TELEMETRY,
            placeholder_text="Enter or select target folder path (e.g. C:\\Users\\...\\Downloads)",
            height=38
        )
        self.entry_folder.pack(side="left", fill="x", expand=True, padx=(0, 8))
        self.entry_folder.bind("<Return>", lambda e: self._on_folder_entered())

        BrutalistButton(
            input_row,
            text="[ BROWSE DIR ]",
            variant="primary",
            width=130,
            height=38,
            command=self._on_browse_folder
        ).pack(side="left", padx=4)

        BrutalistButton(
            input_row,
            text="[ RESCAN ]",
            variant="secondary",
            width=100,
            height=38,
            command=self._on_rescan_clicked
        ).pack(side="left", padx=4)

        BrutalistButton(
            input_row,
            text="[ EXPLORER ]",
            variant="secondary",
            width=110,
            height=38,
            command=self._on_open_explorer
        ).pack(side="left", padx=4)

    def _build_controls_matrix(self):
        """Configuration options: Date source, naming pattern, scope, collision handling."""
        controls_frame = ctk.CTkFrame(
            self,
            fg_color=COLOR_SURFACE_1,
            corner_radius=CORNER_RADIUS,
            border_width=1,
            border_color=COLOR_BORDER
        )
        controls_frame.pack(fill="x", padx=16, pady=4)

        grid_frame = ctk.CTkFrame(controls_frame, fg_color="transparent")
        grid_frame.pack(fill="x", padx=14, pady=10)

        # Column 1: Date Source
        col1 = ctk.CTkFrame(grid_frame, fg_color="transparent")
        col1.pack(side="left", fill="x", expand=True, padx=4)

        ctk.CTkLabel(col1, text="[ DATE SOURCE ]", font=FONT_TELEMETRY_BOLD, text_color=COLOR_TEXT_MUTED).pack(anchor="w", pady=(0, 4))
        self.opt_date_source = ctk.CTkOptionMenu(
            col1,
            values=["Date Modified", "Date Created", "EXIF Photo Date"],
            corner_radius=CORNER_RADIUS,
            fg_color=COLOR_SURFACE_2,
            button_color=COLOR_SURFACE_HOVER,
            text_color=COLOR_TEXT_PRIMARY,
            font=FONT_TELEMETRY,
            dropdown_font=FONT_TELEMETRY,
            dropdown_fg_color=COLOR_SURFACE_1,
            command=lambda _: self._trigger_rescan()
        )
        self.opt_date_source.set("Date Modified")
        self.opt_date_source.pack(fill="x")

        # Column 2: Folder Format
        col2 = ctk.CTkFrame(grid_frame, fg_color="transparent")
        col2.pack(side="left", fill="x", expand=True, padx=4)

        ctk.CTkLabel(col2, text="[ FOLDER PATTERN ]", font=FONT_TELEMETRY_BOLD, text_color=COLOR_TEXT_MUTED).pack(anchor="w", pady=(0, 4))
        self.opt_folder_format = ctk.CTkOptionMenu(
            col2,
            values=["YYYY-MM-DD", "DD-MM-YYYY", "YYYY_MM_DD", "YYYY.MM.DD", "YYYY/MM (Year/Month)", "Month YYYY"],
            corner_radius=CORNER_RADIUS,
            fg_color=COLOR_SURFACE_2,
            button_color=COLOR_SURFACE_HOVER,
            text_color=COLOR_TEXT_PRIMARY,
            font=FONT_TELEMETRY,
            dropdown_font=FONT_TELEMETRY,
            dropdown_fg_color=COLOR_SURFACE_1,
            command=lambda _: self._trigger_rescan()
        )
        self.opt_folder_format.set("YYYY-MM-DD")
        self.opt_folder_format.pack(fill="x")

        # Column 3: Collision Policy
        col3 = ctk.CTkFrame(grid_frame, fg_color="transparent")
        col3.pack(side="left", fill="x", expand=True, padx=4)

        ctk.CTkLabel(col3, text="[ ON COLLISION ]", font=FONT_TELEMETRY_BOLD, text_color=COLOR_TEXT_MUTED).pack(anchor="w", pady=(0, 4))
        self.opt_collision = ctk.CTkOptionMenu(
            col3,
            values=["Ask (Prompt Pop-up)", "Auto-Rename (File_1.ext)", "Skip Conflicting", "Overwrite (Replace)"],
            corner_radius=CORNER_RADIUS,
            fg_color=COLOR_SURFACE_2,
            button_color=COLOR_SURFACE_HOVER,
            text_color=COLOR_TEXT_PRIMARY,
            font=FONT_TELEMETRY,
            dropdown_font=FONT_TELEMETRY,
            dropdown_fg_color=COLOR_SURFACE_1
        )
        self.opt_collision.set("Ask (Prompt Pop-up)")
        self.opt_collision.pack(fill="x")

        # Column 4: Toggles
        col4 = ctk.CTkFrame(grid_frame, fg_color="transparent")
        col4.pack(side="left", fill="x", expand=True, padx=4)

        ctk.CTkLabel(col4, text="[ SCAN SCOPE ]", font=FONT_TELEMETRY_BOLD, text_color=COLOR_TEXT_MUTED).pack(anchor="w", pady=(0, 4))
        self.var_root_only = ctk.BooleanVar(value=True)
        cb_root = ctk.CTkCheckBox(
            col4,
            text="Root files only (ignore subfolders)",
            variable=self.var_root_only,
            corner_radius=CORNER_RADIUS,
            font=FONT_TELEMETRY_SMALL,
            fg_color=COLOR_NEON_LIME,
            checkmark_color="#0A0A0A",
            text_color=COLOR_TEXT_PRIMARY,
            command=self._trigger_rescan
        )
        cb_root.pack(anchor="w", pady=4)

    def _build_preview_matrix(self):
        """High-density telemetry preview table with search filter and item rows."""
        table_container = ctk.CTkFrame(
            self,
            fg_color=COLOR_SURFACE_1,
            corner_radius=CORNER_RADIUS,
            border_width=1,
            border_color=COLOR_BORDER
        )
        table_container.pack(fill="both", expand=True, padx=16, pady=4)

        # Header bar of table
        table_top = ctk.CTkFrame(table_container, fg_color="transparent")
        table_top.pack(fill="x", padx=12, pady=(10, 6))

        # Stats badges
        self.badge_files_count = TacticalBadge(
            table_top,
            text="FILES: 0",
            bg_color=COLOR_SURFACE_2,
            text_color=COLOR_NEON_LIME
        )
        self.badge_files_count.pack(side="left", padx=4)

        self.badge_folders_count = TacticalBadge(
            table_top,
            text="TARGET FOLDERS: 0",
            bg_color=COLOR_SURFACE_2,
            text_color=COLOR_TEXT_PRIMARY
        )
        self.badge_folders_count.pack(side="left", padx=4)

        self.badge_payload_size = TacticalBadge(
            table_top,
            text="PAYLOAD: 0 B",
            bg_color=COLOR_SURFACE_2,
            text_color=COLOR_TEXT_MUTED
        )
        self.badge_payload_size.pack(side="left", padx=4)

        # Search filter
        self.entry_filter = ctk.CTkEntry(
            table_top,
            corner_radius=CORNER_RADIUS,
            border_width=1,
            border_color=COLOR_BORDER,
            fg_color=COLOR_BG,
            text_color=COLOR_TEXT_PRIMARY,
            font=FONT_TELEMETRY,
            placeholder_text="Filter files by name...",
            width=220,
            height=30
        )
        self.entry_filter.pack(side="right", padx=4)
        self.entry_filter.bind("<KeyRelease>", lambda e: self._apply_search_filter())

        # Table Column Headers
        col_header_frame = ctk.CTkFrame(
            table_container,
            fg_color=COLOR_SURFACE_2,
            corner_radius=CORNER_RADIUS,
            border_width=1,
            border_color=COLOR_BORDER,
            height=32
        )
        col_header_frame.pack(fill="x", padx=12, pady=(4, 0))
        col_header_frame.pack_propagate(False)

        ctk.CTkLabel(col_header_frame, text="STATUS", font=FONT_TELEMETRY_BOLD, text_color=COLOR_TEXT_MUTED, width=70, anchor="w").pack(side="left", padx=(10, 4))
        ctk.CTkLabel(col_header_frame, text="FILE NAME", font=FONT_TELEMETRY_BOLD, text_color=COLOR_TEXT_MUTED, width=320, anchor="w").pack(side="left", padx=4)
        ctk.CTkLabel(col_header_frame, text="SIZE", font=FONT_TELEMETRY_BOLD, text_color=COLOR_TEXT_MUTED, width=90, anchor="e").pack(side="left", padx=4)
        ctk.CTkLabel(col_header_frame, text="DETECTED DATE", font=FONT_TELEMETRY_BOLD, text_color=COLOR_TEXT_MUTED, width=150, anchor="w").pack(side="left", padx=10)
        ctk.CTkLabel(col_header_frame, text="DESTINATION FOLDER", font=FONT_TELEMETRY_BOLD, text_color=COLOR_TEXT_MUTED, anchor="w").pack(side="left", fill="x", expand=True, padx=4)

        # Scrollable rows frame
        self.scroll_table = ctk.CTkScrollableFrame(
            table_container,
            fg_color=COLOR_BG,
            corner_radius=CORNER_RADIUS,
            border_width=1,
            border_color=COLOR_BORDER
        )
        self.scroll_table.pack(fill="both", expand=True, padx=12, pady=(4, 12))

        # Initial Empty State Placeholder
        self._render_empty_state("NO FOLDER SELECTED // SPECIFY DIRECTORY TO BEGIN")

    def _build_bottom_action_bar(self):
        """Progress bar, log status line, and execution action buttons."""
        bottom_frame = ctk.CTkFrame(
            self,
            fg_color=COLOR_SURFACE_1,
            corner_radius=CORNER_RADIUS,
            border_width=1,
            border_color=COLOR_BORDER,
            height=76
        )
        bottom_frame.pack(fill="x", padx=16, pady=(4, 16))
        bottom_frame.pack_propagate(False)

        # Left: Progress and status message
        left_status = ctk.CTkFrame(bottom_frame, fg_color="transparent")
        left_status.pack(side="left", fill="both", expand=True, padx=14, pady=10)

        self.progress_bar = ctk.CTkProgressBar(
            left_status,
            corner_radius=CORNER_RADIUS,
            height=10,
            fg_color=COLOR_SURFACE_2,
            progress_color=COLOR_NEON_LIME
        )
        self.progress_bar.pack(fill="x", pady=(2, 4))
        self.progress_bar.set(0.0)

        self.lbl_status = ctk.CTkLabel(
            left_status,
            text="[STATUS: READY FOR INPUT]",
            font=FONT_TELEMETRY_BOLD,
            text_color=COLOR_TEXT_MUTED,
            anchor="w"
        )
        self.lbl_status.pack(fill="x")

        # Right: Action Buttons
        right_actions = ctk.CTkFrame(bottom_frame, fg_color="transparent")
        right_actions.pack(side="right", padx=14, pady=12)

        self.btn_undo = BrutalistButton(
            right_actions,
            text="[ << UNDO LAST RUN ]",
            variant="secondary",
            width=170,
            height=44,
            command=self._on_undo_clicked
        )
        self.btn_undo.pack(side="left", padx=6)

        self.btn_execute = BrutalistButton(
            right_actions,
            text="[ >>> EXECUTE ORGANIZE ]",
            variant="primary",
            width=230,
            height=44,
            command=self._on_execute_clicked
        )
        self.btn_execute.pack(side="left", padx=6)

    # =========================================================================
    # EVENT HANDLERS & LOGIC
    # =========================================================================

    def _on_browse_folder(self):
        """Open native Windows directory selection dialog."""
        folder = filedialog.askdirectory(title="Select Folder to Organize")
        if folder:
            self.entry_folder.delete(0, "end")
            self.entry_folder.insert(0, folder)
            self._set_active_folder(folder)

    def _on_folder_entered(self):
        """User typed or pasted path in entry."""
        folder = self.entry_folder.get().strip().strip('"')
        if folder and os.path.isdir(folder):
            self._set_active_folder(folder)
        elif folder:
            messagebox.showwarning("[!] INVALID DIRECTORY", f"The specified path does not exist or is not a directory:\n{folder}")

    def _on_rescan_clicked(self):
        """Explicit rescan trigger."""
        if self.current_folder and os.path.isdir(self.current_folder):
            self._start_scanning()
        else:
            self._on_browse_folder()

    def _on_open_explorer(self):
        """Open the currently selected folder in Windows Explorer."""
        folder = self.current_folder or self.entry_folder.get().strip().strip('"')
        if folder and os.path.isdir(folder):
            subprocess.Popen(f'explorer "{os.path.abspath(folder)}"')
        else:
            messagebox.showinfo("[i] INFO", "Please select a valid folder first.")

    def _trigger_rescan(self):
        """Trigger rescan when option dropdowns change."""
        if self.current_folder and os.path.isdir(self.current_folder):
            self._start_scanning()

    def _set_active_folder(self, folder_path: str):
        """Set target folder, initialize engines, and start scanning."""
        self.current_folder = os.path.abspath(folder_path)
        self.organizer_engine = OrganizerEngine(self.current_folder)
        self.tx_manager = TransactionManager(self.current_folder)
        self._update_undo_button_state()
        self._start_scanning()

    def _start_scanning(self):
        """Run directory scanning on a background thread to prevent UI freezing."""
        if self.is_processing or not self.current_folder:
            return

        self.is_processing = True
        self.badge_status.set_text(BADGE_SYS_SCANNING, COLOR_HAZARD_ORANGE)
        self.lbl_status.configure(text=f"[SCANNING: {self.current_folder}...]", text_color=COLOR_HAZARD_ORANGE)
        self._render_empty_state("READING FILESYSTEM METADATA... PLEASE WAIT")

        date_source = self.opt_date_source.get()
        folder_pattern = self.opt_folder_format.get()
        recursive = not self.var_root_only.get()

        def scan_worker():
            try:
                items = scan_directory(
                    base_dir=self.current_folder,
                    date_source=date_source,
                    folder_pattern=folder_pattern,
                    recursive=recursive
                )
                self.after(0, lambda: self._on_scan_completed(items))
            except Exception as e:
                self.after(0, lambda: self._on_scan_failed(str(e)))

        threading.Thread(target=scan_worker, daemon=True).start()

    def _on_scan_completed(self, items: List[Dict[str, Any]]):
        """Callback when scan thread finishes successfully."""
        self.is_processing = False
        self.scanned_items = items
        self.badge_status.set_text(BADGE_SYS_READY, COLOR_NEON_LIME)

        total_bytes = sum(item["size_bytes"] for item in items)
        unique_folders = len(set(item["folder_rel"] for item in items))

        self.badge_files_count.set_text(f"FILES: {len(items)}")
        self.badge_folders_count.set_text(f"TARGET FOLDERS: {unique_folders}")
        self.badge_payload_size.set_text(f"PAYLOAD: {format_file_size(total_bytes)}")

        self.lbl_status.configure(
            text=f"[INDEXED {len(items)} FILES -> {unique_folders} DAILY FOLDERS ({format_file_size(total_bytes)})]",
            text_color=COLOR_TEXT_PRIMARY
        )
        self.progress_bar.set(0.0)

        self._apply_search_filter()

    def _on_scan_failed(self, error_msg: str):
        """Callback if scan thread encountered an exception."""
        self.is_processing = False
        self.badge_status.set_text("[SYS // ERROR]", COLOR_DANGER)
        self.lbl_status.configure(text=f"[SCAN ERROR: {error_msg}]", text_color=COLOR_DANGER)
        self._render_empty_state(f"FAILED TO SCAN DIRECTORY:\n{error_msg}")

    # =========================================================================
    # TABLE RENDERING
    # =========================================================================

    def _render_empty_state(self, message: str):
        """Clear table and display a centered industrial placeholder."""
        for widget in self.scroll_table.winfo_children():
            widget.destroy()

        empty_box = ctk.CTkFrame(self.scroll_table, fg_color="transparent")
        empty_box.pack(expand=True, fill="both", pady=80)

        ctk.CTkLabel(
            empty_box,
            text=f"// {message}",
            font=FONT_TELEMETRY_BOLD,
            text_color=COLOR_TEXT_MUTED
        ).pack()

    def _apply_search_filter(self):
        """Filter items in preview table based on query string."""
        query = self.entry_filter.get().strip().lower()
        if not query:
            self.filtered_items = self.scanned_items
        else:
            self.filtered_items = [
                item for item in self.scanned_items
                if query in item["name"].lower() or query in item["folder_rel"].lower()
            ]
        self._render_table_rows()

    def _render_table_rows(self):
        """Populate the scrollable table with file rows."""
        for widget in self.scroll_table.winfo_children():
            widget.destroy()

        if not self.filtered_items:
            self._render_empty_state("NO FILES MATCH THE CURRENT FILTER OR FOLDER IS EMPTY")
            return

        # Render rows (cap initial render if huge for instant display)
        max_render = 500
        for idx, item in enumerate(self.filtered_items[:max_render]):
            row_bg = COLOR_SURFACE_1 if idx % 2 == 0 else COLOR_SURFACE_2
            row_frame = ctk.CTkFrame(
                self.scroll_table,
                fg_color=row_bg,
                corner_radius=CORNER_RADIUS,
                border_width=0,
                height=28
            )
            row_frame.pack(fill="x", pady=1)
            row_frame.pack_propagate(False)

            # Status column
            status = item.get("status", "PENDING")
            status_color = COLOR_NEON_LIME if status == "MOVED" else (COLOR_HAZARD_ORANGE if status == "SKIPPED" else COLOR_TEXT_MUTED)
            ctk.CTkLabel(
                row_frame,
                text=f"[{status[:7]}]",
                font=FONT_TELEMETRY_SMALL,
                text_color=status_color,
                width=70,
                anchor="w"
            ).pack(side="left", padx=(8, 4))

            # File name
            name_label = ctk.CTkLabel(
                row_frame,
                text=item["name"],
                font=FONT_TELEMETRY,
                text_color=COLOR_TEXT_PRIMARY,
                width=320,
                anchor="w"
            )
            name_label.pack(side="left", padx=4)

            # Size
            ctk.CTkLabel(
                row_frame,
                text=item["size_formatted"],
                font=FONT_TELEMETRY_SMALL,
                text_color=COLOR_TEXT_MUTED,
                width=90,
                anchor="e"
            ).pack(side="left", padx=4)

            # Date
            ctk.CTkLabel(
                row_frame,
                text=item["date_str"],
                font=FONT_TELEMETRY_SMALL,
                text_color=COLOR_TEXT_MUTED,
                width=150,
                anchor="w"
            ).pack(side="left", padx=10)

            # Target directory
            ctk.CTkLabel(
                row_frame,
                text=f"-> {item['folder_rel']}/",
                font=FONT_TELEMETRY_BOLD,
                text_color=COLOR_NEON_LIME,
                anchor="w"
            ).pack(side="left", fill="x", expand=True, padx=4)

        if len(self.filtered_items) > max_render:
            overflow_frame = ctk.CTkFrame(self.scroll_table, fg_color="transparent")
            overflow_frame.pack(fill="x", pady=6)
            ctk.CTkLabel(
                overflow_frame,
                text=f"... and {len(self.filtered_items) - max_render} more files (all included in batch execution)",
                font=FONT_TELEMETRY_SMALL,
                text_color=COLOR_TEXT_MUTED
            ).pack()

    # =========================================================================
    # EXECUTION & UNDO ENGINE
    # =========================================================================

    def _collision_resolver_callback(self, src: str, dst: str):
        """Invoke interactive ConflictDialog modal on main thread."""
        dialog = ConflictDialog(self, src, dst)
        return dialog.get_result()

    def _on_execute_clicked(self):
        """Begin organizing files."""
        if not self.scanned_items:
            messagebox.showinfo("[i] NO FILES", "There are no files to organize. Please select a valid folder.")
            return

        if self.is_processing:
            return

        # Confirmation prompt
        confirm = messagebox.askyesno(
            "[?] CONFIRM BATCH EXECUTION",
            f"Are you sure you want to organize {len(self.scanned_items)} file(s) in:\n{self.current_folder}\n\nAll files will be moved into daily subfolders.\n(This action can be undone with 1-click afterwards)."
        )
        if not confirm:
            return

        self.is_processing = True
        self.btn_execute.configure(state="disabled")
        self.btn_undo.configure(state="disabled")
        self.badge_status.set_text(BADGE_SYS_EXECUTING, COLOR_HAZARD_ORANGE)

        # Determine collision policy
        col_setting = self.opt_collision.get()
        if "Auto-Rename" in col_setting:
            policy = "auto_rename"
        elif "Skip" in col_setting:
            policy = "skip"
        elif "Overwrite" in col_setting:
            policy = "replace"
        else:
            policy = "ask"

        def worker():
            def progress(current, total, file_name):
                pct = current / total if total > 0 else 0
                self.after(0, lambda: self._on_batch_progress(pct, current, total, file_name))

            report = self.organizer_engine.execute_batch(
                items=self.scanned_items,
                collision_policy=policy,
                collision_callback=self._collision_resolver_callback,
                progress_callback=progress
            )
            self.after(0, lambda: self._on_batch_finished(report))

        threading.Thread(target=worker, daemon=True).start()

    def _on_batch_progress(self, pct: float, current: int, total: int, file_name: str):
        """Update progress bar and status line as files move."""
        self.progress_bar.set(pct)
        self.lbl_status.configure(
            text=f"[MOVING {current}/{total}]: {file_name}",
            text_color=COLOR_NEON_LIME
        )

    def _on_batch_finished(self, report: Dict[str, Any]):
        """Handler when file moving batch finishes."""
        self.is_processing = False
        self.btn_execute.configure(state="normal")
        self.badge_status.set_text(BADGE_SYS_DONE, COLOR_SUCCESS)
        self.progress_bar.set(1.0)

        moved = report.get("moved", 0)
        skipped = report.get("skipped", 0)
        errors = report.get("errors_count", 0)

        self.lbl_status.configure(
            text=f"[COMPLETE: {moved} MOVED | {skipped} SKIPPED | {errors} ERRORS]",
            text_color=COLOR_SUCCESS if errors == 0 else COLOR_HAZARD_ORANGE
        )

        self._update_undo_button_state()
        self._render_table_rows()

        # Summary popup
        msg = f"Organization completed successfully!\n\n• Moved: {moved}\n• Skipped: {skipped}\n• Errors: {errors}"
        if errors > 0:
            msg += "\n\nCheck logs for detailed error descriptions."
        messagebox.showinfo("[✓] BATCH SUCCESS", msg)

        # Auto rescan remaining
        self._start_scanning()

    def _update_undo_button_state(self):
        """Check if undo is available and toggle button state."""
        if self.tx_manager and self.tx_manager.can_undo():
            self.btn_undo.configure(state="normal", text="[ << UNDO LAST RUN ]", text_color=COLOR_NEON_LIME)
        else:
            self.btn_undo.configure(state="disabled", text="[ << UNDO (NO HISTORY) ]", text_color=COLOR_TEXT_MUTED)

    def _on_undo_clicked(self):
        """Revert the most recent batch of file moves."""
        if not self.tx_manager or not self.tx_manager.can_undo():
            messagebox.showinfo("[i] NO HISTORY", "No transaction batch available to undo.")
            return

        last_batch = self.tx_manager.get_last_batch()
        batch_count = last_batch.get("count", 0) if last_batch else 0

        confirm = messagebox.askyesno(
            "[?] CONFIRM UNDO ROLLBACK",
            f"Are you sure you want to undo the last batch?\n\nThis will restore up to {batch_count} file(s) back to their original locations."
        )
        if not confirm:
            return

        self.is_processing = True
        self.btn_execute.configure(state="disabled")
        self.btn_undo.configure(state="disabled")
        self.badge_status.set_text("[UNDO // REVERTING...]", COLOR_HAZARD_ORANGE)
        self.lbl_status.configure(text="[REVERTING FILES TO ORIGINAL PATHS...]", text_color=COLOR_HAZARD_ORANGE)

        def worker():
            res = self.tx_manager.rollback_last_batch()
            self.after(0, lambda: self._on_undo_finished(res))

        threading.Thread(target=worker, daemon=True).start()

    def _on_undo_finished(self, res: Dict[str, Any]):
        """Handler when undo batch finishes."""
        self.is_processing = False
        self.btn_execute.configure(state="normal")
        self.badge_status.set_text(BADGE_SYS_READY, COLOR_NEON_LIME)

        reverted = res.get("reverted", 0)
        failed = res.get("failed", 0)

        self.lbl_status.configure(
            text=f"[UNDO COMPLETE: {reverted} RESTORED | {failed} FAILED]",
            text_color=COLOR_SUCCESS
        )

        self._update_undo_button_state()

        messagebox.showinfo(
            "[✓] UNDO COMPLETE",
            f"Rollback finished!\n\n• Successfully restored: {reverted} file(s)\n• Failed: {failed}"
        )

        # Rescan to reflect restored state
        self._start_scanning()
