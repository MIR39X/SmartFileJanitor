# main.py
import argparse
import sys
from pathlib import Path
from core import SmartFileJanitor

def main():
    parser = argparse.ArgumentParser(description="Smart File Janitor (SFJ) - A tool to organize your files.")
    parser.add_argument(
        "directory", 
        nargs="?", 
        default=None, 
        help="The directory to organize. Defaults to the current directory."
    )
    
    parser.add_argument(
        "--watch",
        action="store_true",
        help="Run in background and watch for new files."
    )
    
    parser.add_argument(
        "--interactive", "-i",
        action="store_true",
        help="Ask for confirmation before moving files."
    )
    
    parser.add_argument(
        "--clean",
        action="store_true",
        help="Run lifecycle cleanup to delete old files."
    )
    
    args = parser.parse_args()
    
    target_dir_str = args.directory
    
    # If no directory provided, pop up folder selection
    if target_dir_str is None:
        try:
            import tkinter as tk
            from tkinter import filedialog
            
            root = tk.Tk()
            root.withdraw() # Hide the main window
            print("Please select a folder to organize...")
            target_dir_str = filedialog.askdirectory(title="Select Folder to Organize")
            root.destroy()
            
            if not target_dir_str:
                print("No folder selected. Exiting.")
                return
        except ImportError:
            print("Tkinter not found. Defaulting to current directory.")
            target_dir_str = "."

    # Resolve the absolute path
    target_dir = Path(target_dir_str).resolve()
    
    print(f"Initializing Smart File Janitor for: {target_dir}")
    if args.interactive:
        print("Interactive Mode: ENABLED")
    print("---------------------------------------------------")
    
    janitor = SmartFileJanitor(str(target_dir), interactive=args.interactive)
    
    if args.watch:
        import time
        from watchdog.observers import Observer
        from core import JanitorHandler
        
        event_handler = JanitorHandler(janitor)
        observer = Observer()
        observer.schedule(event_handler, str(target_dir), recursive=False)
        observer.start()
        print(f"Watching for changes in: {target_dir}")
        print("Press Ctrl+C to stop.")
        try:
            while True:
                time.sleep(1)
        except KeyboardInterrupt:
            observer.stop()
        observer.join()
    elif args.clean:
        janitor.cleanup_old_files()
    else:
        janitor.organize()

if __name__ == "__main__":
    main()
