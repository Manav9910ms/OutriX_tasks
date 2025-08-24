import os
import shutil
import tkinter as tk
from tkinter import filedialog, messagebox, ttk

# CATEGORY MAPPING
CATEGORIES = {
    "Documents": [".docx", ".pdf", ".txt", ".xlsx", ".pptx"],
    "Images": [".jpg", ".jpeg", ".png", ".gif"],
    "Videos": [".mp4", ".mov", ".avi"],
    "Others": []
}

def preview_files(folder):
    preview_data = {}
    for category, extensions in CATEGORIES.items():
        matches = [
            f for f in os.listdir(folder)
            if os.path.isfile(os.path.join(folder, f)) and
               (os.path.splitext(f)[1].lower() in extensions or
               (category == "Others" and os.path.splitext(f)[1].lower() not in sum(CATEGORIES.values(), [])))
        ]
        preview_data[category] = matches
    return preview_data

def organize(folder, selected_categories):
    total_files = sum(len(files) for cat, files in preview_files(folder).items() if cat in selected_categories)
    moved_count = 0
    for cat, extensions in CATEGORIES.items():
        if cat not in selected_categories:
            continue
        dest_folder = os.path.join(folder, cat)
        os.makedirs(dest_folder, exist_ok=True)
        for file in os.listdir(folder):
            file_path = os.path.join(folder, file)
            if os.path.isfile(file_path) and (
                os.path.splitext(file)[1].lower() in extensions or
                (cat == "Others" and os.path.splitext(file)[1].lower() not in sum(CATEGORIES.values(), []))
            ):
                shutil.move(file_path, os.path.join(dest_folder, file))
                moved_count += 1
                progress_var.set(int((moved_count / total_files) * 100))
                root.update_idletasks()

def browse_folder():
    folder_selected = filedialog.askdirectory()
    if folder_selected:
        folder_path.set(folder_selected)
        update_preview()

def update_preview():
    folder = folder_path.get()
    if not os.path.exists(folder):
        return
    data = preview_files(folder)
    for widget in preview_frame.winfo_children():
        widget.destroy()
    for cat, files in data.items():
        var = tk.BooleanVar(value=True)
        category_vars[cat] = var
        tk.Checkbutton(preview_frame, text=f"{cat} ({len(files)} files)",
                       variable=var, bg="#F8F9FA", anchor="w", font=("Segoe UI", 10)).pack(fill="x", pady=2)

def start_organizing():
    folder = folder_path.get()
    if not os.path.exists(folder):
        messagebox.showerror("Error", "Folder does not exist.")
        return
    selected = [cat for cat, var in category_vars.items() if var.get()]
    if not selected:
        messagebox.showwarning("No Selection", "Please select at least one category.")
        return
    if messagebox.askyesno("Confirm", f"Organize selected categories in:\n{folder}?"):
        organize(folder, selected)
        messagebox.showinfo("Done", "Organizing complete!")
        update_preview()

# GUI Setup
root = tk.Tk()
root.title("File Organizer Pro")
root.geometry("480x420")
root.configure(bg="#F8F9FA")

folder_path = tk.StringVar()
category_vars = {}
progress_var = tk.IntVar()

# Folder selection
tk.Label(root, text="Folder to Organize", font=("Segoe UI", 11, "bold"), bg="#F8F9FA").pack(pady=6)
tk.Entry(root, textvariable=folder_path, width=42, font=("Segoe UI", 10), relief="solid", bd=1).pack()
tk.Button(root, text="Browse", command=browse_folder, bg="#0078D4", fg="white",
          font=("Segoe UI", 10, "bold"), relief="flat").pack(pady=6)

# Preview section
preview_frame = tk.Frame(root, bg="#F8F9FA")
preview_frame.pack(fill="both", expand=True, pady=10)

# Progress bar
progress_bar = ttk.Progressbar(root, variable=progress_var, maximum=100)
progress_bar.pack(fill="x", padx=10, pady=8)

# Action button
tk.Button(root, text="Start Organizing", bg="#28A745", fg="white",
          font=("Segoe UI", 11, "bold"), relief="flat",
          command=start_organizing).pack(pady=10)

root.mainloop()