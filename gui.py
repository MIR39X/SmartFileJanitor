import tkinter as tk
from tkinter import ttk, filedialog, messagebox, scrolledtext
import threading
import sys
import logging
from pathlib import Path
from core import SmartFileJanitor, JanitorHandler
from config import load_config, save_config, EXTENSION_MAP, RETENTION_POLICIES
from watchdog.observers import Observer

class RedirectText:
    """Redirects stdout/stderr to a text widget."""
    def __init__(self, text_widget):
        self.text_widget = text_widget

    def write(self, string):
        self.text_widget.insert(tk.END, string)
        self.text_widget.see(tk.END)

    def flush(self):
        pass

class JanitorGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Smart File Janitor V0.0")
        self.root.geometry("800x600")
        
        self.config = load_config()
        self.target_dir = tk.StringVar(value=str(Path.cwd()))
        self.observer = None
        
        self._setup_styles()
        self._create_widgets()
        
        # Redirect stdout
        sys.stdout = RedirectText(self.log_text)
        sys.stderr = RedirectText(self.log_text)
        
        # Setup logging handler to redirect to GUI as well
        self._setup_logging_handler()

    def _setup_styles(self):
        style = ttk.Style()
        style.theme_use('clam')
        style.configure("TButton", padding=6, font=('Helvetica', 10))
        style.configure("TLabel", font=('Helvetica', 10))
        style.configure("Header.TLabel", font=('Helvetica', 12, 'bold'))

    def _create_widgets(self):
        # Main Notebook (Tabs)
        self.notebook = ttk.Notebook(self.root)
        self.notebook.pack(expand=True, fill='both', padx=10, pady=10)

        # Tab: Dashboard
        self.tab_dashboard = ttk.Frame(self.notebook)
        self.notebook.add(self.tab_dashboard, text='Dashboard')
        self._init_dashboard(self.tab_dashboard)

        # Tab: Settings
        self.tab_settings = ttk.Frame(self.notebook)
        self.notebook.add(self.tab_settings, text='Settings')
        self._init_settings(self.tab_settings)

    def _init_dashboard(self, parent):
        frame = ttk.Frame(parent, padding=20)
        frame.pack(fill='both', expand=True)

        # Target Directory
        dir_frame = ttk.Frame(frame)
        dir_frame.pack(fill='x', pady=10)
        ttk.Label(dir_frame, text="Target Folder:", style="Header.TLabel").pack(side='left')
        ttk.Entry(dir_frame, textvariable=self.target_dir, width=50).pack(side='left', padx=10)
        ttk.Button(dir_frame, text="Browse...", command=self.browse_folder).pack(side='left')

        # Action Buttons
        btn_frame = ttk.Frame(frame)
        btn_frame.pack(fill='x', pady=20)
        
        self.btn_clean = ttk.Button(btn_frame, text="Run Clean Now (Organize)", command=self.run_clean)
        self.btn_clean.pack(side='left', padx=5)
        
        self.btn_lifecycle = ttk.Button(btn_frame, text="Run Lifecycle Cleanup", command=self.run_lifecycle)
        self.btn_lifecycle.pack(side='left', padx=5)

        self.btn_watch = ttk.Button(btn_frame, text="Start Watchdog", command=self.toggle_watchdog)
        self.btn_watch.pack(side='left', padx=5)

        # Logs
        log_frame = ttk.LabelFrame(frame, text="Activity Log", padding=10)
        log_frame.pack(fill='both', expand=True, pady=10)
        
        self.log_text = scrolledtext.ScrolledText(log_frame, height=10, state='normal', font=('Consolas', 9))
        self.log_text.pack(fill='both', expand=True)

    def _init_settings(self, parent):
        frame = ttk.Frame(parent, padding=20)
        frame.pack(fill='both', expand=True)

        # Help Text
        ttk.Label(frame, text="Manage File Mappings & Retention", style="Header.TLabel").pack(anchor='w')
        ttk.Label(frame, text="Edit config.json directly for advanced JSON handling.").pack(anchor='w', pady=5)

        # Config Display
        self.conf_text = scrolledtext.ScrolledText(frame, height=20, font=('Consolas', 10))
        self.conf_text.pack(fill='both', expand=True, pady=10)
        
        # Load current config text
        import json
        self.conf_text.insert(tk.END, json.dumps(self.config, indent=4))

        # Save Button
        ttk.Button(frame, text="Save Configuration", command=self.save_settings).pack(pady=10)

    def _setup_logging_handler(self):
        class TextHandler(logging.Handler):
            def __init__(self, text_widget):
                super().__init__()
                self.text_widget = text_widget
            def emit(self, record):
                msg = self.format(record)
                def append():
                    self.text_widget.insert(tk.END, msg + '\n')
                    self.text_widget.see(tk.END)
                self.text_widget.after(0, append)

        logger = logging.getLogger()
        handler = TextHandler(self.log_text)
        handler.setFormatter(logging.Formatter('%(asctime)s - %(levelname)s - %(message)s'))
        logger.addHandler(handler)

    def browse_folder(self):
        folder = filedialog.askdirectory()
        if folder:
            self.target_dir.set(folder)

    def get_janitor(self):
        return SmartFileJanitor(self.target_dir.get(), interactive=False) # GUI implies interactive enough

    def run_clean(self):
        print(f"--- Starting Manual Scan on {self.target_dir.get()} ---")
        janitor = self.get_janitor()
        threading.Thread(target=janitor.organize, daemon=True).start()

    def run_lifecycle(self):
        if not messagebox.askyesno("Confirm", "This will delete old files based on retention policy. Proceed?"):
            return
        print(f"--- Starting Lifecycle Cleanup on {self.target_dir.get()} ---")
        janitor = self.get_janitor()
        threading.Thread(target=janitor.cleanup_old_files, daemon=True).start()

    def toggle_watchdog(self):
        if self.observer:
            # Stop
            self.observer.stop()
            self.observer.join()
            self.observer = None
            self.btn_watch.config(text="Start Watchdog")
            print("--- Watchdog Stopped ---")
        else:
            # Start
            path = self.target_dir.get()
            janitor = self.get_janitor()
            event_handler = JanitorHandler(janitor)
            self.observer = Observer()
            self.observer.schedule(event_handler, path, recursive=False)
            try:
                self.observer.start()
                self.btn_watch.config(text="Stop Watchdog")
                print(f"--- Watchdog Started on {path} ---")
            except Exception as e:
                messagebox.showerror("Error", f"Failed to start watchdog: {e}")
                self.observer = None

    def save_settings(self):
        import json
        try:
            raw_text = self.conf_text.get("1.0", tk.END)
            new_config = json.loads(raw_text)
            save_config(new_config)
            # Reload to apply changes in config.py globals? 
            # Note: This simple reload might not update config.py constants imported elsewhere effectively without restart
            # ideally we reload module or access config via function. 
            # For now, we notify user.
            messagebox.showinfo("Success", "Settings saved! Restart app to fully apply changes.")
        except json.JSONDecodeError as e:
            messagebox.showerror("Error", f"Invalid JSON: {e}")

if __name__ == "__main__":
    try:
        root = tk.Tk()
        app = JanitorGUI(root)
        root.mainloop()
    except KeyboardInterrupt:
        sys.exit()
