import tkinter as tk
from tkinter import ttk
import os
import sys
import shutil

import matplotlib.pyplot as plt
import sympy as sp
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from PIL import Image, ImageTk

try:
    from ctypes import windll
    windll.shcore.SetProcessDpiAwareness(1)
except Exception:
    pass

root = tk.Tk()
root.title("Temperature Conversion Calculator")
root.state("zoomed")
root.minsize(900, 600)
root.config(bg="#f0f0f0")

COLOR_THEMES = {
    "Light": {
        "main_bg": "#f7f7f7",
        "frame_bg": "#ffffff",
        "step_bg1": "#eef4fb",
        "step_bg2": "#f5f5f5",
        "separator": "#bdbdbd",
        "button_bg": "#e6f0ff",
        "operations_bg": "#7db3df",
        "variables_bg": "#b7d7f0",
        "utility_bg": "#d9534f",
        "utility_fg": "white",
        "compute_bg": "#3a5fcf",
        "compute_fg": "white",
        "compute_active_bg": "#2f4db5",
        "text_color": "#1a1a1a",
        "error_color": "#c62828",
        "sidenav_bg": "#f2f2f2",
        "sidenav_header_bg": "#dcdcdc",
        "highlight_terms": "blue",
    },
    "Dark": {
        "main_bg": "#1e1e1e",
        "frame_bg": "#333333",
        "step_bg1": "#262626",
        "step_bg2": "#2f2f2f",
        "separator": "#4d4d4d",
        "button_bg": "#3a3a3a",
        "operations_bg": "#425e88",
        "variables_bg": "#7aaec7",
        "variables_fg": "black",
        "utility_bg": "#e57373",
        "utility_fg": "black",
        "compute_bg": "#2952a3",
        "compute_fg": "white",
        "compute_active_bg": "#1f3f7a",
        "text_color": "#e0e0e0",
        "error_color": "#ff4444",
        "sidenav_bg": "#2b2b2b",
        "sidenav_header_bg": "#1f1f1f",
        "highlight_terms": "#4a90e2",
    },
    "Pink": {
        "main_bg": "#fff1f5",
        "frame_bg": "#ffeaf0",
        "step_bg1": "#ffebf1",
        "step_bg2": "#fff3f8",
        "separator": "#ff9dbb",
        "button_bg": "#fff2f6",
        "operations_bg": "#ffc9da",
        "variables_bg": "#ffbdd0",
        "utility_bg": "#d81b60",
        "utility_fg": "white",
        "compute_bg": "#ff5ca8",
        "compute_fg": "white",
        "compute_active_bg": "#e04090",
        "text_color": "#7a003c",
        "error_color": "#c2185b",
        "sidenav_bg": "#ffe5ed",
        "sidenav_header_bg": "#ffc6d9",
        "highlight_terms": "#ff2e63",
    },
    "Orange": {
        "main_bg": "#fff6ed",
        "frame_bg": "#fff2e6",
        "step_bg1": "#fff3e8",
        "step_bg2": "#fff8f0",
        "separator": "#ffcfa3",
        "button_bg": "#fff1e1",
        "operations_bg": "#ffe0bf",
        "variables_bg": "#ffcb99",
        "utility_bg": "#e64a19",
        "utility_fg": "white",
        "compute_bg": "#ff7a00",
        "compute_fg": "white",
        "compute_active_bg": "#cc5e00",
        "text_color": "#663300",
        "error_color": "#d84315",
        "sidenav_bg": "#fff1e0",
        "sidenav_header_bg": "#ffd2a6",
        "highlight_terms": "#ff6d00",
    },
}

current_theme = "Light"
theme_colors = COLOR_THEMES[current_theme]
calculation_history = []
sidenav_visible = False
sidenav_width = 460
current_sidenav_content = None
root.selected_target = None
root.current_step_data = None

main_container = tk.Frame(root, bg=theme_colors["main_bg"])
main_container.pack(fill=tk.BOTH, expand=True)

main_container.grid_rowconfigure(0, weight=1)
main_container.grid_columnconfigure(0, weight=0, minsize=sidenav_width)  # sidenav 
main_container.grid_columnconfigure(1, weight=1)  # left panel
main_container.grid_columnconfigure(2, weight=0)  # separator
main_container.grid_columnconfigure(3, weight=1)  # right panel

sidenav_frame = tk.Frame(main_container, bg=theme_colors["sidenav_bg"], width=sidenav_width)
sidenav_frame.grid_propagate(False)
sidenav_frame.grid(row=0, column=0, sticky="nsew")
sidenav_visible = True

main_frame = main_container

left_frame = tk.Frame(main_container, bg=theme_colors["frame_bg"], relief=tk.RIDGE, bd=2)
left_frame.grid(row=0, column=1, sticky="nsew")
left_frame.grid_propagate(False)

separator = tk.Frame(main_container, width=4, bg=theme_colors["separator"])
separator.grid(row=0, column=2, sticky="ns")

right_frame = tk.Frame(main_container, bg=theme_colors["frame_bg"], relief=tk.RIDGE, bd=2)
right_frame.grid(row=0, column=3, sticky="nsew")
right_frame.grid_propagate(False)

