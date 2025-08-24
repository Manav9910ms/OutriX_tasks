import tkinter as tk

root = tk.Tk()
root.title("Interactive Calculator")
root.geometry("360x500")
root.configure(bg="#f0f0f0")

expr = tk.StringVar()

# Current theme colors
theme = {
    "bg": "#f0f0f0",
    "btn_bg": "#e0e0e0",
    "btn_fg": "#333333",
    "display_bg": "#ffffff",
    "display_fg": "#333333"
}

# ---------------- FUNCTIONS ----------------
def apply_theme():
    root.configure(bg=theme["bg"])
    display.config(bg=theme["display_bg"], fg=theme["display_fg"])
    for b in buttons:
        b.config(bg=theme["btn_bg"], fg=theme["btn_fg"])
    btn_clear.config(bg="#ff6666", fg="#ffffff", activebackground="#ff4c4c")
    theme_btn.config(bg=theme["btn_bg"], fg=theme["btn_fg"])

def toggle_theme():
    if theme["bg"] == "#f0f0f0":  # switch to dark
        theme.update({
            "bg": "#222222", "btn_bg": "#444444", "btn_fg": "#ffffff",
            "display_bg": "#333333", "display_fg": "#ffffff"
        })
    else:  # back to light
        theme.update({
            "bg": "#f0f0f0", "btn_bg": "#e0e0e0", "btn_fg": "#333333",
            "display_bg": "#ffffff", "display_fg": "#333333"
        })
    apply_theme()

def flash(btn):
    orig = btn.cget("bg")
    btn.config(bg="#b0b0b0")
    btn.after(100, lambda: btn.config(bg=orig))

def shake():
    x, y = root.winfo_x(), root.winfo_y()
    for offset in (-10, 10, -6, 6, -2, 2, 0):
        root.geometry(f"+{x + offset}+{y}")
        root.update()
        root.after(30)

def on_click(key, btn=None):
    if btn: flash(btn)
    if key == "=":
        try:
            expr.set(str(eval(expr.get())))
        except:
            expr.set("Error")
            shake()
    elif key == "C":
        expr.set("")
    elif key == "⌫":
        expr.set(expr.get()[:-1])
    else:
        expr.set(expr.get() + key)

# ---------------- UI ----------------
display = tk.Entry(root, textvariable=expr, font=("Segoe UI", 24),
                   bd=0, justify="right", bg=theme["display_bg"], fg=theme["display_fg"])
display.pack(fill="x", padx=16, pady=(16, 8))

buttons = []
def make_button(text, row, col):
    btn = tk.Button(root, text=text, font=("Segoe UI", 18),
                    bg=theme["btn_bg"], fg=theme["btn_fg"],
                    bd=0, relief="flat", activebackground="#d0d0d0",
                    command=lambda t=text, b=None: on_click(t, b))
    btn.place(relx=col*0.25, rely=0.2+row*0.16, relwidth=0.25, relheight=0.16)
    btn.config(command=lambda t=text, b=btn: on_click(t, b))
    buttons.append(btn)
    return btn

labels = [
    ('7',0,0),('8',0,1),('9',0,2),('/',0,3),
    ('4',1,0),('5',1,1),('6',1,2),('*',1,3),
    ('1',2,0),('2',2,1),('3',2,2),('-',2,3),
    ('0',3,0),('.',3,1),('=',3,2),('+',3,3),
]
for txt, r, c in labels:
    make_button(txt, r, c)

# Clear and backspace row
btn_clear = tk.Button(root, text="C", font=("Segoe UI", 18),
                      bg="#ff6666", fg="#ffffff", bd=0, relief="flat",
                      activebackground="#ff4c4c",
                      command=lambda: on_click("C"))
btn_clear.place(relx=0, rely=0.84, relwidth=0.5, relheight=0.16)

make_button("⌫", 4, 2)  # Backspace button position

# Theme toggle button
theme_btn = tk.Button(root, text=" Theme", font=("Segoe UI", 14),
                      command=toggle_theme, bd=0, relief="flat",
                      bg=theme["btn_bg"], fg=theme["btn_fg"])
theme_btn.place(relx=0.5, rely=0.84, relwidth=0.5, relheight=0.16)

apply_theme()
root.mainloop()