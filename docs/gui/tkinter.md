---
title: Tkinter
description: Built-in GUI toolkit — windows, widgets, layouts and event handling
---

# Tkinter <span class="pm-badge pm-badge-competent">Competent</span>

<div class="pm-topic-header">
  <strong>🖥️ GUI · Level 2</strong>
  <div class="pm-topic-meta">
    <span>⏱️ ~3 days</span>
  </div>
</div>

---

## Basic window

```python
import tkinter as tk
from tkinter import ttk, messagebox

class App:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("My App")
        self.root.geometry("400x300")
        self.setup_ui()

    def setup_ui(self):
        # Label
        ttk.Label(self.root, text="Enter your name:").pack(pady=10)

        # Entry (text input)
        self.name_var = tk.StringVar()
        ttk.Entry(self.root, textvariable=self.name_var, width=30).pack()

        # Button
        ttk.Button(self.root, text="Greet", command=self.greet).pack(pady=10)

        # Output label
        self.output = ttk.Label(self.root, text="")
        self.output.pack()

    def greet(self):
        name = self.name_var.get()
        if name:
            self.output.config(text=f"Hello, {name}!")
        else:
            messagebox.showwarning("Input needed", "Please enter your name")

    def run(self):
        self.root.mainloop()

if __name__ == "__main__":
    App().run()
```

---

## Common widgets

```python
# Combobox (dropdown)
combo = ttk.Combobox(root, values=["Option 1", "Option 2", "Option 3"])
combo.pack()

# Listbox with scrollbar
frame = ttk.Frame(root)
scrollbar = ttk.Scrollbar(frame)
listbox = tk.Listbox(frame, yscrollcommand=scrollbar.set)
scrollbar.config(command=listbox.yview)
for i in range(50):
    listbox.insert(tk.END, f"Item {i}")
listbox.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
frame.pack(fill=tk.BOTH, expand=True)

# Progress bar
progress = ttk.Progressbar(root, length=300, mode="determinate")
progress["value"] = 60
progress.pack()

# File dialog
from tkinter import filedialog
path = filedialog.askopenfilename(filetypes=[("Python files", "*.py")])
```

---

## Practice Exercises

1. **Build a calculator** with button grid and display.
2. **Build a to-do app** with add, delete, mark complete.
3. **Build a file explorer** that shows directory contents in a Listbox.
4. **Build a text editor** with open, save, find/replace.