left_content_frame = tk.Frame(left_frame, bg=theme_colors["frame_bg"], padx=15, pady=8)
left_content_frame.pack(fill=tk.BOTH, expand=True)

right_content_frame = tk.Frame(right_frame, bg=theme_colors["frame_bg"], padx=12, pady=8)
right_content_frame.pack(fill=tk.BOTH, expand=True)

# Right panel header
steps_header_frame = tk.Frame(right_content_frame, bg=theme_colors["frame_bg"])
steps_header_frame.pack(fill=tk.X, pady=(10, 10))

steps_label = tk.Label(
    steps_header_frame,
    text="Temperature Conversion Steps",
    font=("Verdana Bold", 13),
    bg=theme_colors["frame_bg"],
    fg=theme_colors["text_color"],
)
steps_label.pack(pady=0)

tk.Frame(right_content_frame, height=2, bg=theme_colors["separator"]).pack(fill=tk.X, pady=(0, 4))

_steps_outer = tk.Frame(right_content_frame, bg=theme_colors["frame_bg"])
_steps_outer.pack(fill=tk.BOTH, expand=True)

steps_canvas = tk.Canvas(_steps_outer, bg=theme_colors["frame_bg"], highlightthickness=0)
steps_scrollbar = tk.Scrollbar(_steps_outer, orient=tk.VERTICAL, command=steps_canvas.yview)
steps_canvas.configure(yscrollcommand=steps_scrollbar.set)
steps_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
steps_canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

steps_scrollable_frame = tk.Frame(steps_canvas, bg=theme_colors["frame_bg"])
_steps_window = steps_canvas.create_window((0, 0), window=steps_scrollable_frame, anchor="nw")

def _on_steps_inner_resize(event):
    steps_canvas.configure(scrollregion=steps_canvas.bbox("all"))

def _on_steps_canvas_resize(event):
    steps_canvas.itemconfig(_steps_window, width=event.width)

steps_scrollable_frame.bind("<Configure>", _on_steps_inner_resize)
steps_canvas.bind("<Configure>", _on_steps_canvas_resize)

def _steps_mousewheel(event):
    steps_canvas.yview_scroll(int(-1 * (event.delta / 120)), "units")

steps_canvas.bind("<Enter>", lambda e: steps_canvas.bind_all("<MouseWheel>", _steps_mousewheel))
steps_canvas.bind("<Leave>", lambda e: steps_canvas.unbind_all("<MouseWheel>"))

# Left panel header
header_frame = tk.Frame(left_content_frame, bg=theme_colors["frame_bg"])
header_frame.pack(fill=tk.X, pady=(0, 10))

calculator_title = tk.Label(
    header_frame,
    text="Temperature Calculator",
    font=("Verdana Bold", 13),
    bg=theme_colors["frame_bg"],
    fg=theme_colors["text_color"],
)
calculator_title.pack(pady=(0, 3))

tk.Frame(header_frame, height=2, bg=theme_colors["separator"]).pack(fill=tk.X, pady=(0, 10))

controls_frame = tk.Frame(header_frame, bg=theme_colors["frame_bg"])
controls_frame.pack(fill=tk.X, pady=(0, 10))

left_buttons_frame = tk.Frame(controls_frame, bg=theme_colors["frame_bg"])
left_buttons_frame.pack(side=tk.LEFT)

right_theme_frame = tk.Frame(controls_frame, bg=theme_colors["frame_bg"])
right_theme_frame.pack(side=tk.RIGHT)

theme_label = tk.Label(
    right_theme_frame,
    text="Theme:",
    font=("Helvetica", 11),
    bg=theme_colors["frame_bg"],
    fg=theme_colors["text_color"],
)
theme_label.pack(side=tk.LEFT, padx=(0, 5), pady=5)

theme_var = tk.StringVar(root, value="Light")

theme_menu = ttk.Combobox(
    right_theme_frame,
    textvariable=theme_var,
    values=list(COLOR_THEMES.keys()),
    width=9,
    state="readonly",
)
theme_menu.config(font=("Consolas", 10))
theme_menu.pack(side=tk.LEFT, padx=5, pady=5)

fig, ax = plt.subplots(figsize=(5.5, 0.8))
ax.axis("off")
canvas = FigureCanvasTkAgg(fig, master=left_content_frame)
canvas.get_tk_widget().pack(pady=(0, 10), fill=tk.X)

# Shared state
x = sp.Symbol("x")
all_buttons = []

# Input section
input_frame = tk.Frame(left_content_frame, bg=theme_colors["step_bg1"], relief=tk.GROOVE, bd=1)
input_frame.pack(pady=10, fill=tk.X, padx=5)

convert_strip = tk.Frame(input_frame, bg=theme_colors["step_bg1"])
convert_strip.pack(fill=tk.X, pady=(10, 5), padx=10)

convert_inner = tk.Frame(convert_strip, bg=theme_colors["step_bg1"])
convert_inner.pack(anchor="center")

convert_label = tk.Label(
    convert_inner,
    text="Convert to:",
    font=("Times", 12),
    bg=theme_colors["step_bg1"],
    fg=theme_colors["text_color"],
)
convert_label.pack(side=tk.LEFT, padx=(0, 10))

convert_c_btn = tk.Button(convert_inner, text="°C", font=("Times", 11), width=4, height=1,
                          bg=theme_colors["compute_bg"], fg=theme_colors["compute_fg"],
                          command=lambda: compute_temperature("C"))
