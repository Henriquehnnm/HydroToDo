import curses
import sqlite3
import os
from datetime import datetime

# HydroToDo Stable
# Characters for rounded border
TL = '╭'
TR = '╮'
BL = '╰'
BR = '╯'
H  = '─'
V  = '│'

DB_PATH = os.path.join(os.path.expanduser("~"), '.hydrotodo.db')

ASCII_TITLE = [
    "██╗  ██╗██╗   ██╗██████╗ ██████╗  ██████╗ ████████╗ ██████╗ ██████╗  ██████╗ ",
    "██║  ██║╚██╗ ██╔╝██╔══██╗██╔══██╗██╔═══██╗╚══██╔══╝██╔═══██╗██╔══██╗██╔═══██╗",
    "███████║ ╚████╔╝ ██║  ██║██████╔╝██║   ██║   ██║   ██║   ██║██║  ██║██║   ██║",
    "██╔══██║  ╚██╔╝  ██║  ██║██╔══██╗██║   ██║   ██║   ██║   ██║██║  ██║██║   ██║",
    "██║  ██║   ██║   ██████╔╝██║  ██║╚██████╔╝   ██║   ╚██████╔╝██████╔╝╚██████╔╝",
    "╚═╝  ╚═╝   ╚═╝   ╚═════╝ ╚═╝  ╚═╝ ╚═════╝    ╚═╝    ╚═════╝ ╚═════╝  ╚═════╝ ",
    "                                                                              "
]


