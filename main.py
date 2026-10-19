import sys
import os

# Ensure project root is in sys.path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from ui.app import FileOrganizerApp


def main():
    """Launch the File Organizer Desktop Application."""
    app = FileOrganizerApp()
    app.mainloop()


if __name__ == "__main__":
    main()