convert_c_btn.pack(side=tk.LEFT, padx=3)

convert_f_btn = tk.Button(convert_inner, text="°F", font=("Times", 11), width=4, height=1,
                          bg=theme_colors["compute_bg"], fg=theme_colors["compute_fg"],
                          command=lambda: compute_temperature("F"))
convert_f_btn.pack(side=tk.LEFT, padx=3)

convert_k_btn = tk.Button(convert_inner, text="K", font=("Times", 11), width=4, height=1,
                          bg=theme_colors["compute_bg"], fg=theme_colors["compute_fg"],
                          command=lambda: compute_temperature("K"))
convert_k_btn.pack(side=tk.LEFT, padx=3)

input_grid = tk.Frame(input_frame, bg=theme_colors["step_bg1"])
input_grid.pack(fill=tk.X, padx=10, pady=(5, 10))

input_grid.grid_columnconfigure(0, weight=1)
input_grid.grid_columnconfigure(1, weight=0)
input_grid.grid_columnconfigure(2, weight=0)
input_grid.grid_columnconfigure(3, weight=1)

c_label = tk.Label(input_grid, text="Enter Celsius:", font=("Times", 12),
                   bg=theme_colors["step_bg1"], fg=theme_colors["text_color"])
c_label.grid(row=0, column=1, sticky="w", padx=(0, 8))
c_entry = tk.Entry(input_grid, width=25, font=("Times", 12))
c_entry.grid(row=0, column=2, pady=(6, 6))

f_label = tk.Label(input_grid, text="Enter Fahrenheit:", font=("Times", 12),
                   bg=theme_colors["step_bg1"], fg=theme_colors["text_color"])
f_label.grid(row=1, column=1, sticky="w", padx=(0, 8))
f_entry = tk.Entry(input_grid, width=25, font=("Times", 12))
f_entry.grid(row=1, column=2, pady=(0, 6))

k_label = tk.Label(input_grid, text="Enter Kelvin:", font=("Times", 12),
                   bg=theme_colors["step_bg1"], fg=theme_colors["text_color"])
k_label.grid(row=2, column=1, sticky="w", padx=(0, 8))
k_entry = tk.Entry(input_grid, width=25, font=("Times", 12))
k_entry.grid(row=2, column=2, pady=(0, 6))

# Keypad section
calculator_frame = tk.Frame(left_content_frame, bg=theme_colors["step_bg1"], relief=tk.GROOVE, bd=1)
calculator_frame.pack(pady=10, padx=5, fill=tk.X)

button_center_frame = tk.Frame(calculator_frame, bg=theme_colors["step_bg1"])
button_center_frame.pack(pady=10, padx=10, fill=tk.X)

for i in range(5):
    button_center_frame.grid_columnconfigure(i, weight=1)

button_width = 4
button_height = 2
button_font = ("Times", 12)

calc_buttons = [
    ["CLR", "DEL", "°"],
    ["7", "8", "9"],
    ["4", "5", "6"],
    ["1", "2", "3"],
    ["±", "0", "."],
]

def resource_path(relative_path):
    """Get absolute path to resource — works for dev and PyInstaller .exe"""
    if hasattr(sys, '_MEIPASS'):
        base = sys._MEIPASS
    else:
        base = os.path.dirname(os.path.abspath(__file__))
    return os.path.join(base, relative_path)

def set_result_text(text: str, color=None):
    ax.clear()
    ax.set_xticks([])
    ax.set_yticks([])
    ax.set_frame_on(False)
    if text:
        ax.text(0.5, 0.5, text, fontsize=16, ha="center", va="center", color=color)
    canvas.draw()

def clear_steps_message():
    for widget in steps_scrollable_frame.winfo_children():
        widget.destroy()

    steps_container = tk.Frame(
        steps_scrollable_frame,
        bg=theme_colors["step_bg1"],
        relief=tk.GROOVE,
        bd=1
    )
    steps_container.pack(fill=tk.X, padx=10, pady=5)

    waiting_label = tk.Label(
        steps_container,
        text="Enter a value in a specific field\nand click a Convert to button\nto see the step-by-step solution",
        font=("Tahoma", 11),
        bg=theme_colors["step_bg1"],
        fg=theme_colors["text_color"],
        height=6,
        justify="center",
        anchor="center",
    )
    waiting_label.pack(fill=tk.X)

