import os
import datetime
from pathlib import Path
from typing import List, Dict, Any, Optional

try:
    from PIL import Image
    from PIL.ExifTags import TAGS
    PIL_AVAILABLE = True
except ImportError:
    PIL_AVAILABLE = False


def format_file_size(size_bytes: int) -> str:
    """Format bytes into human-readable string (B, KB, MB, GB)."""
    if size_bytes < 1024:
        return f"{size_bytes} B"
    elif size_bytes < 1024 * 1024:
        return f"{size_bytes / 1024:.1f} KB"
    elif size_bytes < 1024 * 1024 * 1024:
        return f"{size_bytes / (1024 * 1024):.1f} MB"
    else:
        return f"{size_bytes / (1024 * 1024 * 1024):.2f} GB"


def get_exif_date(file_path: str) -> Optional[datetime.datetime]:
    """Attempt to extract the original capture date from image EXIF metadata."""
    if not PIL_AVAILABLE:
        return None
    
    ext = Path(file_path).suffix.lower()
    if ext not in ('.jpg', '.jpeg', '.tiff', '.tif', '.png', '.webp'):
        return None

    try:
        with Image.open(file_path) as img:
            exif_data = img._getexif()
            if not exif_data:
                return None
            
            for tag_id, value in exif_data.items():
                tag_name = TAGS.get(tag_id, tag_id)
                if tag_name in ('DateTimeOriginal', 'DateTimeDigitized', 'DateTime'):
                    if isinstance(value, str):
                        try:
                            # Standard EXIF format: "YYYY:MM:DD HH:MM:SS"
                            date_str = value.split(' ')[0].replace(':', '-')
                            return datetime.datetime.strptime(date_str, "%Y-%m-%d")
                        except Exception:
                            pass
    except Exception:
        return None
    return None


def get_file_date(file_path: str, date_source: str = "Date Modified") -> datetime.datetime:
    """
    Retrieve file date according to chosen date_source:
    - 'Date Modified' (mtime)
    - 'Date Created' (ctime on Windows)
    - 'EXIF Photo Date' (falls back to mtime if absent)
    """
    if date_source == "EXIF Photo Date":
        exif_dt = get_exif_date(file_path)
        if exif_dt:
            return exif_dt
        # Fallback to mtime
        return datetime.datetime.fromtimestamp(os.path.getmtime(file_path))
    elif date_source == "Date Created":
        try:
            return datetime.datetime.fromtimestamp(os.path.getctime(file_path))
        except Exception:
            return datetime.datetime.fromtimestamp(os.path.getmtime(file_path))
    else:  # Default: Date Modified
        return datetime.datetime.fromtimestamp(os.path.getmtime(file_path))


def format_folder_name(dt: datetime.datetime, format_pattern: str) -> str:
    """Format folder name from datetime according to preset or strftime template."""
    pattern_map = {
        "YYYY-MM-DD": "%Y-%m-%d",
        "DD-MM-YYYY": "%d-%m-%Y",
        "YYYY_MM_DD": "%Y_%m_%d",
        "YYYY.MM.DD": "%Y.%m.%d",
        "YYYY/MM (Year/Month)": os.path.join("%Y", "%m"),
        "Month YYYY": "%B %Y",
    }
    
    pattern = pattern_map.get(format_pattern, format_pattern)
    try:
        return dt.strftime(pattern)
    except Exception:
        return dt.strftime("%Y-%m-%d")


def scan_directory(
    base_dir: str,
    date_source: str = "Date Modified",
    folder_pattern: str = "YYYY-MM-DD",
    recursive: bool = False,
    exclude_hidden: bool = True
) -> List[Dict[str, Any]]:
    """
    Scan the target directory and calculate destination folders for each file.
    Skips the journal file and already organized date subfolders if root-only.
    """
    results: List[Dict[str, Any]] = []
    base_path = Path(base_dir).resolve()
    
    if not base_path.exists() or not base_path.is_dir():
        return results

    journal_name = ".file_organizer_journal.json"

    if not recursive:
        # Scan only root folder
        try:
            with os.scandir(base_path) as entries:
                for entry in entries:
                    if not entry.is_file():
                        continue
                    if exclude_hidden and entry.name.startswith('.'):
                        continue
                    if entry.name == journal_name:
                        continue
                    
                    full_path = os.path.join(base_path, entry.name)
                    try:
                        stat = entry.stat()
                        size = stat.st_size
                    except OSError:
                        size = 0
                    
                    dt = get_file_date(full_path, date_source)
                    folder_rel = format_folder_name(dt, folder_pattern)
                    target_dir = os.path.join(base_path, folder_rel)
                    target_path = os.path.join(target_dir, entry.name)

                    results.append({
                        "name": entry.name,
                        "src_path": full_path,
                        "rel_src": entry.name,
                        "size_bytes": size,
                        "size_formatted": format_file_size(size),
                        "date": dt,
                        "date_str": dt.strftime("%Y-%m-%d %H:%M"),
                        "folder_rel": folder_rel,
                        "target_dir": target_dir,
                        "target_path": target_path,
                        "ext": Path(entry.name).suffix.lower(),
                        "status": "PENDING"
                    })
        except PermissionError:
            pass
    else:
        # Recursive scan
        for root, dirs, files in os.walk(base_path):
            if exclude_hidden:
                dirs[:] = [d for d in dirs if not d.startswith('.')]
            
            for file in files:
                if exclude_hidden and file.startswith('.'):
                    continue
                if file == journal_name:
                    continue
                
                full_path = os.path.join(root, file)
                rel_src = os.path.relpath(full_path, base_path)
                
                try:
                    size = os.path.getsize(full_path)
                except OSError:
                    size = 0
                
                dt = get_file_date(full_path, date_source)
                folder_rel = format_folder_name(dt, folder_pattern)
                target_dir = os.path.join(base_path, folder_rel)
                target_path = os.path.join(target_dir, file)

                results.append({
                    "name": file,
                    "src_path": full_path,
                    "rel_src": rel_src,
                    "size_bytes": size,
                    "size_formatted": format_file_size(size),
                    "date": dt,
                    "date_str": dt.strftime("%Y-%m-%d %H:%M"),
                    "folder_rel": folder_rel,
                    "target_dir": target_dir,
                    "target_path": target_path,
                    "ext": Path(file).suffix.lower(),
                    "status": "PENDING"
                })

    return results
