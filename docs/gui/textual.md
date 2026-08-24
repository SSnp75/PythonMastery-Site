---
title: Textual (TUI)
description: Modern terminal user interfaces — rich widgets, CSS styling and async
---

# Textual (TUI) <span class="pm-badge pm-badge-intermediate">Intermediate</span>

<div class="pm-topic-header">
  <strong>🖥️ GUI · Level 3</strong>
  <div class="pm-topic-meta">
    <span>⏱️ ~3 days</span>
  </div>
</div>

---

## What is Textual?

Textual builds beautiful terminal applications with CSS-like styling, mouse support and rich widgets — like a web framework for the terminal.

```python
from textual.app import App, ComposeResult
from textual.widgets import Header, Footer, Static, Input, Button, DataTable
from textual.containers import Container, Horizontal

class TodoApp(App):
    CSS = """
    Screen { layout: vertical; }
    #input-area { height: 3; layout: horizontal; }
    #input-area Input { width: 1fr; }
    #input-area Button { width: 15; }
    DataTable { height: 1fr; }
    """

    BINDINGS = [("q", "quit", "Quit"), ("d", "delete", "Delete")]

    def compose(self) -> ComposeResult:
        yield Header()
        with Horizontal(id="input-area"):
            yield Input(placeholder="Add a task...", id="task-input")
            yield Button("Add", variant="primary", id="add-btn")
        yield DataTable(id="tasks")
        yield Footer()

    def on_mount(self):
        table = self.query_one("#tasks", DataTable)
        table.add_columns("ID", "Task", "Status")
        self._next_id = 1

    def on_button_pressed(self, event: Button.Pressed):
        if event.button.id == "add-btn":
            self._add_task()

    def on_input_submitted(self, event: Input.Submitted):
        self._add_task()

    def _add_task(self):
        input_widget = self.query_one("#task-input", Input)
        task = input_widget.value.strip()
        if task:
            table = self.query_one("#tasks", DataTable)
            table.add_row(str(self._next_id), task, "Pending")
            self._next_id += 1
            input_widget.value = ""

if __name__ == "__main__":
    TodoApp().run()
```

```bash
pip install textual
python app.py   # renders beautiful TUI in terminal!
```

---

## Practice Exercises

1. **Build a dashboard** showing system stats (CPU, memory, disk) with live updates.
2. **Build a file browser** with tree widget and preview pane.
3. **Build a log viewer** that tails a log file with color-coded levels.
4. **Build a database explorer** — connect, browse tables, run queries.