def display_steps(source_unit, input_value, target_unit, result_value):
    root.current_step_data = (source_unit, input_value, target_unit, result_value)

    for widget in steps_scrollable_frame.winfo_children():
        widget.destroy()

    steps_container = tk.Frame(
        steps_scrollable_frame,
        bg=theme_colors["step_bg1"],
        relief=tk.GROOVE,
        bd=1
    )
    steps_container.pack(fill=tk.X, padx=10, pady=5, anchor="n")

    titles = [
        "Given Value",
        "Conversion Formula",
        "Substitution",
        "Simplification",
        "Final Answer"
    ]

    steps = step_texts(source_unit, input_value, target_unit, result_value)

    for i, (title, step) in enumerate(zip(titles, steps)):
        step_bg = theme_colors["step_bg1"] if i % 2 == 0 else theme_colors["step_bg2"]

        step_frame = tk.Frame(
            steps_container,
            bg=step_bg,
            padx=14,
            pady=10
        )
        step_frame.pack(fill=tk.X, pady=1)

        title_label = tk.Label(
            step_frame,
            text=f"Step {i + 1}: {title}",
            font=("Courier New", 10, "bold"),
            bg=step_bg,
            fg=theme_colors["text_color"],
        )
        title_label.pack(fill=tk.X, pady=(4, 8))

        inner_box = tk.Frame(
            step_frame,
            bg=theme_colors["frame_bg"],
            bd=1,
            relief=tk.GROOVE
        )
        inner_box.pack(fill=tk.X, padx=0, pady=(0, 8))

        spacer = tk.Frame(inner_box, height=6, bg=step_bg)
        spacer.pack(fill=tk.X)

        fig_step = plt.figure(figsize=(6.8, 1.0), facecolor=theme_colors["frame_bg"])
        ax_step = fig_step.add_subplot(111)
        ax_step.set_facecolor(theme_colors["frame_bg"])
        ax_step.axis("off")

        ax_step.text(
            0.5,
            0.5,
            step,
            fontsize=12,
            ha="center",
            va="center",
            color=theme_colors["text_color"],
        )

        canvas_step = FigureCanvasTkAgg(fig_step, master=inner_box)
        canvas_step.draw()
        canvas_widget = canvas_step.get_tk_widget()
        canvas_widget.config(bg=theme_colors["frame_bg"], highlightthickness=0)
        canvas_widget.pack(fill=tk.X, padx=6, pady=8)

        plt.close(fig_step)

        if i < len(steps) - 1:
            tk.Frame(
                steps_container,
                height=1,
                bg=theme_colors["separator"]
            ).pack(fill=tk.X)

def step_texts(source_unit, input_value, target_unit, result_value):
    n = format_number(input_value)
    r = format_number(result_value)

    if source_unit == "C" and target_unit == "F":
        return [
            f"{n} °C → °F",
            "F = (C × 9/5) + 32",
            f"F = ({n} × 9/5) + 32",
            f"F = {format_number(float(input_value) * 9 / 5)} + 32",
            f"{n} °C = {r} °F",
        ]

    if source_unit == "C" and target_unit == "K":
        return [
            f"{n} °C → K",
            "K = C + 273.15",
            f"K = {n} + 273.15",
            f"K = {format_number(float(input_value) + 273.15)}",
            f"{n} °C = {r} K",
        ]

    if source_unit == "F" and target_unit == "C":
        celsius = (float(input_value) - 32) * 5 / 9
        return [
            f"{n} °F → °C",
            "C = (F - 32) × 5/9",
            f"C = ({n} - 32) × 5/9",
            f"C = {format_number(float(input_value) - 32)} × 5/9",
            f"{n} °F = {r} °C",
        ]

    if source_unit == "F" and target_unit == "K":
        celsius = (float(input_value) - 32) * 5 / 9
        return [
            f"{n} °F → K",
            "K = ((F - 32) × 5/9) + 273.15",
            f"K = (({n} - 32) × 5/9) + 273.15",
            f"K = {format_number(celsius)} + 273.15",
            f"{n} °F = {r} K",
        ]

    if source_unit == "K" and target_unit == "C":
        return [
            f"{n} K → °C",
            "C = K - 273.15",
            f"C = {n} - 273.15",
            f"C = {format_number(float(input_value) - 273.15)}",
            f"{n} K = {r} °C",
        ]

    if source_unit == "K" and target_unit == "F":
        celsius = float(input_value) - 273.15
        return [
            f"{n} K → °F",
            "F = ((K - 273.15) × 9/5) + 32",
            f"F = (({n} - 273.15) × 9/5) + 32",
            f"F = {format_number(celsius)} × 9/5 + 32",
            f"{n} K = {r} °F",
        ]

    return [
        f"Input: {n} {source_unit}",
        "No conversion needed.",
        f"The value is already in {target_unit}.",
        "Solution: same unit",
        f"Final Answer: {r} {target_unit}",
    ]

def format_number(value):
    rounded = round(float(value), 2)
    if abs(rounded - int(rounded)) < 1e-10:
        return str(int(rounded))
    return f"{rounded:.2f}".rstrip("0").rstrip(".")


def parse_temperature(value_text):
    cleaned = value_text.strip().replace("°", "")
    if cleaned in {"", "+", "-", ".", "+.", "-."}:
        raise ValueError
    return float(cleaned)


def convert_temperature(value, source_unit, target_unit):
    if source_unit == target_unit:
        return value
    if source_unit == "C":
        if target_unit == "F":
            return value * 9 / 5 + 32
        if target_unit == "K":
            return value + 273.15
    elif source_unit == "F":
        celsius = (value - 32) * 5 / 9
        if target_unit == "C":
            return celsius
        if target_unit == "K":
            return celsius + 273.15
    elif source_unit == "K":
        celsius = value - 273.15
        if target_unit == "C":
            return celsius
        if target_unit == "F":
            return celsius * 9 / 5 + 32
    raise ValueError("Unsupported conversion")


def display_error(msg):
    set_result_text(msg, color=theme_colors["error_color"])


