# core.py
import shutil
import logging
from pathlib import Path
from datetime import datetime
from config import EXTENSION_MAP, LOG_FILENAME, OTHERS_FOLDER

import shutil
import logging
from pathlib import Path
from datetime import datetime
from watchdog.events import FileSystemEventHandler
from config import EXTENSION_MAP, LOG_FILENAME, OTHERS_FOLDER

class JanitorHandler(FileSystemEventHandler):
    def __init__(self, janitor):
        self.janitor = janitor

    def on_created(self, event):
        if not event.is_directory:
            logging.info(f"New file detected: {event.src_path}")
            self.janitor.organize_file(Path(event.src_path))

class SmartFileJanitor:
    def __init__(self, root_dir: str, interactive: bool = False):
        """
        Initialize the Smart File Janitor.
        
        Args:
            root_dir (str): The absolute path to the directory to organize.
            interactive (bool): If True, asks for user confirmation before moving files.
        """
        self.root_dir = Path(root_dir)
        self.interactive = interactive
        self._setup_logging()

    def _setup_logging(self):
        """Configures the logging system."""
        log_path = self.root_dir / LOG_FILENAME
        logging.basicConfig(
            filename=log_path,
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )
        # Also print to console
        console = logging.StreamHandler()
        console.setLevel(logging.INFO)
        formatter = logging.Formatter('%(message)s')
        console.setFormatter(formatter)
        logging.getLogger('').addHandler(console)

    def _get_destination_folder(self, extension: str) -> str:
        """
        Determines the destination folder based on the file extension.
        """
        extension = extension.lower()
        for folder, extensions in EXTENSION_MAP.items():
            if extension in extensions:
                return folder
        return OTHERS_FOLDER

    def _resolve_collision(self, destination_path: Path) -> Path:
        """
        Handles filename collisions by appending a timestamp.
        
        Args:
            destination_path (Path): The intended path that already exists.
            
        Returns:
            Path: A new, unique path with a timestamp appended.
        """
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        stem = destination_path.stem
        suffix = destination_path.suffix
        new_filename = f"{stem}_{timestamp}{suffix}"
        return destination_path.parent / new_filename

    def organize(self):
        """
        Main execution method to scan and organize files.
        """
        logging.info(f"Starting cleanup in: {self.root_dir}")
        
    def organize_file(self, file_path: Path):
        """
        Organizes a single file into its appropriate destination.
        """
        # specific_restrictions
        IGNORED_FILES = {LOG_FILENAME, "main.py", "core.py", "config.py"}
        
        if file_path.name in IGNORED_FILES:
            return

        if not file_path.exists():
            return

        extension = file_path.suffix
        if not extension:
            return

        folder_name = self._get_destination_folder(extension)
        dest_dir = self.root_dir / folder_name
        
        # Create destination directory if it doesn't exist
        dest_dir.mkdir(exist_ok=True)
        
        dest_path = dest_dir / file_path.name

        # Collision Protocol
        if dest_path.exists():
            new_dest_path = self._resolve_collision(dest_path)
            logging.warning(f"Collision detected: {file_path.name} -> Renaming to {new_dest_path.name}")
            dest_path = new_dest_path
        
        # Interactive Confirmation
        if self.interactive:
            print(f"[?] Move '{file_path.name}' to '{folder_name}'? (y/n): ", end='', flush=True)
            response = input().strip().lower()
            if response != 'y':
                logging.info(f"Skipped: {file_path.name} (User cancelled)")
                return

        try:
            # Check if file still exists before moving (race condition check)
            if file_path.exists():
                shutil.move(str(file_path), str(dest_path))
                logging.info(f"Moved: {file_path.name} -> {folder_name}/{dest_path.name}")
        except Exception as e:
            logging.error(f"Failed to move {file_path.name}: {e}")

    def organize(self):
        """
        Main execution method to scan and organize files.
        """
        logging.info(f"Starting cleanup in: {self.root_dir}")
        
        if not self.root_dir.exists():
            logging.error(f"Directory not found: {self.root_dir}")
            return

        # specific_restrictions
        IGNORED_FILES = {LOG_FILENAME, "main.py", "core.py", "config.py"}
        files = [f for f in self.root_dir.iterdir() if f.is_file() and f.name not in IGNORED_FILES]

        if not files:
            logging.info("No files found to organize.")
            return

        for file_path in files:
            self.organize_file(file_path)


    def cleanup_old_files(self):
        """
        Deletes files in specified folders that are older than the retention policy.
        """
        import time
        from config import RETENTION_POLICIES
        
        logging.info("Starting lifecycle cleanup...")
        print("Running Lifecycle Cleanup...")

        for folder_name, days in RETENTION_POLICIES.items():
            folder_path = self.root_dir / folder_name
            if not folder_path.exists():
                continue
            
            cutoff_time = time.time() - (days * 86400) # 86400 seconds in a day
            
            for file_path in folder_path.iterdir():
                if not file_path.is_file():
                    continue
                
                # Check modification time
                if file_path.stat().st_mtime < cutoff_time:
                    # Interactive Confirmation
                    if self.interactive:
                        print(f"[!] Delete old file '{folder_name}/{file_path.name}'? (Last modified: {datetime.fromtimestamp(file_path.stat().st_mtime)}) (y/n): ", end='', flush=True)
                        response = input().strip().lower()
                        if response != 'y':
                            logging.info(f"Skipped deletion: {file_path.name}")
                            continue
                    
                    try:
                        file_path.unlink()
                        logging.info(f"Deleted old file: {folder_name}/{file_path.name}")
                        print(f"Deleted: {file_path.name}")
                    except Exception as e:
                        logging.error(f"Failed to delete {file_path.name}: {e}")

        logging.info("Lifecycle cleanup completed.")
        print("Cleanup completed.")
