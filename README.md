# Smart File Janitor (SFJ)

> *"Computers are so cool man, I mean genuinely a blessing for me."*

## Overview
The **Smart File Janitor (SFJ)** is a Python-based automation utility designed to keep your digital life organized. It replaces manual file sorting with a smart, rule-based engine that automatically triages incoming data, cleans up clutter, and maintains directory hygiene.

Whether you're downloading lecture slides, saving memes, or coding late at night, SFJ ensures every file finds its perfect home instantly.

## Features
- **📂 Intelligent Triage**: Automatically routes files (PDFs, JPGs, MP3s, etc.) into dedicated folders like `Documents`, `Images`, and `Code`.
- **🛡️ Data Safety**: Never overwrites files. If a duplicate exists, SFJ automatically handles it with a timestamp collision protocol.
- **👀 Watchdog Mode**: distinct from manual runs, the specialized `--watch` mode monitors your folders in real-time and organizes files the moment they appear.
- **🗣️ Interactive Mode**: Want control? Enable interactive mode to confirm every move or deletion with a simple `y/n` prompt.
- **♻️ Lifecycle Management**: Keeps your workspace lean by automatically purging old temporary files or installers based on your retention policies.
- **🖥️ GUI Dashboard**: A distinct, user-friendly control panel to manage settings, run cleanups, and view logs without touching code.

## Installation

1.  **Clone the repository**:
    ```bash
    git clone https://github.com/MIR39X/SmartFileJanitor
    cd SFS_V0.0
    ```

2.  **Install Dependencies**:
    SFJ requires the `watchdog` library for real-time monitoring.
    ```bash
    pip install watchdog
    ```
    *(Note: Tkinter is usually pre-installed with Python on Windows)*

## Usage

### 🖥️ The Dashboard (Recommended)
Run the graphical interface for the easiest experience:
```bash
python gui.py
```
From here you can:
*   **Run Clean Now**: One-click organization.
*   **Start Watchdog**: Enable background monitoring.
*   **Settings**: Edit your folder mappings and rules visually.

### 💻 Command Line Interface (CLI)

**Standard Cleanup**:
Pop up a folder selector to choose what to clean.
```bash
python main.py
```

**Background Monitoring**:
Watch the current directory and organize files instantly.
```bash
python main.py --watch
```

**Interactive Safety Mode**:
Ask for permission before moving each file.
```bash
python main.py --interactive
```

**Lifecycle Cleanup**:
Delete files older than 30 days (based on config).
```bash
python main.py --clean
```

## Configuration
Modify `config.json` to customize your experience.

```json
{
    "EXTENSION_MAP": {
        "Documents": [".pdf", ".docx"],
        "Images": [".jpg", ".png"]
    },
    "RETENTION_POLICIES": {
        "Installers": 30,
        "Temp": 7
    }
}
```

---
*Automate the boring stuff, so you can focus on the cool stuff.*