def find_filled_entry():
    fields = {
        "C": c_entry.get().strip(),
        "F": f_entry.get().strip(),
        "K": k_entry.get().strip(),
    }
    filled = [(unit, text) for unit, text in fields.items() if text]
    return filled


def update_conversion_button_states(*_):
    filled = find_filled_entry()

    if len(filled) != 1:
        for btn in (convert_c_btn, convert_f_btn, convert_k_btn):
            btn.config(state=tk.DISABLED if len(filled) == 0 else tk.DISABLED)
        return

    source_unit, _ = filled[0]
    for unit, btn in (("C", convert_c_btn), ("F", convert_f_btn), ("K", convert_k_btn)):
        btn.config(state=tk.DISABLED if unit == source_unit else tk.NORMAL)


def compute_temperature(target_unit):
    root.selected_target = target_unit

    filled = find_filled_entry()
    if len(filled) == 0:
        display_error("Please enter a temperature value.")
        update_conversion_button_states()
        return
    if len(filled) > 1:
        display_error("Please fill only one input field at a time.")
        update_conversion_button_states()
        return

    source_unit, raw_value = filled[0]

    try:
        value = parse_temperature(raw_value)
        result_value = convert_temperature(value, source_unit, target_unit)
    except Exception:
        display_error("Invalid temperature value.")
        update_conversion_button_states()
        return

    if source_unit == target_unit:
        display_error(f"{source_unit} to {target_unit} is already the same unit.")
        update_conversion_button_states()
        return

    if source_unit == "K":
        left_unit = "K"
    else:
        left_unit = f"°{source_unit}"

    if target_unit == "K":
        right_unit = "K"
    else:
        right_unit = f"°{target_unit}"

    display_text = f"{format_number(value)} {left_unit} = {format_number(result_value)} {right_unit}"
    set_result_text(display_text)
    display_steps(source_unit, value, target_unit, result_value)
    calculation_history.append((source_unit, format_number(value), target_unit, format_number(result_value)))
    update_conversion_button_states()

def clear_entries():
    c_entry.delete(0, tk.END)
    f_entry.delete(0, tk.END)
    k_entry.delete(0, tk.END)
    clear_steps_message()
    root.current_step_data = None
    set_result_text("")
    update_conversion_button_states()


def toggle_sign(entry_widget):
    value = entry_widget.get().strip()
    if not value:
        entry_widget.insert(0, "-")
    elif value.startswith("-"):
        entry_widget.delete(0, 1)
    else:
        entry_widget.delete(0, tk.END)
        entry_widget.insert(0, "-" + value)
    update_conversion_button_states()

def apply_button_theme():
    for btn in all_buttons:
        label = btn.cget("text")

        if label in ("CLR", "DEL"):
            bg = theme_colors["utility_bg"]
            fg = theme_colors["utility_fg"]
        elif label in ("°", "±"):
            bg = theme_colors["operations_bg"]
            fg = theme_colors["text_color"]
        else:
            bg = theme_colors["button_bg"]
            fg = theme_colors["text_color"]

        btn.config(
            bg=bg,
            fg=fg,
            activebackground=bg,
            activeforeground=fg
        )

    for btn in (convert_c_btn, convert_f_btn, convert_k_btn):
        btn.config(
            bg=theme_colors["compute_bg"],
            fg=theme_colors["compute_fg"],
            activebackground=theme_colors["compute_active_bg"],
            activeforeground=theme_colors["compute_fg"],
            disabledforeground=theme_colors["compute_bg"]
        )

    for btn in (info_button, history_button, about_button):
        btn.config(
            bg=theme_colors["operations_bg"],
            fg=theme_colors["text_color"],
            activebackground=theme_colors["operations_bg"],
            activeforeground=theme_colors["text_color"]
        )

def insert_text(value):
    current_widget = root.focus_get()
    if isinstance(current_widget, tk.Entry):
        if value == "CLR":
            clear_entries()
        elif value == "DEL":
            try:
                cursor = current_widget.index(tk.INSERT)
                if cursor > 0:
                    current_widget.delete(cursor - 1, cursor)
            except Exception:
                pass
            update_conversion_button_states()
        elif value == "±":
            toggle_sign(current_widget)
        else:
            current_widget.insert(tk.INSERT, value)
            update_conversion_button_states()


for row_idx, row in enumerate(calc_buttons):
    for col_idx, symbol in enumerate(row):
        if symbol in ["CLR", "DEL"]:
            bg_color = theme_colors["utility_bg"]
        elif symbol in ["°", "±"]:
            bg_color = theme_colors["operations_bg"]
        else:
            bg_color = theme_colors["button_bg"]

        btn = tk.Button(
            button_center_frame,
            text=symbol,
            font=button_font,
            width=button_width,
            height=button_height,
            bg=bg_color,
            fg=theme_colors["text_color"],
            command=lambda s=symbol: insert_text(s),
        )
        btn.grid(row=row_idx, column=col_idx + 1, padx=5, pady=5, sticky="nsew")
        all_buttons.append(btn)


# About panel
MEMBERS = [
    ("A.png", "Gwyneth T.\nAbrenica"),
    ("DR.jpg", "Angelica T.\nDela Rosa"),
    ("M.jpg", "Lyrish Ann P.\nMalabad"),
    ("O.jpg", "Jhon Mark A.\nObosa"),
]