def init_db():
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS todos (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    text TEXT NOT NULL,
                    done INTEGER NOT NULL DEFAULT 0,
                    category TEXT NOT NULL DEFAULT 'General',
                    notes TEXT NOT NULL DEFAULT '',
                    created_at TEXT,
                    note_updated_at TEXT
                )''')
    c.execute('''CREATE TABLE IF NOT EXISTS deleted_categories (
                    name TEXT PRIMARY KEY
                )''')
    c.execute("PRAGMA table_info(todos)")
    columns = [row[1] for row in c.fetchall()]
    if 'category' not in columns:
        c.execute("ALTER TABLE todos ADD COLUMN category TEXT NOT NULL DEFAULT 'General'")
    if 'notes' not in columns:
        c.execute("ALTER TABLE todos ADD COLUMN notes TEXT NOT NULL DEFAULT ''")
    if 'created_at' not in columns:
        c.execute("ALTER TABLE todos ADD COLUMN created_at TEXT")
    if 'note_updated_at' not in columns:
        c.execute("ALTER TABLE todos ADD COLUMN note_updated_at TEXT")
    conn.commit()
    conn.close()


def load_todos(category='General'):
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute('SELECT id, text, done, notes, created_at, note_updated_at FROM todos WHERE category = ?', (category,))
    todos = [{
        'id': row[0],
        'text': row[1],
        'done': bool(row[2]),
        'notes': row[3],
        'created_at': row[4],
        'note_updated_at': row[5]
    } for row in c.fetchall()]
    conn.close()
    return todos


def add_todo(text, category='General'):
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    created_at = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    c.execute('INSERT INTO todos (text, done, category, created_at) VALUES (?, 0, ?, ?)', (text, category, created_at))
    conn.commit()
    conn.close()


def update_todo_done(todo_id, done):
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute('UPDATE todos SET done = ? WHERE id = ?', (int(done), todo_id))
    conn.commit()
    conn.close()


def delete_todo(todo_id):
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute('DELETE FROM todos WHERE id = ?', (todo_id,))
    conn.commit()
    conn.close()


def update_todo_notes(todo_id, notes):
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    note_updated_at = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    c.execute('UPDATE todos SET notes = ?, note_updated_at = ? WHERE id = ?', (notes, note_updated_at, todo_id))
    conn.commit()
    conn.close()


def add_deleted_category(cat):
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute('INSERT OR IGNORE INTO deleted_categories (name) VALUES (?)', (cat,))
    conn.commit()
    conn.close()


def remove_deleted_category(cat):
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute('DELETE FROM deleted_categories WHERE name = ?', (cat,))
    conn.commit()
    conn.close()


def delete_todos_by_category(category):
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute('DELETE FROM todos WHERE category = ?', (category,))
    conn.commit()
    conn.close()


def draw_rounded_box(win, y, x, h, w):
    win.addstr(y, x, TL + H * (w - 2) + TR)
    for i in range(1, h - 1):
        win.addstr(y + i, x, V)
        win.addstr(y + i, x + w - 1, V)
    win.addstr(y + h - 1, x, BL + H * (w - 2) + BR)


def wrap_text(text, width):
    """Wrap text to fit within a given width, returning a list of lines."""
    if width <= 0:
        return [text]
    lines = []
    while len(text) > width:
        # Find the last space within the width limit
        split_at = text.rfind(' ', 0, width)
        if split_at == -1:
            # No space found, hard break at width
            split_at = width
        lines.append(text[:split_at])
        text = text[split_at:].lstrip()
    if text:
        lines.append(text)
    return lines if lines else ['']


def get_wrapped_input(stdscr, start_y, start_x, width, max_lines, prompt=""):
    """Get user input with text wrapping support."""
    curses.curs_set(2)  # Block cursor
    text = ""

    while True:
        # Clear the input area
        for i in range(max_lines):
            stdscr.addstr(start_y + i, start_x, " " * width)

        # Display prompt and wrapped text
        full_text = prompt + text
        wrapped = wrap_text(full_text, width)

        for i, line in enumerate(wrapped[:max_lines]):
            stdscr.addstr(start_y + i, start_x, line)

        # Position cursor at the end of text
        if wrapped:
            cursor_line = min(len(wrapped) - 1, max_lines - 1)
            cursor_col = len(wrapped[cursor_line])
            stdscr.move(start_y + cursor_line, start_x + cursor_col)

        stdscr.refresh()
        key = stdscr.getch()

        if key == ord('\n'):  # Enter - submit
            break
        elif key == 27:  # Escape - cancel
            text = ""
            break
        elif key in (curses.KEY_BACKSPACE, 127, 8):  # Backspace
            if text:
                text = text[:-1]
        elif key >= 32 and key <= 126:  # Printable ASCII
            text += chr(key)

    curses.curs_set(0)  # Hide cursor
    return text


def edit_multiline_text(stdscr, start_y, start_x, width, height, initial_text=""):
    """Edit multiline text with basic navigation. Returns edited text or None if cancelled."""
    curses.curs_set(2)  # Block cursor
    lines = initial_text.split('\n') if initial_text else ['']
    cursor_line = len(lines) - 1
    cursor_col = len(lines[cursor_line])
    scroll_offset = 0

    while True:
        # Adjust scroll to keep cursor visible
        if cursor_line < scroll_offset:
            scroll_offset = cursor_line
        elif cursor_line >= scroll_offset + height:
            scroll_offset = cursor_line - height + 1

        # Clear and draw the text area
        for i in range(height):
            stdscr.addstr(start_y + i, start_x, " " * width)
            line_idx = scroll_offset + i
            if line_idx < len(lines):
                display_line = lines[line_idx][:width]
                stdscr.addstr(start_y + i, start_x, display_line)

        # Position cursor
        screen_cursor_line = cursor_line - scroll_offset
        screen_cursor_col = min(cursor_col, width - 1)
        stdscr.move(start_y + screen_cursor_line, start_x + screen_cursor_col)

        stdscr.refresh()
        key = stdscr.getch()

        if key == 27:  # Escape - cancel
            curses.curs_set(0)
            return None
        elif key == 6:  # Ctrl+F - save and finish
            curses.curs_set(0)
            return '\n'.join(lines)
        elif key == ord('\n'):  # Enter - new line
            # Split line at cursor
            rest = lines[cursor_line][cursor_col:]
            lines[cursor_line] = lines[cursor_line][:cursor_col]
            lines.insert(cursor_line + 1, rest)
            cursor_line += 1
            cursor_col = 0
        elif key in (curses.KEY_BACKSPACE, 127, 8):  # Backspace
            if cursor_col > 0:
                lines[cursor_line] = lines[cursor_line][:cursor_col-1] + lines[cursor_line][cursor_col:]
                cursor_col -= 1
            elif cursor_line > 0:
                # Merge with previous line
                cursor_col = len(lines[cursor_line - 1])
                lines[cursor_line - 1] += lines[cursor_line]
                lines.pop(cursor_line)
                cursor_line -= 1
        elif key == curses.KEY_DC:  # Delete
            if cursor_col < len(lines[cursor_line]):
                lines[cursor_line] = lines[cursor_line][:cursor_col] + lines[cursor_line][cursor_col+1:]
            elif cursor_line < len(lines) - 1:
                # Merge with next line
                lines[cursor_line] += lines[cursor_line + 1]
                lines.pop(cursor_line + 1)
        elif key == curses.KEY_UP:
            if cursor_line > 0:
                cursor_line -= 1
                cursor_col = min(cursor_col, len(lines[cursor_line]))
        elif key == curses.KEY_DOWN:
            if cursor_line < len(lines) - 1:
                cursor_line += 1
                cursor_col = min(cursor_col, len(lines[cursor_line]))
        elif key == curses.KEY_LEFT:
            if cursor_col > 0:
                cursor_col -= 1
            elif cursor_line > 0:
                cursor_line -= 1
                cursor_col = len(lines[cursor_line])
        elif key == curses.KEY_RIGHT:
            if cursor_col < len(lines[cursor_line]):
                cursor_col += 1
            elif cursor_line < len(lines) - 1:
                cursor_line += 1
                cursor_col = 0
        elif key == curses.KEY_HOME:
            cursor_col = 0
        elif key == curses.KEY_END:
            cursor_col = len(lines[cursor_line])
        elif key >= 32 and key <= 126:  # Printable ASCII
            lines[cursor_line] = lines[cursor_line][:cursor_col] + chr(key) + lines[cursor_line][cursor_col:]
            cursor_col += 1

    curses.curs_set(0)
    return '\n'.join(lines)


def get_all_categories():
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute('SELECT DISTINCT category FROM todos')
    cats = [row[0] for row in c.fetchall()]
    c.execute('SELECT name FROM deleted_categories')
    deleted = set(row[0] for row in c.fetchall())
    conn.close()
    filtered = [cat for cat in cats if cat not in deleted]
    return filtered if filtered else ['General']


def main(stdscr):
    curses.curs_set(0)
    stdscr.clear()
    curses.start_color()
    curses.use_default_colors()  # Enable using default terminal colors
    curses.init_pair(1, curses.COLOR_BLACK, -1)  # -1 means use default terminal color
    curses.init_pair(2, curses.COLOR_YELLOW, -1)
    curses.init_pair(3, curses.COLOR_GREEN, -1)
    curses.init_pair(4, curses.COLOR_MAGENTA, -1)

    init_db()
    # Structure for tabs
    tab_categories = get_all_categories()
    tabs = [load_todos(cat) for cat in tab_categories]
    current_tab = 0
    max_tabs = 10
    current_indices = [0 for _ in tab_categories]

    show_help = False
    help_lines = [
        "Available commands:",
        "",
        "↑↓         Navigate between tasks",
        "Enter      Mark/unmark task",
        "a          Add new task",
        "d          Delete selected task",
        "n          Edit notes for task",
        "Ctrl+T     New tab",
        "Ctrl+W     Close tab",
        "←/→        Switch tab",
        "h          Show/hide help",
        "q          Quit program",
        "",
        "In notes editor:",
        "Ctrl+F     Save notes",
        "Esc        Cancel editing",
    ]

    while True:
        stdscr.clear()
        height, width = stdscr.getmaxyx()

        # Minimum resolution check
        min_width = 80
        min_height = 30
        if width < min_width or height < min_height:
            msg = f"Current resolution: {width}x{height} | Minimum: {min_width}x{min_height}"
            stdscr.clear()
            msg_x = max(0, min(width - 1, (width - len(msg)) // 2))
            msg_y = min(height - 1, height // 2)
            try:
                stdscr.addstr(msg_y, msg_x, msg[:max(0, width - msg_x)], curses.color_pair(2) | curses.A_BOLD)
            except curses.error:
                pass  # ignores if the screen is too small to even draw
            stdscr.refresh()
            key = stdscr.getch()
            if key in (ord('q'), 3):  # 'q', Ctrl+C
                break
            continue


        # Title box
        title_box_w = max(len(line) for line in ASCII_TITLE) + 4
        title_box_h = len(ASCII_TITLE) + 2
        # Ensures that the box does not exceed screen limits
        if title_box_w > width:
            title_box_w = width - 2 if width > 2 else width
        if title_box_h > height:
            title_box_h = height - 2 if height > 2 else height
        title_box_x = max(0, (width - title_box_w) // 2)
        title_box_y = 1
        # Only draws if it fits on screen
        if title_box_y + title_box_h < height and title_box_x + title_box_w < width:
            draw_rounded_box(stdscr, title_box_y, title_box_x, title_box_h, title_box_w)
            for i, line in enumerate(ASCII_TITLE):
                if i + 1 + title_box_y < height and title_box_x + 2 < width:
                    stdscr.addstr(title_box_y + 1 + i, title_box_x + 2, line[:max(0, width - title_box_x - 4)], curses.color_pair(3) | curses.A_BOLD)

        if show_help:
            # Centered help screen, but slightly lower
            help_w = max(len(line) for line in help_lines) + 4
            help_h = len(help_lines) + 2
            help_x = (width - help_w) // 2
            help_y = max(2, (height - help_h) // 2 + height // 10)  # offset downwards
            draw_rounded_box(stdscr, help_y, help_x, help_h, help_w)
            for i, line in enumerate(help_lines):
                stdscr.addstr(help_y + 1 + i, help_x + 2, line, curses.color_pair(2) | curses.A_BOLD)
        else:
            # Tabs at the top (better highlight)
            tab_strs = []
            for i, cat in enumerate(tab_categories):
                if i == current_tab:
                    tab_strs.append(f"╭─[{cat}]─╮")
                else:
                    tab_strs.append(f"  {cat}  ")
            tab_bar = " ".join(tab_strs)
            stdscr.addstr(title_box_y + title_box_h, max(0, (width - len(tab_bar)) // 2), tab_bar, curses.color_pair(2) | curses.A_BOLD)

            # Calculate available space for task box and detail panel
            available_height = height - title_box_h - 6  # Leave room for help hint
            box_h = 8  # Shorter fixed height for task box
            detail_panel_h = max(10, available_height - box_h - 1)  # Detail panel gets remaining space

            # Main tab box (same width as title box)
            box_w = title_box_w
            box_x = title_box_x
            box_y = title_box_y + title_box_h + 2
            draw_rounded_box(stdscr, box_y, box_x, box_h, box_w)
            todos = tabs[current_tab]
            # Ensures the selected index is within the list size
            if current_indices[current_tab] >= len(todos):
                current_indices[current_tab] = max(0, len(todos) - 1)
            current_index = current_indices[current_tab]
            # SCROLL for tasks
            max_visible = max(1, box_h - 4)
            if len(todos) > max_visible:
                if current_index < max_visible // 2:
                    start = 0
                elif current_index > len(todos) - (max_visible // 2):
                    start = len(todos) - max_visible
                else:
                    start = current_index - max_visible // 2
                end = start + max_visible
            else:
                start = 0
                end = len(todos)
            if len(todos) == 0:
                msg = "No tasks yet..."
                msg_y = box_y + (box_h // 2)
                msg_x = box_x + ((box_w - len(msg)) // 2)
                stdscr.addstr(msg_y, msg_x, msg, curses.color_pair(2) | curses.A_BOLD)
            elif len(todos) > 0:
                display_line = 0
                text_width = box_w - 4  # Account for border and padding
                indent = "    "  # Indent for wrapped lines (same width as prefix)
                for idx, i in enumerate(range(start, end)):
                    if 0 <= i < len(todos) and display_line < max_visible:
                        todo = todos[i]
                        prefix = "[X] " if todo['done'] else "[ ] "
                        attr = curses.color_pair(2) | curses.A_BOLD if i == current_index else 0
                        # Wrap the todo text
                        wrapped_lines = wrap_text(todo['text'], text_width - len(prefix))
                        for line_idx, line_text in enumerate(wrapped_lines):
                            if display_line >= max_visible:
                                break
                            if line_idx == 0:
                                line = prefix + line_text
                            else:
                                line = indent + line_text
                            stdscr.addstr(box_y + 2 + display_line, box_x + 2, line[:text_width], attr)
                            display_line += 1
            # Scroll indicators for tasks (on the right side)
            if start > 0:
                stdscr.addstr(box_y + 1, box_x + box_w - 3, '↑', curses.color_pair(2) | curses.A_BOLD)
            if end < len(todos):
                stdscr.addstr(box_y + box_h - 2, box_x + box_w - 3, '↓', curses.color_pair(2) | curses.A_BOLD)

            # Detail panel below task box
            detail_y = box_y + box_h + 1
            detail_w = box_w
            detail_x = box_x
            draw_rounded_box(stdscr, detail_y, detail_x, detail_panel_h, detail_w)

            if len(todos) > 0 and 0 <= current_index < len(todos):
                selected_todo = todos[current_index]
                detail_text_w = detail_w - 4

                # Show task name at top of detail panel (with wrapping)
                task_label = "Task: "
                task_text = selected_todo['text']
                stdscr.addstr(detail_y + 1, detail_x + 2, task_label, curses.color_pair(3) | curses.A_BOLD)

                # Wrap the task title
                task_wrapped = wrap_text(task_text, detail_text_w - len(task_label))
                task_display_lines = 0
                for i, line in enumerate(task_wrapped[:2]):  # Max 2 lines for task title
                    if i == 0:
                        stdscr.addstr(detail_y + 1, detail_x + 2 + len(task_label), line)
                    else:
                        stdscr.addstr(detail_y + 1 + i, detail_x + 2, " " * len(task_label) + line)
                    task_display_lines += 1

                # Created date
                created_y = detail_y + 1 + task_display_lines
                created_label = "Created: "
                created_at = selected_todo.get('created_at', '')
                if created_at:
                    stdscr.addstr(created_y, detail_x + 2, created_label, curses.color_pair(4) | curses.A_BOLD)
                    stdscr.addstr(created_y, detail_x + 2 + len(created_label), created_at)
                else:
                    stdscr.addstr(created_y, detail_x + 2, created_label, curses.color_pair(4) | curses.A_BOLD)
                    stdscr.addstr(created_y, detail_x + 2 + len(created_label), "(unknown)")

                # Separator line
                sep_y = created_y + 1
                stdscr.addstr(sep_y, detail_x + 2, H * (detail_text_w), curses.color_pair(1))

                # Notes section with timestamp
                note_updated_at = selected_todo.get('note_updated_at', '')
                if note_updated_at:
                    notes_label = f"Notes: (edited {note_updated_at}) - press 'n' to edit"
                else:
                    notes_label = "Notes: (press 'n' to edit)"
                # Truncate if too long
                notes_label = notes_label[:detail_text_w]
                stdscr.addstr(sep_y + 1, detail_x + 2, notes_label, curses.color_pair(2) | curses.A_BOLD)

                # Calculate notes area
                notes_start_y = sep_y + 2
                max_notes_lines = detail_panel_h - (notes_start_y - detail_y) - 1  # Lines available for notes

                # Build all wrapped notes lines
                notes = selected_todo.get('notes', '')
                all_notes_lines = []
                if notes:
                    for note_line in notes.split('\n'):
                        wrapped = wrap_text(note_line, detail_text_w) if note_line else ['']
                        all_notes_lines.extend(wrapped)

                # Display notes with scrolling (auto-scroll to show content)
                if all_notes_lines:
                    total_notes_lines = len(all_notes_lines)
                    # For now, show from the beginning (scrolling will be in edit mode)
                    notes_start = 0
                    notes_end = min(notes_start + max_notes_lines, total_notes_lines)

                    for i, line in enumerate(all_notes_lines[notes_start:notes_end]):
                        stdscr.addstr(notes_start_y + i, detail_x + 2, line)

                    # Scroll indicators for notes (on the right side)
                    if notes_start > 0:
                        stdscr.addstr(notes_start_y, detail_x + detail_w - 3, '↑', curses.color_pair(2) | curses.A_BOLD)
                    if notes_end < total_notes_lines:
                        stdscr.addstr(notes_start_y + max_notes_lines - 1, detail_x + detail_w - 3, '↓', curses.color_pair(2) | curses.A_BOLD)
                else:
                    stdscr.addstr(notes_start_y, detail_x + 2, "(no notes)", curses.color_pair(1))
            else:
                # No task selected
                msg = "Select a task to view details"
                stdscr.addstr(detail_y + detail_panel_h // 2, detail_x + (detail_w - len(msg)) // 2, msg, curses.color_pair(1))

        # Minimal help command
        help_hint = "Press 'h' for help"
        stdscr.addstr(height - 2, max(0, (width - len(help_hint)) // 2), help_hint, curses.color_pair(4) | curses.A_BOLD)

        stdscr.refresh()
        key = stdscr.getch()

        # Tab shortcuts
        if key == 20:  # Ctrl+T
            if len(tabs) < max_tabs:
                cat = get_wrapped_input(stdscr, height - 4, 2, width - 4, 1, "New category name: ").strip()
                if cat and cat not in tab_categories:
                    remove_deleted_category(cat)
                    tab_categories.append(cat)
                    tabs.append(load_todos(cat))
                    current_indices.append(0)
                    current_tab = len(tabs) - 1
        elif key == 23:  # Ctrl+W
            if len(tabs) > 1:
                add_deleted_category(tab_categories[current_tab])
                delete_todos_by_category(tab_categories[current_tab])
                tab_categories.pop(current_tab)
                tabs.pop(current_tab)
                current_indices.pop(current_tab)
                if current_tab >= len(tabs):
                    current_tab = len(tabs) - 1
        elif key == 545:  # Ctrl+Left
            if current_tab > 0:
                current_tab -= 1
        elif key == 560:  # Ctrl+Right
            if current_tab < len(tabs) - 1:
                current_tab += 1
        elif key == curses.KEY_LEFT:
            if current_tab > 0:
                current_tab -= 1
        elif key == curses.KEY_RIGHT:
            if current_tab < len(tabs) - 1:
                current_tab += 1
        elif key == ord('h'):
            show_help = not show_help
        elif key == ord('q'):
            break
        elif key == curses.KEY_UP:
            if current_indices[current_tab] > 0:
                current_indices[current_tab] -= 1
        elif key == curses.KEY_DOWN:
            if current_indices[current_tab] < len(tabs[current_tab]) - 1:
                current_indices[current_tab] += 1
        elif key == ord('\n') and tabs[current_tab]:
            todos = tabs[current_tab]
            idx = current_indices[current_tab]
            if 0 <= idx < len(todos):
                todos[idx]['done'] = not todos[idx]['done']
                update_todo_done(todos[idx]['id'], todos[idx]['done'])
                # Update tab list
                tabs[current_tab] = load_todos(tab_categories[current_tab])
        elif key == ord('a'):
            box_y = title_box_y + title_box_h + 2
            box_x = title_box_x
            box_w = title_box_w
            box_h = min(max(10, len(tabs[current_tab]) + 5), height - title_box_h - 7)
            input_width = box_w - 4
            max_input_lines = 3  # Allow up to 3 lines for input
            text = get_wrapped_input(stdscr, box_y + box_h - 4, box_x + 2, input_width, max_input_lines, "New task: ")
            if text.strip():
                add_todo(text, tab_categories[current_tab])
                tabs[current_tab] = load_todos(tab_categories[current_tab])
                current_indices[current_tab] = len(tabs[current_tab]) - 1
        elif key == ord('d') and tabs[current_tab]:
            todos = tabs[current_tab]
            idx = current_indices[current_tab]
            if 0 <= idx < len(todos):
                delete_todo(todos[idx]['id'])
                tabs[current_tab] = load_todos(tab_categories[current_tab])
                # Adjust index so it does not exceed list size
                if current_indices[current_tab] >= len(tabs[current_tab]):
                    current_indices[current_tab] = max(0, len(tabs[current_tab]) - 1)
        elif key == ord('n') and tabs[current_tab]:
            todos = tabs[current_tab]
            idx = current_indices[current_tab]
            if 0 <= idx < len(todos):
                # Edit notes for selected task
                selected_todo = todos[idx]
                current_notes = selected_todo.get('notes', '')

                # Calculate detail panel position (same as drawing code)
                available_height = height - title_box_h - 6
                box_h = 8  # Matches the task box height
                detail_panel_h = max(10, available_height - box_h - 1)
                detail_y = title_box_y + title_box_h + 2 + box_h + 1
                detail_x = title_box_x
                detail_w = title_box_w

                # Calculate where notes editing area starts (after task title and separator)
                notes_edit_y = detail_y + 4  # After task title (2 lines max) + separator + notes label
                notes_edit_h = detail_panel_h - 5  # Leave room for header elements

                # Show editing hint
                edit_hint = "Editing notes... (Ctrl+F to save, Esc to cancel)"
                stdscr.addstr(detail_y + 3, detail_x + 2, edit_hint + " " * (detail_w - 4 - len(edit_hint)), curses.color_pair(3) | curses.A_BOLD)
                stdscr.refresh()

                # Edit notes in the detail panel area
                new_notes = edit_multiline_text(
                    stdscr,
                    notes_edit_y,
                    detail_x + 2,
                    detail_w - 4,
                    notes_edit_h,
                    current_notes
                )

                if new_notes is not None:
                    update_todo_notes(selected_todo['id'], new_notes)
                    tabs[current_tab] = load_todos(tab_categories[current_tab])

if __name__ == "__main__":
    try:
        curses.wrapper(main)
    except KeyboardInterrupt:
        pass  # Exits silently on Ctrl+C
