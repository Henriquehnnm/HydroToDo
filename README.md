<h1 align="center">HydroToDo</h1>

<p align="center">
  <b>HydroToDo</b> is a stylish, terminal-based task manager written in Python.<br>
  It allows you to organize, check off, and visualize your to-dos efficiently using a modern Text User Interface (TUI) built with <code>curses</code>.<br>
  With features like tabbed lists, interactive help, and keyboard shortcuts, HydroToDo brings ease and clarity to your daily workflow.
</p>

---

## Features

- **Add, Remove, and Complete Tasks:**  
  Easily manage your to-do list—add new tasks, mark as done, or delete with a keystroke.
- **Tabbed Lists:**  
  Organize your tasks into multiple categories, each in its own tab.
- **ASCII Rounded Box UI:**  
  Tasks are displayed in visually appealing boxes with rounded ASCII borders for readability.
- **Interactive Help:**  
  Quickly access shortcut keys and usage instructions from within the app.
- **Keyboard Shortcuts:**  
  Fast navigation and task management using intuitive hotkeys.
- **Live Updates:**  
  Your task list refreshes dynamically with every change.
- **Responsive Design:**  
  Handles terminal resizing and warns if the window is too small.

---

## Preview

<p align="center">
  <img src="screenshot.png" alt="HydroToDo Screenshot" width="700"/>
</p>

---

## Requirements

- **Python**: Version 3.6 or higher
- **sqlite3**: Standard library (included with Python)
- **curses**: Terminal interface (native on Linux/macOS/WSL)

> **Note:** Officially supported on Linux, macOS, and WSL.  
> Windows users may try running HydroToDo with the `windows-curses` package, but compatibility and support are **not guaranteed**.

---

## Installation

Clone the repository and navigate to the project folder:

```bash
git clone https://github.com/Henriquehnnm/HydroToDo.git
cd HydroToDo
```
If on Windows:
```bash
pip install windows-curses
```

---

## Usage

Run the script directly from your terminal:

```bash
python3 hydrotodo.py
```

### Main Shortcuts

- <kbd>↑</kbd>/<kbd>↓</kbd> : Navigate tasks
- <kbd>Enter</kbd>           : Check/uncheck task
- <kbd>a</kbd>               : Add new task
- <kbd>d</kbd>               : Delete selected task
- <kbd>Ctrl+T</kbd>          : New tab (category)
- <kbd>Ctrl+W</kbd>          : Close current tab
- <kbd>←</kbd>/<kbd>→</kbd>  : Switch tabs
- <kbd>h</kbd>               : Show/hide help
- <kbd>q</kbd>               : Quit the app

---

## Code Structure

- **Interactive TUI:**  
  Built with the `curses` library for a smooth and keyboard-driven experience.
- **Rounded Box Drawing:**  
  Custom functions for rendering rounded ASCII boxes.
- **SQLite Persistence:**  
  Tasks are stored locally in a SQLite database for reliability.
- **Tabs and Shortcuts:**  
  Multiple categories managed via tabs and keyboard shortcuts.
- **Error Handling:**  
  Graceful handling of very small terminals and input errors.

---

## Contributing

HydroToDo is under active development and currently in **Beta**.  
Suggestions and contributions are welcome via [issues](https://github.com/Henriquehnnm/HydroToDo/issues) or [pull requests](https://github.com/Henriquehnnm/HydroToDo/pulls).

---

## Contact

For questions or suggestions, please [open an issue](https://github.com/Henriquehnnm/HydroToDo/issues) or contact via email.