def load_member_photo(filename, size=(90, 90)):
    path = resource_path(os.path.join("pics", filename))

    if not os.path.isfile(path):
        print("Missing image:", path)
        return None

    try:
        img = Image.open(path).convert("RGB")
        img = img.resize(size, Image.LANCZOS)
        return ImageTk.PhotoImage(img)
    except Exception as e:
        print(f"Error loading {path}: {e}")
        return None

def show_about_panel(content_frame):
    """Populate the sidenav content frame with About information."""
    # Keep PhotoImage references alive so they aren't garbage-collected
    photo_refs = []

    # Title block
    title_lbl = tk.Label(
        content_frame,
        text="🌡️ Temperature Conversion Calculator",
        font=("Verdana Bold", 13, "bold"),
        bg=theme_colors["step_bg1"],
        fg=theme_colors["text_color"],
        wraplength=380,
        justify="center",
    )
    title_lbl.pack(pady=(12, 2), padx=10)

    course_lbl = tk.Label(
        content_frame,
        text="Computational Physics  •  COPH311",
        font=("Helvetica", 11, "italic"),
        bg=theme_colors["step_bg1"],
        fg=theme_colors["text_color"],
    )
    course_lbl.pack(pady=(0, 2))

    section_lbl = tk.Label(
        content_frame,
        text="BSCS 3Y2-1",
        font=("Helvetica", 11, "bold"),
        bg=theme_colors["step_bg1"],
        fg=theme_colors["text_color"],
    )
    section_lbl.pack(pady=(0, 10))

    tk.Frame(content_frame, height=1, bg=theme_colors["separator"]).pack(fill=tk.X, padx=10, pady=(0, 10))

    # Members label
    members_lbl = tk.Label(
        content_frame,
        text="Group Members",
        font=("Courier New", 12, "bold"),
        bg=theme_colors["step_bg1"],
        fg=theme_colors["text_color"],
    )
    members_lbl.pack(pady=(0, 8))

    # Member cards
    grid_frame = tk.Frame(content_frame, bg=theme_colors["step_bg1"])
    grid_frame.pack(padx=10, pady=(0, 12), fill=tk.X)

    grid_frame.grid_columnconfigure(0, weight=1)
    grid_frame.grid_columnconfigure(1, weight=1)

    for idx, (filename, name) in enumerate(MEMBERS):
        row, col = divmod(idx, 2)

        card = tk.Frame(
            grid_frame,
            bg=theme_colors["frame_bg"],
            bd=1,
            relief=tk.GROOVE,
            padx=8,
            pady=8,
        )
        card.grid(row=row, column=col, padx=8, pady=8, sticky="nsew")

        photo = load_member_photo(filename, size=(90, 90))

        if photo:
            photo_refs.append(photo)
            img_lbl = tk.Label(card, image=photo, bg=theme_colors["frame_bg"])
            img_lbl.image = photo
            img_lbl.pack(pady=(0, 4))
        else:
            # Placeholder when the image file is missing
            placeholder = tk.Label(
                card,
                text="📷",
                font=("Helvetica", 30),
                bg=theme_colors["frame_bg"],
                fg=theme_colors["text_color"],
                width=5,
                height=2,
            )
            placeholder.pack()

        name_lbl = tk.Label(
            card,
            text=name,
            font=("Helvetica", 10, "bold"),
            bg=theme_colors["frame_bg"],
            fg=theme_colors["text_color"],
            wraplength=120,
            justify="center",
        )
        name_lbl.pack(pady=(6, 0))

    content_frame._photo_refs = photo_refs


# History and info side panel

def toggle_sidenav(content_type):
    global sidenav_visible, current_sidenav_content

    for widget in sidenav_frame.winfo_children():
        widget.destroy()

    if not sidenav_visible:
        sidenav_frame.grid(row=0, column=0, sticky="nsew")
        sidenav_visible = True

    current_sidenav_content = content_type

    header_bg = theme_colors["sidenav_header_bg"]
    header = tk.Frame(sidenav_frame, bg=header_bg, height=50)
    header.pack(fill=tk.X)

    title_map = {
        "info": "Calculation Information",
        "history": "Calculation History",
        "about": "About",
    }
    title_text = title_map.get(content_type, "")
    title = tk.Label(header, text=title_text, font=("Tahoma Bold", 15, "bold"),
                     bg=header_bg, fg=theme_colors["text_color"])
    title.pack(side=tk.LEFT, padx=15, pady=10)

    content_frame = tk.Frame(sidenav_frame, bg=theme_colors["sidenav_bg"], padx=15, pady=15)
    content_frame.pack(fill=tk.BOTH, expand=True)
    content_container = tk.Frame(content_frame, bg=theme_colors["step_bg1"], bd=1, relief=tk.SUNKEN)
    content_container.pack(fill=tk.BOTH, expand=True)

    if content_type == "info":
        info_text = tk.Text(
            content_container,
            wrap=tk.WORD,
            bg=theme_colors["step_bg1"],
            font=("Segoe UI", 11),
            padx=10,
            pady=10,
            fg=theme_colors["text_color"],
            width=1,
        )
        info_text.pack(fill=tk.BOTH, expand=True)
        info_body = """
                🌡️TEMPERATURE CALCULATOR

A simple converter for switching between Celsius, Fahrenheit, and Kelvin.

FEATURES
1. Enter one value at a time in only one field.
2. Use the Convert to buttons to pick the target scale.
3. See the final answer in the result area and the step-by-step solution on the right.
4. The History button saves previous conversions.

SUPPORTED CONVERSIONS
→ Celsius to Fahrenheit
→ Celsius to Kelvin
→ Fahrenheit to Celsius
→ Fahrenheit to Kelvin
→ Kelvin to Celsius
→ Kelvin to Fahrenheit

USAGE TIPS
1. Type only one temperature value in one field.
2. Click the matching Convert to button.
3. Use the ° button for temperature formatting if needed.
4. The ± button helps toggle the sign of the active input.

LIMITATIONS
1. This calculator expects numeric input only.
2. Do not fill multiple fields at the same time.
3. Non-numeric text will return an error.
"""
        info_text.insert(tk.END, info_body)
        info_text.config(state=tk.DISABLED)

        info_text.tag_config("header", foreground=theme_colors["highlight_terms"],
                             font=("Segoe UI Black", 12))
        for term in ["TEMPERATURE CALCULATOR", "FEATURES", "SUPPORTED CONVERSIONS",
                     "USAGE TIPS", "LIMITATIONS"]:
            start = "1.0"
            while True:
                start = info_text.search(term, start, stopindex=tk.END, nocase=True)
                if not start:
                    break
                end = f"{start}+{len(term)}c"
                info_text.tag_add("header", start, end)
                start = end

    elif content_type == "history":
        if not calculation_history:
            no_history = tk.Label(
                content_container,
                text="No conversions in history yet.",
                font=("Helvetica", 12, "italic"),
                bg=theme_colors["step_bg1"],
                fg=theme_colors["text_color"],
            )
            no_history.pack(pady=20)
        else:
            history_frame = tk.Frame(content_container, bg=theme_colors["step_bg1"], padx=10, pady=10)
            history_frame.pack(fill=tk.BOTH, expand=True)

            scrollbar = tk.Scrollbar(history_frame)
            scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

            history_list = tk.Listbox(
                history_frame,
                bg=theme_colors["step_bg1"],
                font=("Helvetica", 12),
                bd=0,
                relief=tk.FLAT,
                fg=theme_colors["text_color"],
                highlightthickness=0,
            )
            history_list.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

            scrollbar.config(command=history_list.yview)
            history_list.config(yscrollcommand=scrollbar.set)

            for i, (source_unit, value_text, target_unit, result_text) in enumerate(calculation_history):
                suffix = "K" if target_unit == "K" else f"°{target_unit}"
                history_list.insert(tk.END, f"{i + 1}. {value_text} °{source_unit} → {result_text} {suffix}")

            def load_selected():
                selected = history_list.curselection()
                if not selected:
                    return
                idx = selected[0]
                source_unit, value_text, target_unit, _ = calculation_history[idx]
                clear_entries()
                if source_unit == "C":
                    c_entry.insert(0, value_text)
                elif source_unit == "F":
                    f_entry.insert(0, value_text)
                else:
                    k_entry.insert(0, value_text)
                update_conversion_button_states()
                compute_temperature(target_unit)

            button_frame = tk.Frame(content_frame, bg=theme_colors["sidenav_bg"])
            button_frame.pack(pady=10)

            load_button = tk.Button(
                button_frame,
                text="Load Selected",
                font=("Helvetica", 12),
                bg=theme_colors["compute_bg"],
                fg=theme_colors["compute_fg"],
                command=load_selected,
            )
            load_button.pack(side=tk.LEFT, padx=5)

    elif content_type == "about":
        show_about_panel(content_container)


def update_theme_specific_widgets():
    calculator_title.config(bg=theme_colors["frame_bg"], fg=theme_colors["text_color"])
    steps_label.config(bg=theme_colors["frame_bg"], fg=theme_colors["text_color"])
    theme_label.config(bg=theme_colors["frame_bg"], fg=theme_colors["text_color"])
    info_button.config(bg=theme_colors["operations_bg"], fg=theme_colors["text_color"])
    history_button.config(bg=theme_colors["operations_bg"], fg=theme_colors["text_color"])
    about_button.config(bg=theme_colors["operations_bg"], fg=theme_colors["text_color"])
    convert_c_btn.config(bg=theme_colors["compute_bg"], fg=theme_colors["compute_fg"],
                         activebackground=theme_colors["compute_active_bg"],
                         activeforeground=theme_colors["compute_fg"])
    convert_f_btn.config(bg=theme_colors["compute_bg"], fg=theme_colors["compute_fg"],
                         activebackground=theme_colors["compute_active_bg"],
                         activeforeground=theme_colors["compute_fg"])
    convert_k_btn.config(bg=theme_colors["compute_bg"], fg=theme_colors["compute_fg"],
                         activebackground=theme_colors["compute_active_bg"],
                         activeforeground=theme_colors["compute_fg"])

CURSOR_FILES = {
    "Light": "cursors/snowflake.cur",
    "Dark":  "cursors/butterfly.cur",
    "Pink":  "cursors/sakura.cur",
    "Orange": "cursors/maple_leaf.cur"
}

def apply_cursor(theme_name):
    cur_rel = CURSOR_FILES.get(theme_name)
    if not cur_rel:
        return

    cur_path = resource_path(cur_rel)

    if not os.path.isfile(cur_path):
        print(f"Cursor file not found: {cur_path}")
        return

    try:
        tmp_dir = "C:/Temp"
        os.makedirs(tmp_dir, exist_ok=True)
        tmp_cursor = os.path.join(tmp_dir, f"cursor_{theme_name}.cur").replace("\\", "/")
        shutil.copy2(cur_path, tmp_cursor)

        cursor_str = f"@{tmp_cursor}"
        root.config(cursor=cursor_str)
    except tk.TclError as e:
        print(f"Cursor load failed: {e}")
    except Exception as e:
        print(f"Unexpected error: {e}")

def change_theme(theme_name):
    global current_theme, theme_colors
    current_theme = theme_name
    theme_colors = COLOR_THEMES[theme_name]

    root.config(bg=theme_colors["main_bg"])
    main_container.config(bg=theme_colors["main_bg"])
    separator.config(bg=theme_colors["separator"])
    sidenav_frame.config(bg=theme_colors["sidenav_bg"])
    left_frame.config(bg=theme_colors["frame_bg"])
    right_frame.config(bg=theme_colors["frame_bg"])
    left_content_frame.config(bg=theme_colors["frame_bg"])
    right_content_frame.config(bg=theme_colors["frame_bg"])
    header_frame.config(bg=theme_colors["frame_bg"])
    controls_frame.config(bg=theme_colors["frame_bg"])
    left_buttons_frame.config(bg=theme_colors["frame_bg"])
    right_theme_frame.config(bg=theme_colors["frame_bg"])

    calculator_title.config(bg=theme_colors["frame_bg"], fg=theme_colors["text_color"])
    steps_header_frame.config(bg=theme_colors["frame_bg"])
    steps_label.config(bg=theme_colors["frame_bg"], fg=theme_colors["text_color"])
    theme_label.config(bg=theme_colors["frame_bg"], fg=theme_colors["text_color"])

    steps_scrollable_frame.config(bg=theme_colors["frame_bg"])
    steps_canvas.config(bg=theme_colors["frame_bg"])
    _steps_outer.config(bg=theme_colors["frame_bg"])
    input_frame.config(bg=theme_colors["step_bg1"])
    convert_strip.config(bg=theme_colors["step_bg1"])
    convert_inner.config(bg=theme_colors["step_bg1"])
    input_grid.config(bg=theme_colors["step_bg1"])
    calculator_frame.config(bg=theme_colors["step_bg1"])
    button_center_frame.config(bg=theme_colors["step_bg1"])

    c_label.config(bg=theme_colors["step_bg1"], fg=theme_colors["text_color"])
    f_label.config(bg=theme_colors["step_bg1"], fg=theme_colors["text_color"])
    k_label.config(bg=theme_colors["step_bg1"], fg=theme_colors["text_color"])
    convert_label.config(bg=theme_colors["step_bg1"], fg=theme_colors["text_color"])
    convert_inner.config(bg=theme_colors["step_bg1"])
    apply_button_theme()
    set_result_text("")

    if current_sidenav_content:
        toggle_sidenav(current_sidenav_content)

    if root.current_step_data:
        display_steps(*root.current_step_data)
    else:
        clear_steps_message()

    update_conversion_button_states()
    apply_cursor(theme_name)

# ─── Nav buttons (About / Info / History) ─────────────────────────────────────

about_button = tk.Button(
    left_buttons_frame,
    text="👥 About",
    font=("Georgia", 11),
    bg=theme_colors["operations_bg"],
    fg=theme_colors["text_color"],
    width=7,
    height=1,
    borderwidth=1,
    relief=tk.RAISED,
    command=lambda: toggle_sidenav("about"),
)
about_button.pack(side=tk.LEFT, padx=3, pady=3)

info_button = tk.Button(
    left_buttons_frame,
    text="ⓘ Info",
    font=("Georgia", 11),
    bg=theme_colors["operations_bg"],
    fg=theme_colors["text_color"],
    width=7,
    height=1,
    borderwidth=1,
    relief=tk.RAISED,
    command=lambda: toggle_sidenav("info"),
)
info_button.pack(side=tk.LEFT, padx=3, pady=3)

history_button = tk.Button(
    left_buttons_frame,
    text="⟳ History",
    font=("Georgia", 11),
    bg=theme_colors["operations_bg"],
    fg=theme_colors["text_color"],
    width=7,
    height=1,
    borderwidth=1,
    relief=tk.RAISED,
    command=lambda: toggle_sidenav("history"),
)
history_button.pack(side=tk.LEFT, padx=3, pady=3)

theme_menu.bind("<<ComboboxSelected>>", lambda event: change_theme(theme_var.get()))

for entry in (c_entry, f_entry, k_entry):
    entry.bind("<KeyRelease>", update_conversion_button_states)
    entry.bind("<FocusIn>", update_conversion_button_states)

# Initial display
clear_steps_message()
set_result_text("")
update_conversion_button_states()
change_theme("Light")

root.bind("<Return>", lambda event: compute_temperature(root.selected_target) if root.selected_target else None)
root.mainloop()